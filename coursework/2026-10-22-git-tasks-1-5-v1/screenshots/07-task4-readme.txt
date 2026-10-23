Git practice 2026-10-22 | 07-task4-readme
Actual command output / Git 实际执行输出

$ git commit -m 'Обновлено описание практикума'
[update-readme a20991c] Обновлено описание практикума
 1 file changed, 2 insertions(+)

$ git diff main...update-readme
diff --git a/readme.txt b/readme.txt
index ed8d9a8..b62d070 100644
--- a/readme.txt
+++ b/readme.txt
@@ -1 +1,3 @@
 Проект: учебный
+
+Практикум Git: создание веток, слияние и разрешение конфликтов.

$ git log --oneline main..update-readme
a20991c Обновлено описание практикума

$ git status
On branch update-readme
nothing to commit, working tree clean
