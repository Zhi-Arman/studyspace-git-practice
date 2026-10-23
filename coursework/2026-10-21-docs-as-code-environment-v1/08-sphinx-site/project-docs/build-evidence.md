# Sphinx 构建证据

Свидетельства сборки Sphinx

SS-DAC-BUILD-01 · v0.2 · 2026-10-21 · Asia/Shanghai

执行者 Codex。工作目录为本文件所在 project-docs；macOS arm64、Python 3.13.12、uv 0.11.17。独立 .venv 内 Sphinx 8.2.3、MyST 4.0.1，共 28 包；是固定兼容组合，不声称最新版本。

Исполнитель Codex. Рабочий каталог — project-docs; macOS arm64, Python 3.13.12, uv 0.11.17. В отдельной .venv Sphinx 8.2.3, MyST 4.0.1, всего 28 пакетов; фиксированная совместимая комбинация, не заявление о новейшей версии.

## 1 安装 Установка

```bash
UV_CACHE_DIR=/private/tmp/studyspace-sphinx-uv-cache uv venv --python 3.13 \
  --no-python-downloads .venv
UV_CACHE_DIR=/private/tmp/studyspace-sphinx-uv-cache uv pip compile \
  requirements-docs.in --generate-hashes --output-file requirements-docs.txt
UV_CACHE_DIR=/private/tmp/studyspace-sphinx-uv-cache uv pip sync \
  --python .venv/bin/python --require-hashes requirements-docs.txt
UV_CACHE_DIR=/private/tmp/studyspace-sphinx-uv-cache uv pip check --python .venv/bin/python
```

安装退出 0，兼容性检查 `All installed packages are compatible`。完整日志：artifacts/dependency-resolution.log、artifacts/dependency-install.log。受限环境首次 DNS 失败，获得本次网络执行授权后按相同固定依赖安装成功；原有环境不变。

Код установки 0, совместимость подтверждена. Журналы: artifacts/dependency-resolution.log и artifacts/dependency-install.log. Первичная ограниченная попытка не разрешала DNS; после разрешённого сетевого запуска установка успешна с теми же зависимостями; прежние среды сохранены.

## 2 严格构建 Строгая сборка

```bash
bash build-site.sh
# 脚本实际执行 / Фактическая команда
.venv/bin/python -m sphinx -b html -n -W --keep-going -E -a -N \
  -w artifacts/sphinx-warnings.log docs site
.venv/bin/python verify.py
```

最终严格构建退出 0，输出 `build succeeded.`，警告文件为空。`-n` 检查缺失引用，`-W` 把警告视为失败，`-E -a` 重读并重写全部页面；未屏蔽警告。首次构建发现 dotenv 高亮标签不支持，改为 ini 后重新严格构建通过。

Итог: код 0, `build succeeded.`, предупреждений нет. `-n` проверяет ссылки, `-W` превращает предупреждения в ошибки, `-E -a` перечитывает и переписывает всё. Предупреждения не подавлены; неподдерживаемая метка dotenv исправлена на ini и сборка повторена.

生成 site/index.html、四正文页面、搜索和索引。verify.py 的 88 项检查通过，250 处本地链接、资源与锚点无断链；22 份源文件与副本 SHA-256 均一致。证据：artifacts/sphinx-build.log、sphinx-warnings.log、verification.json、source-manifest.json。外部链接不在本地爬取范围。

Созданы главная, четыре страницы, поиск и индекс. 88 проверок пройдены, 250 локальных ссылок/ресурсов/якорей без разрывов; SHA-256 22 источников и копий совпадают. Свидетельства в перечисленных файлах artifacts. Внешние ссылки отдельно не обходились.

## 3 浏览器验证 Проверка браузером

```bash
.venv/bin/python -m http.server 8767 --bind 127.0.0.1 --directory site
```

通过 gstack `/browse` 自带 Chromium 访问回环站点，Aside 未安装。浏览器首次因本地端口绑定 EPERM 启动失败，取得本次执行授权后成功。只服务 site，没有接触生产系统或第三方登录。

Использован Chromium gstack `/browse` на loopback, Aside отсутствует. Первичная привязка порта завершилась EPERM; после разрешённого запуска браузер работает. Сервируется только site, без продакшена и сторонних аккаунтов.

| 检查 Проверка | 结果 Результат |
| --- | --- |
| 首页及四页 Главная и четыре страницы | HTTP 200，打开、快照、截图 / Открыты и сняты |
| 搜索 Поиск | SQLite 找到管理员手册 / Найдено руководство администратора |
| 下载 Скачивания | 登记页 9 个链接 HEAD 200 / 9 ссылок реестра HEAD 200 |
| 控制台 Консоль | 清空旧缓冲后本地检查无错误 / После очистки ошибок нет |
| 显示 Отображение | 五页桌面及 375px 首页无水平溢出 / Нет горизонтального переполнения |

41 条浏览器命令均退出 0。原始输出：artifacts/browser-verification.json；截图：artifacts/browser-index.png、browser-user-guide.png、browser-admin-guide.png、browser-release-notes.png、browser-document-register.png、browser-search.png、browser-mobile.png。截图均已查看。浏览脚本只调用 gstack browse CLI。

41 команда браузера завершилась с кодом 0. Вывод и снимки по указанным путям, все снимки просмотрены. Скрипт использует только gstack browse CLI.

## 4 Word 与边界 Word и границы

Word 共 12 页，与 Markdown 同源。ZIP、中俄段落对应检查和最终逐页查看通过。使用桌面提供的 Python、LibreOffice 和本任务 artifacts/fonts.conf；中文字体发现问题已修复。PDF/PNG 位于 artifacts/word-delivery，仅用于排版 QA；最终 Word 与站内下载副本一致。

Word: 12 страниц, общий источник с Markdown. ZIP, соответствие абзацев и просмотр всех страниц пройдены. Использованы встроенные Python/LibreOffice и artifacts/fonts.conf для китайских шрифтов. PDF/PNG в artifacts/word-delivery только для QA; Word и скачиваемая копия совпадают.

R10 后端安装、R11 TestClient、R12 合成恢复是前阶段引用，本轮未重新执行。应用安装启停、真实应用 HTTP、升级回滚、生产恢复和 38 个业务用例仍 NOT_RUN。本站成功不代表应用验收；教师原包、原始意见、团队复审和教师确认仍待补。

R10–R12 — прежние свидетельства, сейчас не повторялись. Установка/запуск приложения, его HTTP, обновление/откат, продакшен и 38 бизнес-кейсов NOT_RUN. Успех сайта не означает приёмку приложения; архив, замечания и подтверждение команды/преподавателя ожидаются.

## 5 官方依据 Официальные источники

2026-10-21 通过 gstack 读取官方说明：MyST 加入 extensions，Markdown 通过 toctree 登记；严格选项含义来自 Sphinx 命令文档。

21.10.2026 через gstack прочитаны официальные инструкции о MyST, toctree и строгих опциях Sphinx.

- [Sphinx sphinx-build 官方选项 Официальные опции](https://www.sphinx-doc.org/en/master/man/sphinx-build.html)
- [MyST 在 Sphinx 启用 Markdown Markdown в Sphinx](https://myst-parser.readthedocs.io/en/latest/intro.html)
