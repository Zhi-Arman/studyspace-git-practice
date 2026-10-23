import datetime, json, os, shlex, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'artifacts'; S=ROOT/'screenshots'; S.mkdir(exist_ok=True)
REPO=Path('/Users/zhi/Documents/软件生命周期/git-practice/lab-git')
ENV=dict(os.environ, LC_ALL='en_US.UTF-8', GIT_MERGE_AUTOEDIT='no')
LOG=A/'commands.json'
records=json.loads(LOG.read_text()) if LOG.exists() else []
stage=sys.argv[1]; evidence=[]

def run(*args, expected=0, show=False):
 p=subprocess.run(args,cwd=REPO,env=ENV,text=True,capture_output=True)
 r=dict(stage=stage,command=shlex.join(args),stdout=p.stdout,stderr=p.stderr,exit=p.returncode,time=datetime.datetime.now(datetime.timezone.utc).isoformat())
 records.append(r); LOG.write_text(json.dumps(records,ensure_ascii=False,indent=2))
 txt='$ '+r['command']+'\n'+r['stdout']+r['stderr']
 if not r['stdout'] and not r['stderr']: txt+='[success; no output]\n'
 if show:evidence.append(txt)
 if p.returncode!=expected: raise RuntimeError(r)
 return p.stdout.strip()

def shell(s): return run('/bin/zsh','-c',s)

if stage=='01-task1':
 assert not LOG.exists(), 'Do not repeat reset'
 backup=Path('/Users/zhi/Documents/软件生命周期/studyspace/coursework/2026-10-22-git-branches-conflict-v1/artifacts/completed-repository.bundle')
 assert REPO.resolve()==Path('/Users/zhi/Documents/软件生命周期/git-practice/lab-git') and (REPO/'.git').is_dir()
 assert run('git','status','--porcelain')==''
 run('git','bundle','verify',str(backup))
 shutil.copy2(backup,A/'previous-repository.bundle')
 shutil.rmtree(REPO); REPO.mkdir()
 run('git','init','-b','main')
 run('git','config','user.name','支浩然')
 run('git','config','user.email','zhr050819@gmail.com')
 shell('printf "%s\\n" "Проект: учебный" > readme.txt')
 run('git','status','--short')
 run('git','add','readme.txt')
 run('git','commit','-m','Добавлен readme',show=True)
 run('git','config','user.name',show=True)
 run('git','log','--oneline',show=True)
 run('cat','readme.txt',show=True)
 run('git','status',show=True)
 assert run('git','rev-list','--count','HEAD')=='1'
elif stage=='02-task2':
 run('git','branch','feature-a');run('git','switch','feature-a')
 shell('printf "%s\\n" "Функция A" > a.txt')
 run('git','add','a.txt');run('git','commit','-m','Добавлена функция A')
 run('git','switch','main');assert not (REPO/'a.txt').exists()
 run('git','merge','feature-a',show=True)
 run('git','branch',show=True);run('cat','a.txt',show=True)
 run('git','log','--oneline',show=True);run('git','status',show=True)
 assert run('git','rev-list','--count','HEAD')=='2'
elif stage=='03-task3-branches':
 shell('printf "%s\\n" "Цена: 100 рублей" > price.txt')
 run('git','add','price.txt');run('git','commit','-m','Добавлена цена')
 run('git','branch','price-up');run('git','branch','price-promo')
 run('git','switch','price-up');shell('printf "%s\\n" "Цена: 120 рублей" > price.txt')
 run('git','commit','-am','Повышена цена')
 run('git','switch','price-promo');assert run('cat','price.txt')=='Цена: 100 рублей'
 shell('printf "%s\\n" "Цена: 90 рублей" > price.txt');run('git','commit','-am','Акционная цена')
 run('git','switch','main')
 for ref in ['main','price-up','price-promo']:run('git','show',ref+':price.txt',show=True)
 run('git','log','--oneline','--graph','--decorate','--all',show=True)
elif stage=='04-task3-conflict':
 run('git','merge','price-up',show=True)
 out=run('git','merge','price-promo',expected=1,show=True);assert 'CONFLICT' in out
 run('git','status','--short',show=True);run('cat','price.txt',show=True)
 (A/'price-conflict.txt').write_text((REPO/'price.txt').read_text())
 assert run('git','ls-files','-u')
elif stage=='05-task3-resolved':
 shell('printf "%s\\n" "Цена: 90 рублей" > price.txt')
 run('git','add','price.txt');run('git','commit','-m','Разрешён конфликт цены',show=True)
 run('cat','price.txt',show=True);run('git','status',show=True)
 run('git','log','--oneline','--graph','--decorate',show=True)
 assert len(run('git','show','-s','--format=%P','HEAD').split())==2
elif stage=='06-task4-tag':
 run('git','tag','v1.0.0',show=True)
 run('git','tag','--list',show=True)
 run('git','log','-1','--oneline','--decorate',show=True)
 run('git','show','v1.0.0:price.txt',show=True)
 run('git','status',show=True)
elif stage=='07-task4-readme':
 run('git','switch','-c','update-readme')
 shell('printf "\\n%s\\n" "Практикум Git: создание веток, слияние и разрешение конфликтов." >> readme.txt')
 run('git','add','readme.txt');run('git','commit','-m','Обновлено описание практикума',show=True)
 run('git','diff','main...update-readme',show=True)
 run('git','log','--oneline','main..update-readme',show=True)
 run('git','status',show=True)
elif stage=='10-final':
 run('git','switch','main')
 run('git','log','--oneline','--graph','--decorate','--all',show=True)
 run('git','status',show=True)
 run('git','tag','--list',show=True)
 assert run('git','status','--porcelain')==''
 assert run('git','ls-files','-u')==''
 assert run('git','rev-list','--count','main')=='6'
 assert run('git','rev-list','--count','main..update-readme')=='1'
 assert run('git','diff','--name-only','main...update-readme')=='readme.txt'
 assert run('git','rev-parse','v1.0.0')==run('git','rev-parse','main')
 assert run('cat','price.txt')=='Цена: 90 рублей'
 run('git','bundle','create',str(A/'completed-repository.bundle'),'--all')
 (A/'verification.json').write_text(json.dumps(dict(all_pass=True,main_commits=6,all_commits=7,tag='v1.0.0',final_price=90,conflict_observed=True,clean=True,branch='main',remote_pr='NOT_CREATED',repo=str(REPO),commits=run('git','log','--oneline','--all'),verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat()),ensure_ascii=False,indent=2))
else:raise ValueError(stage)

(S/(stage+'.txt')).write_text('Git practice 2026-10-22 | '+stage+'\nActual command output / Git 实际执行输出\n\n'+'\n'.join(evidence))
(ROOT/'终端实际操作记录.md').write_text('# Git 全程实际执行记录\n\n'+ '\n\n'.join('## '+r['stage']+'\n\n```console\n$ '+r['command']+'\n'+r['stdout']+r['stderr']+'[exit '+str(r['exit'])+']\n```' for r in records))
print((S/(stage+'.txt')).read_text())
