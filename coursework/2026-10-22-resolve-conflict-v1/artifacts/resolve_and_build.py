from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from html.parser import HTMLParser
import hashlib
import json
import re
import shlex
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[1]
PREVIOUS=PROJECT/'coursework/2026-10-22-controlled-conflict-v1'
B=PREVIOUS/'author-b'
OLD=json.loads((PREVIOUS/'artifacts/execution.json').read_text())
COURSE=PROJECT/'coursework/2026-10-21-docs-as-code-environment-v1/08-sphinx-site/project-docs'
FILE='docs/build-check.md'
RESOLVED='.venv/bin/python -m sphinx -W -n -b html docs site\n'
FILES=['.gitignore','docs/build-check.md','docs/conf.py','docs/index.md','requirements-docs.txt']
commands=[];checks=[]
def run(cwd,*argv,ok=True):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
    commands.append(dict(cwd=str(cwd),argv=list(argv),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if ok and p.returncode:raise RuntimeError(commands[-1])
    return p.stdout.strip(),p.returncode
def out(cwd,*argv):return run(cwd,*argv)[0]
def check(name,value):
    checks.append(dict(name=name,passed=bool(value)));assert value,name
def save(name,value):(ROOT/'artifacts'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
if '--resume-build' not in __import__('sys').argv:
    check('expected unresolved file',out(B,'git','status','--porcelain=v1')=='UU '+FILE)
    check('HEAD matches A merge',out(B,'git','rev-parse','HEAD')==OLD['a_merge_commit'])
    check('MERGE_HEAD matches B commit',out(B,'git','rev-parse','MERGE_HEAD')==OLD['b_head'])
    before=(B/FILE).read_text()
    check('conflict content matches archived scene',before==OLD['conflict_text'])
    stages={str(i):out(B,'git','show',f':{i}:'+FILE)+'\n' for i in (1,2,3)}
    check('both A B options verified',stages['2']==OLD['commands_text']['A'] and stages['3']==OLD['commands_text']['B'])
    (ROOT/'artifacts/conflict-before.md').write_text(before)
    (ROOT/'artifacts/index-before.txt').write_text(out(B,'git','ls-files','--unmerged')+'\n')
    (ROOT/'artifacts/status-before.txt').write_text(out(B,'git','status')+'\n')
    (ROOT/'artifacts/gitignore-before.txt').write_text((B/'.gitignore').read_text())
    save('before.json',dict(head=OLD['a_merge_commit'],merge_head=OLD['b_head'],stages=stages))
    shutil.copy2('/var/folders/ff/kqw394c93dd7krl0z2hcqqdh0000gn/T/codex-clipboard-3175d237-1a9e-45db-a92a-e9d13b3783ba.jpg',ROOT/'artifacts/task.jpg')
    for n in ('docs/conf.py','docs/index.md','requirements-docs.txt'):
        check(n+' is new support file',not (B/n).exists())
    check('isolated virtual environment is new',not (B/'.venv').exists())
    (B/FILE).write_text(RESOLVED)
    check('resolution preserves both flags',('-W' in RESOLVED and '-n' in RESOLVED))
    check('conflict markers removed',not re.search(r'^(<<<<<<<|=======|>>>>>>>)', (B/FILE).read_text(),re.M))
    (B/'docs/conf.py').write_text('''project = "StudySpace Git Practice"
    author = "StudySpace"
    copyright = "2026 StudySpace"
    release = "1.0"
    extensions = ["myst_parser"]
    source_suffix = {".md": "markdown"}
    root_doc = "index"
    language = "zh_CN"
    exclude_patterns = ["build-check.md"]
    html_theme = "alabaster"
    html_title = "StudySpace Git 协作练习 / Практика Git"
    nitpicky = True
    ''')
    (B/'docs/index.md').write_text('''# StudySpace Git 协作练习
    
    Практика совместной работы StudySpace в Git
    
    本页构建当前仓库的用户指南、管理员指南和已解决冲突的构建命令。课程文档状态为 DRAFT，构建成功不代表业务实现或验收。
    
    Здесь собираются руководства пользователя и администратора текущего репозитория и команда после разрешения конфликта. Документы имеют статус DRAFT; успешная сборка не означает реализацию или приёмку приложения.
    
    ## 1 环境准备
    
    1 Подготовка среды
    
    在仓库根目录用 Python 3.13 与 uv 创建环境，并按哈希锁定依赖：
    
    В корне репозитория создайте среду с Python 3.13 и uv, затем установите зависимости с проверкой хешей:
    
    ```bash
    uv venv --python 3.13 .venv
    uv pip sync --require-hashes --python .venv/bin/python requirements-docs.txt
    ```
    
    ## 2 构建检查命令
    
    2 Команда проверки сборки
    
    最终命令同时保留 A 的 -W 与 B 的 -n。执行前确认位于仓库根目录，site 为本地产物目录。
    
    Итоговая команда сохраняет -W из версии A и -n из версии B. Выполняйте её из корня репозитория; site содержит локальный результат.
    
    ```{literalinclude} build-check.md
    :language: bash
    ```
    
    ## 3 用户指南
    
    3 Руководство пользователя
    
    ```{include} ../user-guide.md
    ```
    
    ## 4 管理员指南
    
    4 Руководство администратора
    
    ```{include} ../admin-guide.md
    ```
    ''')
    shutil.copy2(COURSE/'requirements-docs.txt',B/'requirements-docs.txt')
    ignore=(B/'.gitignore').read_text().rstrip()+'\n'
    for line in ('.venv/','site/','__pycache__/'):
        if line not in ignore.splitlines():ignore+=line+'\n'
    (B/'.gitignore').write_text(ignore)
    out(B,'git','diff','--check')
    (ROOT/'artifacts/resolution-before-stage.diff').write_text(out(B,'git','diff','--cc','--',FILE)+'\n')
    check('index still unmerged before build',len(out(B,'git','ls-files','--unmerged').splitlines())==3)
    save('resolution-prepared.json',dict(resolved_command=RESOLVED,support_files=FILES,working_directory=str(B),status='READY_TO_BUILD'))
    out(B,'uv','venv','--python',str(COURSE/'.venv/bin/python'),'.venv')
else:
    check('archived original scene preserved',(ROOT/'artifacts/conflict-before.md').read_text()==OLD['conflict_text'])
    check('resume keeps expected HEAD',out(B,'git','rev-parse','HEAD')==OLD['a_merge_commit'])
    check('resume keeps expected MERGE_HEAD',out(B,'git','rev-parse','MERGE_HEAD')==OLD['b_head'])
    check('resume final command preserved',(B/FILE).read_text()==RESOLVED)
    check('resume support files exist',all((B/n).is_file() for n in FILES))
    check('resume keeps three unresolved index stages',len(out(B,'git','ls-files','--unmerged').splitlines())==3)
    check('resume uses exact course dependency lock',(B/'requirements-docs.txt').read_bytes()==(COURSE/'requirements-docs.txt').read_bytes())
    out(B,'git','diff','--check')
out(B,'uv','pip','sync',*([] if '--online' in __import__('sys').argv else ['--offline']),'--require-hashes','--strict','--python','.venv/bin/python','requirements-docs.txt')
out(B,'uv','pip','check','--python','.venv/bin/python')
version=out(B,'.venv/bin/python','-c','import sys,sphinx,myst_parser; print(sys.version.split()[0]); print(sphinx.__version__); print(myst_parser.__version__)')
build_stdout,build_code=run(B,*shlex.split(RESOLVED),ok=False)
build=commands[-1]
(ROOT/'artifacts/sphinx-build.log').write_text(build['stdout']+build['stderr'])
save('build-command.json',build)
check('resolved command builds current repository',build_code==0)
warnings=len(re.findall(r'\bWARNING:',build['stdout']+build['stderr']))
check('strict nitpicky build has zero warnings',warnings==0)
check('HTML index generated',(B/'site/index.html').is_file())
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)
t=Text();t.feed((B/'site/index.html').read_text())
visible=' '.join(''.join(t.parts).split())
check('built page contains resolved command',RESOLVED.strip() in visible)
check('built page contains current user guide','Markdown 用户指南' in visible and 'Руководство пользователя Markdown' in visible)
check('built page contains current admin guide','Git 练习管理员指南' in visible)
check('venv and site are ignored',out(B,'git','check-ignore','.venv/pyvenv.cfg','site/index.html').splitlines()==['.venv/pyvenv.cfg','site/index.html'])
out(B,'git','diff','--check')
out(B,'git','add','--',*FILES)
check('staging resolves all unmerged entries',out(B,'git','ls-files','--unmerged')=='')
check('staged command matches final decision',out(B,'git','show',':'+FILE)+'\n'==RESOLVED)
staged=out(B,'git','diff','--cached','--name-only').splitlines()
check('only necessary five files staged',set(staged)==set(FILES))
out(B,'git','diff','--cached','--check')
(ROOT/'artifacts/staged.diff').write_text(out(B,'git','diff','--cached','--stat')+'\n\n'+out(B,'git','diff','--cached','--',FILE,'.gitignore','docs/conf.py','docs/index.md')+'\n')
out(B,'git','commit','-m','docs: resolve build command conflict and enable reproducible docs build')
resolution=out(B,'git','rev-parse','HEAD')
parents=out(B,'git','rev-list','--parents','-n','1','HEAD').split()
check('resolution commit retains both merge parents',parents==[resolution,OLD['a_merge_commit'],OLD['b_head']])
check('merge state cleared',not (B/'.git/MERGE_HEAD').exists())
check('resolved worktree clean',out(B,'git','status','--porcelain=v1','--untracked-files=all')=='')
out(B,'git','fsck','--full')
(ROOT/'artifacts/history-local.txt').write_text(out(B,'git','log','--graph','--oneline','--decorate','-12')+'\n')
result=dict(executed_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),status='RESOLVED_BUILT_COMMITTED',
            working_directory=str(B),file=FILE,resolved_command=RESOLVED,base_main=OLD['a_merge_commit'],b_original=OLD['b_head'],
            resolution_commit=resolution,resolution_parents=parents[1:],files=FILES,staged_files=staged,
            build_exit_code=build_code,build_warnings=warnings,versions=version,html=str(B/'site/index.html'),
            requirements_sha256=hashlib.sha256((B/'requirements-docs.txt').read_bytes()).hexdigest(),
            mode='SINGLE_ACCOUNT_AUTOMATED_ROLE_DEMO',human_agreement='NOT_VERIFIED',business_tests='NOT_RUN',
            checks=checks,commands=commands)
save('local-resolution.json',result)
print(json.dumps({k:result[k] for k in ('status','resolution_commit','resolved_command','build_exit_code','build_warnings','versions','html')},ensure_ascii=False,indent=2))
print('Local checks passed:',len(checks),'/',len(checks))
