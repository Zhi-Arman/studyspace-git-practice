from pathlib import Path
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
ORIGIN = PROJECT/'coursework/2026-10-21-git-environment-roles-v1/teaching-origin.git'
WORK = ROOT/'shared-work'
URL = 'https://github.com/Zhi-Arman/studyspace-git-practice'
log = []
def run(cwd, *args):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    log.append(dict(cwd=str(cwd),argv=list(args),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode: raise RuntimeError(log[-1])
    return p.stdout.strip()

rules = '''# 同步与角色协作规则

Синхронизация и правила совместной работы

SS-GIT-SYNC-01 · v1.0 · 2026-10-22 · Asia/Shanghai

## 1 本轮分工

1 Роли в этом упражнении

| 角色 Роль | 成员 Участник | 职责 Обязанности |
| --- | --- | --- |
| 作者 A Автор A | 支浩然 | 编辑 user-guide.md，检查本人差异并提交 PR。 Редактирует user-guide.md, проверяет diff и создаёт PR. |
| 作者 B Автор B | 俞智文 | 编辑 admin-guide.md，检查本人差异并提交 PR。 Редактирует admin-guide.md, проверяет diff и создаёт PR. |
| 审查者 Рецензент | 曹浩然 | 检查 A/B 的内容、双语对应、差异与冲突处理；不由作者自行批准。 Проверяет содержание A/B, языковые пары, diff и разрешение конфликтов; автор не утверждает собственный PR. |
| 协调人 Координатор | 吕嘉伟 | 维护分工、提交顺序和问题记录。 Ведёт роли, порядок работы и список вопросов. |

分工沿用 StudySpace 已有成员名单。个人账号授权与本人操作需由成员分别完成；自动化提交不代表成员本人批准。

Роли основаны на существующем списке StudySpace. Каждый участник отдельно подтверждает свой аккаунт и выполнение; автоматизированный коммит не означает личного согласования.

## 2 提交与 PR 语言

2 Язык коммитов и PR

commit 及 PR 标题、正文使用英语，文档正文保持中文在上、俄语在下。提交类型沿用 feat、fix、docs、test、refactor、chore。

Сообщения коммитов, заголовки и описания PR ведутся на английском. Документы сохраняют китайский текст над русским. Типы коммитов: feat, fix, docs, test, refactor, chore.

示例 Пример: `docs: clarify user guide editing steps`

PR 正文依次说明 Change、Validation、Reviewer；只记录实际运行的验证。

В описании PR указываются Change, Validation и Reviewer; перечисляются только выполненные проверки.

## 3 协作规则

3 Правила совместной работы

1. 禁止 force push，包括 --force、--force-with-lease 和非快进的 +refspec；遇到拒绝先停止，联系伙伴并检查差异。
   Принудительный push запрещён, включая --force, --force-with-lease и +refspec без fast-forward. При отказе остановитесь, обсудите ситуацию и проверьте diff.
2. 禁止删除本地或远程分支；PR 合并后也保留分支，关闭自动删除分支。
   Удаление локальных и удалённых веток запрещено. После слияния PR ветки сохраняются; автоматическое удаление отключается.
3. 开始工作前确认 git status 干净，先 fetch，再在 main 上执行 pull --ff-only。已有修改先保存并与成员协调，不用 reset --hard 或 clean 清场。
   Перед работой проверьте чистоту git status, выполните fetch и pull --ff-only в main. Существующие правки сохраняются и согласуются; reset --hard и clean для очистки не применяются.
4. 使用 feature/<topic>、fix/<topic> 或 docs/<topic> 分支，分别提交小范围 PR；作者不得自行批准，审查者检查双语内容、差异和验证证据。
   Используйте feature/<topic>, fix/<topic> или docs/<topic> и небольшие PR. Автор не утверждает свой PR; рецензент проверяет языковые пары, diff и свидетельства проверок.
5. 冲突时双方先确认应保留的内容，解决后用普通提交记录；不改写已共享历史。本规则用于当前练习，旧指南中的直接推送 main 示例属于上一轮本地演示。
   При конфликте согласуйте сохраняемое содержание и создайте обычный коммит, не переписывая общую историю. Эти правила действуют в текущем упражнении; примеры прямого push в main в старых руководствах относятся к предыдущей локальной демонстрации.

本文件记录协作约定；是否启用服务器端强制保护，应以 GitHub 仓库的实际设置为准。

Файл фиксирует правила команды. Наличие серверной защиты определяется фактическими настройками GitHub.
'''

readme = f'''# StudySpace Git 协作练习

Учебная совместная работа StudySpace в Git

2026-10-22 · v2 · 文档 DRAFT / Документы DRAFT

共享仓库 / Общий репозиторий: {URL}

本仓库延续实践 4.1.1 的本地文档练习历史，用于本轮同步、角色与后续分支协作。包含 README、用户指南、管理员指南和协作规则；不包含 StudySpace 应用业务实现。

Репозиторий продолжает локальную историю документов практики 4.1.1 и используется для синхронизации, ролей и последующей работы с ветками. Здесь README, руководство пользователя, руководство администратора и правила; бизнес-реализации StudySpace нет.

当前规则与分工见 [COLLABORATION.md](COLLABORATION.md)。A 编辑 [user-guide.md](user-guide.md)，B 编辑 [admin-guide.md](admin-guide.md)，审查者检查 PR。

Текущие роли и правила находятся в [COLLABORATION.md](COLLABORATION.md). A редактирует [user-guide.md](user-guide.md), B — [admin-guide.md](admin-guide.md); рецензент проверяет PR.

历史提交中的 Participant A/B 为本机演示身份。本轮自动化以已有本机作者身份提交，不冒充同学本人操作或批准。

Participant A/B в истории — локальные учебные подписи. Автоматизация использует существующую локальную подпись и не выдаётся за личную работу или одобрение студентов.
'''

if not WORK.exists(): run(ROOT,'git','clone','--no-hardlinks',str(ORIGIN),str(WORK))
assert run(WORK,'git','status','--porcelain') == ''
for key in ('user.name','user.email'):
    value = subprocess.check_output(['git','config','--local','--get',key],cwd=PROJECT,text=True).strip()
    subprocess.run(['git','config','--local',key,value],cwd=WORK,check=True)
(WORK/'README.md').write_text(readme)
(WORK/'COLLABORATION.md').write_text(rules)
(ROOT/'COLLABORATION.md').write_text(rules)
run(WORK,'git','diff','--check')
run(WORK,'git','add','--','README.md','COLLABORATION.md')
run(WORK,'git','commit','-m','docs: define synchronization roles and collaboration rules')
files=run(WORK,'git','ls-tree','-r','--name-only','HEAD').splitlines()
assert set(files)=={'.gitignore','README.md','COLLABORATION.md','user-guide.md','admin-guide.md'}
head=run(WORK,'git','rev-parse','HEAD')
(ROOT/'artifacts/online-preparation.json').write_text(json.dumps(dict(url=URL,private=True,files=files,head=head,commands=log),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(prepared=str(WORK),head=head,files=files),ensure_ascii=False,indent=2))
