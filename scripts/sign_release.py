#!/usr/bin/env python3
"""Sign an unsigned Android release using one private GitHub Actions secret."""
import base64, json, os, pathlib, subprocess, tempfile

bundle=os.environ.get('PING_TEST_SIGNING_BUNDLE','').strip()
if not bundle:
    raise SystemExit('::error::Signing secret is missing')
import io
import zipfile

def read_bundle(value):
    value=value.lstrip(chr(65279)).strip()
    if value.startswith('PING_TEST_SIGNING_BUNDLE='):
        value=value.split('=',1)[1].strip()
    value=value.strip().strip('"').strip("'")
    if value.startswith('{'):
        obj=json.loads(value)
        raw=None
    else:
        raw=base64.b64decode(''.join(value.split()),validate=True)
        if raw[:2]==b'PK':
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                meta=json.loads(archive.read('signing.json'))
                candidates=[name for name in archive.namelist() if name.endswith('.p12') or name.endswith('.pfx')]
                if len(candidates)!=1: raise ValueError('Ambiguous PKCS12 file')
                private=archive.read(candidates[0])
            obj={'keystoreBase64':base64.b64encode(private).decode('ascii'),
                 'storePassword':meta['keystore_password'],
                 'keyPassword':meta['key_password'],
                 'keyAlias':meta['alias'],
                 'certSha256':meta['certificate_sha256']}
        else:
            obj=json.loads(raw.decode('utf-8'))
    private=base64.b64decode(''.join(obj['keystoreBase64'].split()),validate=True)
    needed=('storePassword','keyPassword','keyAlias','certSha256')
    if len(private)<500 or not all(obj.get(n) for n in needed):
        raise ValueError('Missing keystore or metadata')
    return obj,private

try:
    config,key=read_bundle(bundle)
except Exception:
    raise SystemExit('::error::Signing secret format is not recognized as a PING TEST Base64 JSON or QR LINK ZIP bundle')
root=pathlib.Path(os.environ['ANDROID_SDK_ROOT'])/'build-tools'/'35.0.0'
if not root.exists():root=pathlib.Path(os.environ['ANDROID_SDK_ROOT'])/'build-tools'/'36.0.0'
unsigned=pathlib.Path('app/build/outputs/apk/release/app-release-unsigned.apk')
if not unsigned.is_file():raise SystemExit('::error::Unsigned release APK not found')
dist=pathlib.Path('dist');dist.mkdir(exist_ok=True)
aligned=dist/'aligned.apk';signed=dist/'PING-TEST.apk'
with tempfile.TemporaryDirectory(prefix='ping-sign-') as folder:
    keystore=pathlib.Path(folder)/'release.p12'
    keystore.write_bytes(key)
    subprocess.run([str(root/'zipalign'),'-f','-p','4',str(unsigned),str(aligned)],check=True)
    env=os.environ.copy()
    env['KEYSTORE_PASS']=config['storePassword'];env['KEY_PASS']=config['keyPassword']
    subprocess.run([str(root/'apksigner'),'sign','--ks',str(keystore),'--ks-type','PKCS12',
        '--ks-key-alias',config['keyAlias'],'--ks-pass','env:KEYSTORE_PASS',
        '--key-pass','env:KEY_PASS','--out',str(signed),str(aligned)],env=env,check=True)
    verify=subprocess.run([str(root/'apksigner'),'verify','--verbose','--print-certs',str(signed)],capture_output=True,text=True,check=True)
    wanted=config['certSha256'].replace(':','').upper()
    if wanted not in verify.stdout.replace(':','').upper():
        signed.unlink(missing_ok=True)
        raise SystemExit('::error::Signing certificate mismatch')
    if wanted!='C17E87ED0E0EB7E9D96CE71F91804AE8A0F8BCAD5065C464342E2FA5F4026802':
        raise SystemExit('::error::Certificate does not match pinned application identity')
aligned.unlink(missing_ok=True)
print('Successfully signed dist/PING-TEST.apk with pinned release certificate')
