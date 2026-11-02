#!/usr/bin/env python3
"""Produce QR LINK-compatible cumulative OTA metadata from the signed APK."""
import hashlib, json, os, pathlib, re, subprocess, sys
from datetime import datetime, timezone

repo=os.environ.get("GITHUB_REPOSITORY","")
if repo!="INFEND/PING-TEST":sys.exit("Refusing nonofficial OTA repository")
apk=pathlib.Path("dist/PING-TEST.apk")
if not apk.is_file():sys.exit("Signed APK not found")
sdk=pathlib.Path(os.environ.get("ANDROID_SDK_ROOT",""))
aapt=sdk/"build-tools"/"35.0.0"/"aapt"
if not aapt.is_file():sys.exit("Android aapt build-tool unavailable")
details=subprocess.check_output([str(aapt),"dump","badging",str(apk)],text=True)
match=re.search(r"^package: name='([^']+)' versionCode='([0-9]+)' versionName='([^']+)'",details,re.M)
if not match:sys.exit("Unable to read APK metadata")
package, code_str, version=match.groups()
code=int(code_str)
if package!="com.xarkon.pingtest" or not re.fullmatch(r"[0-9]+\\.[0-9]+\\.[0-9]+",version):
    sys.exit("Invalid APK identity or version")
index=json.loads(pathlib.Path("release_notes/versions.json").read_text(encoding="utf-8"))
if index.get(version)!=code:sys.exit("Version code must be indexed in release_notes/versions.json")
history=[]
for name,version_code in sorted(index.items(),key=lambda pair:pair[1]):
    if version_code>code:continue
    path=pathlib.Path("release_notes")/f"v{name}.txt"
    if not path.exists():sys.exit("Missing release notes for "+name)
    visible=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if line.startswith(("[+] ","[-] ","[=] ","[–] ")):
            visible.append(line)
        elif line.startswith("• "):
            visible.append("[+] "+line[2:])
    if not visible:sys.exit("No visible changes for "+name)
    notes="\\n".join(visible)
    history.append({"versionCode":version_code,"versionName":name,"notes":notes})
if not history or history[-1]["versionCode"]!=code:
    sys.exit("Cumulative history does not reach current version")
if any(b["versionCode"]!=a["versionCode"]+1 for a,b in zip(history,history[1:])):
    sys.exit("OTA versionCode history has gaps")
notes=history[-1]["notes"]
data={"schema":1,"packageName":package,"versionCode":code,"versionName":version,
      "apkUrl":f"https://github.com/{repo}/releases/download/v{version}/PING-TEST.apk",
      "sha256":hashlib.sha256(apk.read_bytes()).hexdigest(),
      "sizeBytes":apk.stat().st_size,"publishedAt":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "notes":notes,"history":history}
out=pathlib.Path("dist/update.json")
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
with open(os.environ["GITHUB_OUTPUT"],"a",encoding="utf-8") as f:
    f.write(f"tag=v{version}\\nversion={version}\\nversion_code={code}\\n")
print("Signed OTA metadata prepared for",package,version,"history versions:",len(history))
