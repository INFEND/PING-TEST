#!/usr/bin/env python3
"""Sign an unsigned Android release using one private GitHub Actions secret."""
import base64, binascii, io, json, os, pathlib, re, subprocess, sys, tempfile, zipfile

# Read the existing Actions secret without ever logging the secret itself.
PINNED_CERT='C17E87ED0E0EB7E9D96CE71F91804AE8A0F8BCAD5065C464342E2FA5F4026802'
bundle=os.environ.get('PING_TEST_SIGNING_BUNDLE','')
if not bundle.strip():
    raise SystemExit('::error::Signing secret is missing')

def read_bundle(value):
    value=value.lstrip(chr(65279)).strip()
    for invisible in (chr(8203),chr(8204),chr(8205),chr(8288)):
        value=value.replace(invisible,'')
    if 'PING_TEST_SIGNING_BUNDLE=' in value:
        value=value.split('PING_TEST_SIGNING_BUNDLE=',1)[1].strip()
    value=value.strip(' \\t\\r\\n\`\\\"\\\'')
    candidates=[value]
    compact=''.join(value.split())
    if compact!=value:
        candidates.append(compact)
    # Accept a complete Base64 bundle even if the clipboard added a
    # code fence, a field label, or prose around the value.
    candidates.extend(re.findall(r'[A-Za-z0-9+/_-]{512,}={0,2}',value))
    tried=set()
    for encoded in candidates:
        if encoded in tried:
            continue
        tried.add(encoded)
        try:
            if encoded.startswith('{'):
                config=json.loads(encoded)
            else:
                encoded=encoded.strip(' \`\\\"\\\'')
                encoded+='='*((-len(encoded))%4)
                raw=base64.b64decode(encoded,altchars=b'-_',validate=True)
                if raw.startswith(b'PK'):
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        meta=json.loads(archive.read('signing.json'))
                        names=[n for n in archive.namelist() if n.lower().endswith(('.p12','.pfx'))]
                        if len(names)!=1:
                            raise ValueError('Ambiguous PKCS12')
                        key=archive.read(names[0])
                    config={'keystoreBase64':base64.b64encode(key).decode('ascii'),
                            'storePassword':meta['keystore_password'],
                            'keyPassword':meta['key_password'],
                            'keyAlias':meta['alias'],
                            'certSha256':meta['certificate_sha256']}
                else:
                    config=json.loads(raw.decode('utf-8'))
            required=('keystoreBase64','storePassword','keyPassword','keyAlias','certSha256')
            if not isinstance(config,dict) or any(
                    not isinstance(config.get(field),str) or not config[field] for field in required):
                continue
            key=base64.b64decode(''.join(config['keystoreBase64'].split()),validate=True)
            if len(key)<500:
                continue
            if config['certSha256'].replace(':','').upper()!=PINNED_CERT:
                continue
            return config,key
        except (ValueError,KeyError,TypeError,UnicodeError,OSError,
                zipfile.BadZipFile,binascii.Error):
            continue
    raise ValueError('Signing secret cannot be decoded to the expected verified PKCS12 bundle')

try:
    config,key=read_bundle(bundle)
except Exception:
    # Number of characters is metadata, never the value or a fingerprint.
    # Distinguish truncated clipboard content from a bad decoder without
    # exposing passwords, Base64, hashes, or private bytes.
    count=len(bundle)
    length_kind='very-short' if count<4000 else ('unexpected-size' if count>12000 else 'normal-size')
    raise SystemExit('::error::Invalid Actions signing bundle ('+length_kind+
                     ', character-count='+str(count)+
                     '). Exact source bundle is valid; verify that this is the complete Secret value.')
if '--preflight' in sys.argv:
    print('Signing bundle recognized, complete and pinned to PING TEST certificate.')
    sys.exit(0)
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
