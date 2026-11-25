#!/usr/bin/env python3
"""Reproduce the optional mod from pinned official, unobfuscated26.3 inputs.

Uses javac25 directly, so a Java process need not have outbound networking.
Minecraft binaries are build inputs only and are never put in the mod archive.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import urllib.request
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

PROJECT=Path(__file__).resolve().parents[1]
LOCK=json.loads((PROJECT/'dependencies.lock.json').read_text())

def checked_file(path:Path,url:str,algorithm:str,expected:str)->Path:
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        request=urllib.request.Request(url,headers={'User-Agent':'GTM-HUD-reproducible-build/1.0'})
        with urllib.request.urlopen(request,timeout=40) as response:
            data=response.read()
        if hashlib.new(algorithm,data).hexdigest()!=expected:
            raise ValueError('Download fingerprint mismatch: '+url)
        temporary=path.with_suffix(path.suffix+'.part')
        temporary.write_bytes(data);temporary.replace(path)
    if hashlib.new(algorithm,path.read_bytes()).hexdigest()!=expected:
        raise ValueError('Existing build input fingerprint mismatch: '+str(path))
    return path

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home',type=Path,default=Path(os.environ.get('JAVA_HOME','')))
    parser.add_argument('--client-root',type=Path,default=PROJECT/'build/verified-deps/minecraft')
    parser.add_argument('--fabric-dir',type=Path,default=PROJECT/'build/verified-deps/fabric')
    parser.add_argument('--junit-console',type=Path)
    args=parser.parse_args()
    java=args.java_home/'bin'/('java.exe' if os.name=='nt' else 'java')
    javac=args.java_home/'bin'/('javac.exe' if os.name=='nt' else 'javac')
    if not java.is_file() or not javac.is_file():parser.error('--java-home must identify a JDK25 installation')
    version=subprocess.run([str(java),'-version'],capture_output=True,text=True,check=True).stderr
    if 'version "25' not in version:raise ValueError('This component targets Java25')
    mc=LOCK['minecraft'];root=args.client_root
    metadata=checked_file(root/'26.3.json',mc['version_url'],'sha1',mc['version_sha1'])
    manifest=json.loads(metadata.read_text());client=checked_file(root/'client.jar',manifest['downloads']['client']['url'],'sha1',mc['client_sha1'])
    libraries=[];requests=[]
    for lib in manifest['libraries']:
        item=lib.get('downloads',{}).get('artifact')
        if not item or ':natives-' in lib['name']:continue
        relative=Path(item['path'])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe official library path')
        path=root/'libraries'/relative;libraries.append(path)
        requests.append((path,item['url'],'sha1',item['sha1']))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(lambda params:checked_file(*params),requests):pass
    fabric=[]
    for key in ['loader','api']:
        entry=LOCK[key];name=entry['url'].rsplit('/',1)[1]
        fabric.append(checked_file(args.fabric_dir/name,entry['url'],'sha256',entry['sha256']))
    api_dir=PROJECT/'build/api-compile';api_dir.mkdir(parents=True,exist_ok=True)
    with ZipFile(fabric[1]) as archive:
        for name in archive.namelist():
            if name.startswith('META-INF/jars/') and name.endswith('.jar'):
                p=api_dir/Path(name).name;p.write_bytes(archive.read(name));libraries.append(p)
    cp=os.pathsep.join(str(p.resolve()) for p in [client,*libraries,fabric[0]])
    classes=PROJECT/'build/verified-classes'
    if classes.exists():shutil.rmtree(classes)
    classes.mkdir(parents=True)
    sources=sorted((PROJECT/'src/main/java').rglob('*.java'))
    subprocess.run([str(javac),'--release','25','-encoding','UTF-8','-cp',cp,'-d',str(classes),*[str(p) for p in sources]],check=True)
    junit=LOCK['junit'];testjar=checked_file(args.junit_console or PROJECT/'build/verified-deps/junit-console.jar',junit['url'],'sha256',junit['sha256'])
    tests=PROJECT/'build/verified-test-classes'
    if tests.exists():shutil.rmtree(tests)
    tests.mkdir(parents=True)
    testcp=os.pathsep.join([cp,str(classes),str(testjar)])
    subprocess.run([str(javac),'--release','25','-encoding','UTF-8','-cp',testcp,'-d',str(tests),*[str(p) for p in sorted((PROJECT/'src/test/java').rglob('*.java'))]],check=True)
    subprocess.run([str(java),'-cp',testcp+os.pathsep+str(tests),'org.junit.platform.console.ConsoleLauncher','execute','--scan-class-path='+str(tests),'--details=summary','--reports-dir='+str(PROJECT/'build/test-results/verified')],check=True)
    subprocess.run([sys.executable,str(PROJECT/'tools/prepare_assets.py')],check=True)
    files={}
    for base in [classes,PROJECT/'src/main/resources',PROJECT/'build/generated/assets']:
        for path in base.rglob('*'):
            if path.is_file():files[path.relative_to(base).as_posix()]=path.read_bytes()
    files['fabric.mod.json']=files['fabric.mod.json'].replace(b'${version}',b'1.0.0')
    output=PROJECT/'build/libs/GTM-Client-HUD-1.0.0.jar';output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',ZIP_DEFLATED) as archive:
        for name,data in sorted(files.items()):
            info=ZipInfo(name,(2026,11,25,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
            archive.writestr(info,data)
    report={'schema':'GTM_CLIENT_BUILD_V1','minecraft':'26.3','java':'25','loader':LOCK['loader']['version'],'fabric_api':LOCK['api']['version'],
            'compiled_sources':len(sources),'tests':'All discovered tests passed; see build/test-results/verified',
            'artifact':output.name,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'bytes':output.stat().st_size,
            'native_acceptance':'Recorded separately; compilation is not a render claim','minecraft_binaries_redistributed':False}
    (PROJECT/'build/build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
