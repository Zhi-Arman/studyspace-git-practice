# 账号 Bot 操作提示 / Инструкции для ботов участников

中文：将对应代码块交给该成员本人电脑上的 Bot。已授权的范围仅为本仓库；本人登录如需交互，由本人完成。不输出凭据，不覆盖目录，不强推或删除分支，不合并 PR。

Русский: Передайте соответствующий блок боту на компьютере участника. Разрешён только указанный репозиторий; интерактивный вход выполняет сам участник. Не раскрывать секреты, не перезаписывать каталоги, не применять force push, не удалять ветки и не сливать PR.

## B 曹浩然：like577 / B

```text
请以我的 GitHub 账号 like577 完成仓库准备练习的 B 步骤：
仓库为 Zhi-Arman/studyspace-git-practice。
先用 gh api user --jq .login 确认账号为 like577；不符则提示本人切换登录，不使用别人的凭据。
如仍有本仓库协作邀请，核对仓库后接受；若已接受则继续。
在合适的课程目录克隆仓库；如已有该仓库则先检查状态，不覆盖目录或丢弃修改。
获取远程分支（git fetch origin，不加 --prune），检查工作区干净后切换到 feature/status-transitions，跟踪 origin/feature/status-transitions。
已有该分支时检查本地与远程差异；不 reset --hard，不强制覆盖，不改写历史。
进入 classroom-git，运行 python3 -m unittest discover -s tests -v（Windows 可按实际 Python 命令调整）。
回到仓库根目录，用本人账号创建 feature/status-transitions -> main 的 PR；标题为 feat: add ticket status transitions。
正文必须原样读取 pr-descriptions/status-transitions.md，保持老师图片要求的故意薄弱初始描述。
可用命令：gh pr create --repo Zhi-Arman/studyspace-git-practice --base main --head feature/status-transitions --title "feat: add ticket status transitions" --body-file pr-descriptions/status-transitions.md
先查询是否已有同来源与目标分支的 PR；若作者为 like577 则返回现有链接，避免重复；若作者不是本人则报告事实，不冒称本人创建。
不要合并任何 PR；代码已由仓库所有者准备，不要把现有代码提交声称为本人编写。
最后回传：登录用户名、接受邀请结果、仓库绝对路径、当前分支、远程地址、工作区状态、测试真实结果、PR 链接和实际作者。
```

## D 吕嘉伟（项目经理）：lvjiaw / D, менеджер проекта

```text
我是成员 D 吕嘉伟，请以我的 GitHub 账号 lvjiaw 检查 Zhi-Arman/studyspace-git-practice 的访问权限并克隆仓库；已接受邀请时直接继续。
先确认 GitHub 登录账号确实为 lvjiaw；若需要本人登录，提示我操作，不输出凭据。
打开 https://github.com/Zhi-Arman/studyspace-git-practice/invitations 并核对后接受。
也可用 gh api user/repository_invitations 查询邀请，核对 full_name 后仅接受本仓库的邀请。
在合适的课程目录执行 git clone https://github.com/Zhi-Arman/studyspace-git-practice.git；已有目录则先检查，不覆盖或删除。
检查 git remote -v、git branch --show-current、git status --short --branch。
回传：登录账号、邀请是否接受、仓库绝对路径、当前分支和工作区状态。
仅接受邀请并克隆，不修改文件、不推送、不创建或合并 PR。
```
