#!/usr/bin/env python3
"""Sign an unsigned Android release using one private GitHub Actions secret."""
import base64, json, os, pathlib, subprocess, tempfile

bundle=os.environ.get('PING_TEST_SIGNING_BUNDLE','').strip()
if not bundle:
    raise SystemExit('::error::Missing Actions secret PING_TEST_SIGNING_BUNDLE')
# Support direct Base64 text, copied quoted Base64, KEY=... lines,
# wrapped Base64, or the decoded JSON. Never log key contents.
import re
if bundle.startswith('PING_TEST_SIGNING_BUNDLE='):
    bundle=bundle.split('=',1)[1].strip()
bundle=bundle.strip('\\ufeff').strip().strip('"').strip("'")
try:
    if bundle.startswith('{'):
        config=json.loads(bundle)
    else:
        compact=re.sub(r'\\s+','',bundle)
        config=json.loads(base64.b64decode(compact,validate=True).decode('utf-8'))
    key=base64.b64decode(config['keystoreBase64'],validate=True)
    required=('storePassword','keyPassword','keyAlias','certSha256')
    if any(not config.get(name) for name in required) or len(key)<500:
        raise ValueError('Incomplete bundle')
except (ValueError,KeyError,UnicodeError,TypeError) as error:
    raise SystemExit('::error::Signing secret is not a complete Base64 JSON bundle. Copy the entire single-line value from PING_TEST_SIGNING_BUNDLE_PRIVATE.txt. No leading or trailing explanation.')
except Exception:
    raise SystemExit('::error::Signing secret could not be decoded. Verify PING_TEST_SIGNING_BUNDLE in repository Actions Secrets.')
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
