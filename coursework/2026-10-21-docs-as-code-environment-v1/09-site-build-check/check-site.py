"""Use gstack browse to click the table of contents and inspect rendered content."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parent
ART=ROOT/'artifacts'
ART.mkdir(exist_ok=True)
B='/Users/zhi/.agents/skills/gstack/browse/dist/browse'
BASE='http://127.0.0.1:8767/'
records=[];checks=[]
def save():
    (ART/'browser-check.json').write_text(json.dumps({'date':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'driver':'gstack bundled Chromium','base_url':BASE,'records':records,'checks':checks},ensure_ascii=False,indent=2)+'\n')
def browse(*args):
    p=subprocess.run([B,*args],cwd=ROOT,text=True,capture_output=True,timeout=30)
    out=p.stdout+p.stderr
    records.append({'command':list(args),'exit_code':p.returncode,'output':out})
    save()
    if p.returncode:raise RuntimeError(out)
    return out
def js(code):
    return json.loads(browse('js',code))
def check(cid,zh,ru,ok,result,screenshot=None):
    checks.append({'id':cid,'zh':zh,'ru':ru,'passed':bool(ok),'result':result,'screenshot':screenshot})
    save()
    if not ok:raise AssertionError(cid+': '+json.dumps(result,ensure_ascii=False))
def snap():browse('snapshot','-i')
def shot(name):
    path=ART/(name+'.png');browse('screenshot','--viewport',str(path));return str(path.relative_to(ROOT))
def open_index():
    browse('goto',BASE+'index.html');snap()
def page_meta():
    return js('JSON.stringify({url:location.href,title:document.title,h1:document.querySelector(".body h1").innerText,overflow:document.documentElement.scrollWidth>innerWidth})')

browse('newtab',BASE+'index.html')
browse('viewport','1280x900')
browse('console','--clear')
open_index()
toc=js('JSON.stringify([...document.querySelectorAll(".toctree-wrapper a")].map(a=>({text:a.innerText,href:a.getAttribute("href")})))')
top=[x for x in toc if '#' not in x['href']]
check('P00','目录列出四个正文页面','Оглавление содержит четыре страницы',len(top)==4,top,shot('00-index'))
for i,item in enumerate(top,1):
    open_index()
    browse('click','.toctree-wrapper a[href="'+item['href']+'"]')
    snap();meta=page_meta()
    check('L0'+str(i),'从目录打开 '+item['text'],'Открыть из оглавления '+item['href'],
          meta['url'].split('#')[0]==BASE+item['href'] and not meta['overflow'],meta,shot('0'+str(i)+'-'+Path(item['href']).stem))

open_index()
target=next(x for x in toc if x['text'].startswith('7 更新'))
browse('click','.toctree-wrapper a[href="'+target['href']+'"]')
snap()
anchor=js('JSON.stringify({url:location.href,hash:location.hash,heading:document.getElementById(decodeURIComponent(location.hash.slice(1))).querySelector("h2").innerText,top:document.getElementById(decodeURIComponent(location.hash.slice(1))).getBoundingClientRect().top})')
check('L05','点击更新与回滚标题锚点','Переход к заголовку обновления и отката',
      anchor['hash'] and '7 更新' in anchor['heading'] and -5<=anchor['top']<=150,anchor,shot('05-heading-anchor'))

browse('goto',BASE+'admin-guide.html');snap()
img=js('JSON.stringify((()=>{const x=document.querySelector(".body img");x.scrollIntoView();return {src:x.src,complete:x.complete,naturalWidth:x.naturalWidth,naturalHeight:x.naturalHeight,alt:x.alt};})())')
browse('screenshot','--selector','.body img',str(ART/'06-image.png'))
check('L06','检查文中图片加载与替代文本','Загрузка изображения и альтернативный текст',
      img['complete'] and img['naturalWidth']==1000 and bool(img['alt']),img,'artifacts/06-image.png')
browse('goto',img['src'])
svg=js('JSON.stringify({url:location.href,root:document.documentElement.tagName,text:document.documentElement.textContent})')
check('L07','直接打开图片资源链接','Прямой переход к ресурсу изображения',
      svg['root'].lower()=='svg' and 'SQLite' in svg['text'],{'url':svg['url'],'root':svg['root']},shot('07-image-resource'))

open_index()
browse('fill','.sphinxsidebar input[name="q"]','SQLite')
browse('press','Enter')
browse('wait','.search li a')
snap()
search=js('JSON.stringify({url:location.href,links:[...document.querySelectorAll(".search li a")].map(a=>({text:a.innerText,href:a.getAttribute("href")}))})')
shot('08-search-results')
browse('click','.search li a[href="admin-guide.html"]');snap()
meta=page_meta()
check('L08','搜索后点击管理员手册结果','Поиск и переход к результату',
      len(search['links'])>=1 and meta['url']==BASE+'admin-guide.html',{'search':search,'landing':meta},shot('08-search-landing'))

metrics=js('JSON.stringify({commands:[...document.querySelectorAll(".body pre")].map(x=>({fontSize:getComputedStyle(x).fontSize,whiteSpace:getComputedStyle(x).whiteSpace,clientWidth:x.clientWidth,scrollWidth:x.scrollWidth,text:x.innerText})),tables:[...document.querySelectorAll(".body table")].map(x=>({fontSize:getComputedStyle(x).fontSize,rows:x.rows.length,clientWidth:x.clientWidth,scrollWidth:x.scrollWidth})),warnings:[...document.querySelectorAll(".body p")].filter(x=>x.innerText.startsWith("警告：")).map(x=>({text:x.innerText,fontSize:getComputedStyle(x).fontSize,display:getComputedStyle(x).display,color:getComputedStyle(x).color})),overflow:document.documentElement.scrollWidth>innerWidth})')
js('JSON.stringify((()=>{[...document.querySelectorAll(".body pre")].find(x=>x.innerText.includes("uv sync")).scrollIntoView();return true;})())')
commands_pic=shot('09-commands')
check('R01','命令完整换行且无截断','Команды переносятся без обрезки',
      all(float(x['fontSize'].replace('px',''))>=13 and x['scrollWidth']<=x['clientWidth']+1 for x in metrics['commands']),
      metrics['commands'],commands_pic)
js('JSON.stringify((()=>{document.querySelector(".body table").scrollIntoView();return true;})())')
table_pic=shot('10-table')
check('R02','表格字体及单元格内容可读','Таблицы и содержимое ячеек читаются',
      len(metrics['tables'])==3 and all(float(x['fontSize'].replace('px',''))>=13 and x['scrollWidth']<=x['clientWidth']+1 for x in metrics['tables']),
      metrics['tables'],table_pic)
table_sections=js('JSON.stringify([...document.querySelectorAll(".body table")].map(x=>x.closest("section").id))')
for i,sid in enumerate(table_sections[1:],2):
    browse('screenshot','--selector','#'+sid+' table',str(ART/('10-table-'+str(i)+'.png')))
js('JSON.stringify((()=>{[...document.querySelectorAll(".body p")].filter(x=>x.innerText.startsWith("警告："))[2].scrollIntoView();return true;})())')
warning_pic=shot('11-warning')
check('R03','安装恢复更新警告可读','Предупреждения установки восстановления обновления читаются',
      len(metrics['warnings'])==3 and all(float(x['fontSize'].replace('px',''))>=15 and x['display']!='none' for x in metrics['warnings']),
      metrics['warnings'],warning_pic)
console=browse('console','--errors')
check('C01','本地页面控制台无错误','Нет ошибок консоли локальных страниц','(no console errors)' in console,console)
browse('closetab')
save()
print(json.dumps({'checks':len(checks),'passed':sum(x['passed'] for x in checks),'link_or_navigation_checks':sum(x['id'].startswith('L') for x in checks),'commands':len(records)},ensure_ascii=False))
