#!/usr/bin/env python3
import hashlib,json,os,pathlib,re,subprocess,sys
apk=pathlib.Path('dist/PING-TEST.apk')
if not apk.is_file():sys.exit('Signed APK not found')
text=pathlib.Path('app/build.gradle').read_text()
version=re.search(r"versionName\s+['\"]([^'\"]+)",text).group(1)
code=int(re.search(r'versionCode\s+(\d+)',text).group(1))
assert re.fullmatch(r'\d+\.\d+\.\d+',version)
assert code>0
path='release_notes/v'+version+'.txt'
notes=pathlib.Path(path).read_text().strip() if pathlib.Path(path).is_file() else f'PING TEST {version}: исправления и поддержка обновлений через GitHub.'
assert len(notes)<=5000
repo=os.environ.get('GITHUB_REPOSITORY','INFEND/PING-TEST')
if repo!='INFEND/PING-TEST':sys.exit('Refusing nonofficial repository')
data={'schema':1,'packageName':'com.xarkon.pingtest','versionCode':code,
      'versionName':version,'apkUrl':f'https://github.com/{repo}/releases/download/v{version}/PING-TEST.apk',
      'sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'sizeBytes':apk.stat().st_size,'notes':notes}
pathlib.Path('dist/update.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(data,ensure_ascii=False,indent=2))
with open(os.environ['GITHUB_OUTPUT'],'a') as stream:
    stream.write(f'tag=v{version}\nversion={version}\n')
