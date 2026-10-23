# StudySpace Sphinx 文档交付

Документация StudySpace на Sphinx

实践 3.4.4 第 4 部分 · v0.2 · DRAFT · 2026-10-21 · Asia/Shanghai

本目录按五张图完成本地文档项目：九章管理员手册、六字段流程卡、安全要求、Sphinx 严格构建与完整提交结构。教师起始包未提供，使用既有学习材料在此独立重建，未冒充原包。应用业务状态仍为 NOT_RUN。

Локальный проект по пяти фото: девять глав администратора, шесть полей процедур, безопасность, строгая сборка Sphinx и структура сдачи. Архив преподавателя отсутствует; проект отдельно создан из имеющихся материалов, без заявления об оригинальности. Бизнес-кейсы приложения остаются NOT_RUN.

## 文件入口 Файлы

- [网站首页 Главная](site/index.html)
- [管理员手册 Markdown Руководство Markdown](docs/admin-guide.md)
- [管理员手册 Word Руководство Word](StudySpace_管理员手册_中俄双语_v0.2.docx)
- [用户指南 Руководство пользователя](docs/user-guide.md)
- [发布说明 Примечания](docs/release-notes.md)
- [文档登记 Реестр](docs/document-register.md)
- [构建证据 Свидетельства сборки](build-evidence.md)
- [逐图要求与自查 Требования по фото и проверка](review.md)

## 文件结构 Структура

```text
project-docs/
├── requirements-docs.txt      # 完整依赖锁 с хешами
├── requirements-docs.in       # 直接依赖 прямые зависимости
├── docs/
│   ├── conf.py
│   ├── index.md
│   ├── user-guide.md
│   ├── admin-guide.md
│   ├── release-notes.md
│   ├── document-register.md
│   ├── images/
│   ├── _static/
│   └── materials/            # 原材料目录层级 исходная иерархия
├── build-evidence.md
├── review.md
├── build-site.sh
├── verify.py
├── StudySpace_管理员手册_中俄双语_v0.2.docx
├── artifacts/                # 日志和检查 журналы и проверки
├── .venv/                    # 独立环境 отдельная среда
└── site/
    └── index.html
```

## 从本目录构建 Сборка из этого каталога

先在终端进入本 README 所在的 project-docs，以下均为相对路径。运行应用手册里的命令时另按手册进入父学习包；两者虚拟环境不同。

В терминале перейти в project-docs, где находится этот README. Ниже относительные пути. Для операций приложения использовать корень учебного пакета, указанный в руководстве; это другая виртуальная среда.

```bash
UV_CACHE_DIR="$PWD/artifacts/uv-cache" uv venv --python 3.13 --no-python-downloads .venv
UV_CACHE_DIR="$PWD/artifacts/uv-cache" uv pip sync --python .venv/bin/python \
  --require-hashes requirements-docs.txt
UV_CACHE_DIR="$PWD/artifacts/uv-cache" uv pip check --python .venv/bin/python
bash build-site.sh
.venv/bin/python verify.py
```

已有环境可直接运行后两条。严格构建启用 `-n -W --keep-going -E -a`，警告写入 artifacts/sphinx-warnings.log。依赖锁固定 Sphinx 8.2.3、MyST 4.0.1 及传递依赖，不要求全局安装。

С готовой средой достаточно двух последних команд. Строгая сборка использует `-n -W --keep-going -E -a`; предупреждения в artifacts/sphinx-warnings.log. Зафиксированы Sphinx 8.2.3, MyST 4.0.1 и транзитивные зависимости, глобальная установка не нужна.

## 本地查看 Локальный просмотр

可直接打开 site/index.html。完整搜索建议使用本地 HTTP，终端运行后打开显示的回环地址，用 Ctrl+C 停止：

Можно открыть site/index.html. Для поиска рекомендуется локальный HTTP; запустить и открыть loopback-адрес, остановить Ctrl+C:

```bash
.venv/bin/python -m http.server 8767 --bind 127.0.0.1 --directory site
```

仅服务 site 目录；不把学习包根目录、.env 或内部配置发布到互联网。端口占用时选择空闲端口，不终止其他项目的进程。

Сервировать только site. Не публиковать корень учебного пакета, .env или внутренние настройки в интернете. При занятом порте выбрать свободный, не завершать чужие процессы.

## 第五部分专项检查 Часть 5 Специальная проверка

后续新图要求的逐页点击、至少五处链接或跳转、图片和标题、可读性、错误修复及复测，已单独完成并保存为 [第 5 部分检查报告及原始证据](../../09-site-build-check/README.md)。本轮检查没有修改本站 docs 源码，应用命令未执行。

Переходы по всем страницам, минимум пять ссылок, изображение и заголовок, читаемость, ошибки и повторная проверка нового фото выполнены отдельно; см. [часть 5 и исходные свидетельства](../../09-site-build-check/README.md). Исходники docs сохранены, команды приложения не выполнялись.
