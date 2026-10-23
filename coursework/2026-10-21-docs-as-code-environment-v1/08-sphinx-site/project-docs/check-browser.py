"""Drive gstack browse only; capture local page, search and download evidence."""
from pathlib import Path
import subprocess
import json

ROOT=Path(__file__).resolve().parent
B='/Users/zhi/.agents/skills/gstack/browse/dist/browse'
records=[]
def browse(*args):
    p=subprocess.run([B,*args],text=True,capture_output=True,cwd=ROOT)
    out=p.stdout+p.stderr
    records.append({'command':list(args),'exit_code':p.returncode,'output':out})
    if p.returncode:raise RuntimeError(out)
    return out

browse('console','--clear')
for name in ['index','user-guide','admin-guide','release-notes','document-register']:
    browse('goto','http://127.0.0.1:8767/'+name+'.html')
    browse('snapshot','-i')
    browse('js','JSON.stringify({url:location.href,title:document.title,h1:document.querySelector(".body h1").innerText,overflow:document.documentElement.scrollWidth>innerWidth,headings:document.querySelectorAll(".body h2").length})')
    browse('screenshot','--viewport',str(ROOT/'artifacts'/('browser-'+name+'.png')))
    browse('console','--errors')

browse('goto','http://127.0.0.1:8767/search.html?q=SQLite')
browse('snapshot','-i')
browse('js','JSON.stringify({query:new URLSearchParams(location.search).get("q"),results:[...document.querySelectorAll(".search li a")].map(a=>({text:a.innerText,href:a.getAttribute("href")}))})')
browse('screenshot','--viewport',str(ROOT/'artifacts/browser-search.png'))
browse('console','--errors')
browse('goto','http://127.0.0.1:8767/document-register.html')
browse('snapshot','-i')
browse('js','(async () => { const links = [...document.querySelectorAll("a.reference.download")]; const result = await Promise.all(links.map(async a => { const r = await fetch(a.href, {method:"HEAD"}); return {url:a.href,status:r.status}; })); return JSON.stringify(result); })()')
browse('goto','http://127.0.0.1:8767/index.html')
browse('snapshot','-i')
browse('viewport','375x812')
browse('js','JSON.stringify({width:innerWidth,contentWidth:document.documentElement.scrollWidth,overflow:document.documentElement.scrollWidth>innerWidth})')
browse('screenshot','--viewport',str(ROOT/'artifacts/browser-mobile.png'))
browse('viewport','1280x900')
browse('console','--errors')
(ROOT/'artifacts/browser-verification.json').write_text(json.dumps({'date':'2026-10-21','driver':'gstack bundled Chromium','records':records},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'commands':len(records),'command_failures':sum(x['exit_code']!=0 for x in records),'report':'artifacts/browser-verification.json'}))
