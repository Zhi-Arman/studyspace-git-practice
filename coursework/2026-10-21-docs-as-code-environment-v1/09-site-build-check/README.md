# StudySpace 第五部分网站与构建检查

StudySpace Часть 5 Проверка сайта и сборки

SS-DAC-CHECK-05 · v1.0 · DRAFT · 2026-10-21 · Asia/Shanghai

已完成图片六项要求：严格构建与退出码、全部目录页实际点击、8 项链接或资源检查（含图片和标题）、命令表格警告可读性、问题处理和复测、应用命令未验证边界。报告为中俄双语，未代替团队或教师签字。

Выполнены шесть требований фото: строгая сборка с кодом, переходы на все страницы, 8 проверок ссылок/ресурсов с изображением и заголовком, читаемость, исправление и повторная проверка, границы команд приложения. Отчёт двуязычный, без подмены подписей команды или преподавателя.

- [Word 报告 Отчёт Word](StudySpace_任务五网站与构建检查_中俄双语_v1.docx)
- [Markdown 报告 Отчёт Markdown](StudySpace_任务五网站与构建检查_中俄双语_v1.md)
- [首次构建 初测 JSON](artifacts/initial-build.json) · [日志 Журнал](artifacts/initial-build.log)
- [最终构建 复测 JSON](artifacts/final-build.json) · [日志 Журнал](artifacts/final-build.log)
- [初轮浏览器工具超时记录 Первый тайм-аут](artifacts/browser-check-initial.json)
- [最终浏览器记录 Итоговая проверка браузера](artifacts/browser-check.json)
- [88 项既有交付检查 Проверки прежней поставки](artifacts/delivery-verification.json)
- [本报告结构与交付检查 Проверка этого отчёта](artifacts/report-verification.json)
- [前一部分网站 Главная предыдущей части](../08-sphinx-site/project-docs/site/index.html)

首次和最终构建均退出 0、警告 0；13 项浏览器检查通过，其中 L01–L08 为链接或资源检查。gstack 读取独立 SVG 交互快照超时已通过更换 SVG 检查方式解决，HTML 页面仍做真实点击与快照。网站源文件未修改。

Обе сборки: код 0, предупреждений 0. Пройдены 13 проверок браузера, L01–L08 касаются ссылок/ресурсов. Тайм-аут snapshot SVG обойдён подходящей проверкой SVG; HTML по-прежнему проверяется реальными кликами и snapshot. Исходники сайта сохранены.

所有截图位于 artifacts/00-index.png 至 11-warning.png，另有 10-table-2.png、10-table-3.png；Word 的 PDF/PNG 位于 artifacts/report-render-final，仅为内部排版 QA。应用安装、启停、恢复、升级回滚和业务验收本轮未执行。

Снимки в artifacts/00-index.png–11-warning.png, дополнительно 10-table-2.png и 10-table-3.png. PDF/PNG Word в artifacts/report-render-final только для внутреннего QA. Установка, запуск, восстановление, обновление/откат приложения и бизнес-приёмка сейчас не выполнялись.

## 复核方法 Как повторить

先在前一部分 project-docs 运行仅绑定回环地址的静态服务器，再从本目录运行下列命令。浏览器脚本只调用 gstack browse CLI；需要允许本地端口。脚本会新建并关闭自己的标签。

Сначала запустить loopback-сервер предыдущего project-docs, затем из этой папки выполнить команды. Скрипт использует только gstack browse CLI; требуется доступ к локальному порту. Собственные вкладки открываются и закрываются скриптом.

```bash
../08-sphinx-site/project-docs/.venv/bin/python run-build.py initial
../08-sphinx-site/project-docs/.venv/bin/python check-site.py
../08-sphinx-site/project-docs/.venv/bin/python run-build.py final
```

这些复核脚本会更新本部分证据文件；当前交付已保留实际初测和最终结果。构建工作目录、完整命令、时间和退出码均在 build.json；原始图片哈希与要求清单在 artifacts/task-input.json。

При повторе обновляются свидетельства этой части; текущая поставка уже содержит фактические результаты. Каталог, команды, время и коды — в build.json, хеш фото и требования — в artifacts/task-input.json.
