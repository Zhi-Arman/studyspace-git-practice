# 代码重构与软件维护实践 / Практика рефакторинга и сопровождения ПО

日期 / Дата: 2026-10-20。课程答案文档版本 / Версия документа: 1.0，DRAFT。

本目录完成两张课堂图片中的四项任务。Word 和 Markdown 含逐项中俄答案；代码为独立课堂示例。 / В папке выполнены четыре задания с двух изображений. Word и Markdown содержат ответы на китайском и русском языках; код относится к отдельным учебным примерам.

文档第 3 节现为重构后的测试结果与修改说明，含两个用例的预期值和实际值、运行日志及六项修改对照。税额计算器 README 保存在独立文件中。 / Раздел 3 документа содержит результаты тестов после рефакторинга: ожидаемые и фактические значения двух случаев, журнал запуска и шесть пунктов изменений. README калькулятора сохранён отдельным файлом.

- [完整双语 Word / Полный двуязычный Word](代码重构与软件维护实践_中俄双语_v1.docx)
- [完整双语 Markdown / Полный двуязычный Markdown](代码重构与软件维护实践_中俄双语_v1.md)
- [原代码 / Исходный код](code/employees_original.py)
- [重构代码与 docstring / Рефакторинг и docstring](code/employees_refactored.py)
- [两个测试 / Два теста](code/test_employees.py)
- [税额计算器 README / README калькулятора](tax-calculator/README.md)
- [可运行计算器 / Программа](tax-calculator/tax_calculator.py)
- [验证记录 / Результаты проверки](artifacts/verification.json)

## 图片要求覆盖 / Покрытие условий

| 来源 / Источник | 要求 / Требование | 完成位置 / Выполнение |
| --- | --- | --- |
| 图片 1 / Изображение 1 | 五项元组、f/g 原逻辑 / Пять полей, исходные f/g | code/employees_original.py；文档第 1 节 / раздел 1 |
| 图片 2 任务 1 / Задание 1 | 清晰命名、DRY、docstring / Имена, DRY, docstring | code/employees_refactored.py；第 1 节 / раздел 1 |
| 图片 2 任务 2 / Задание 2 | 测试理由与两个测试 / Обоснование и два теста | code/test_employees.py；第 2 节 / раздел 2 |
| 图片 2 任务 3 / Задание 3 | README 五个栏目 / Пять разделов README | tax-calculator/README.md |
| 图片 2 任务 4 / Задание 4 | 从 1.4.2 判断三项改动 / Три изменения от 1.4.2 | 第 4 节 / раздел 4：1.4.3、1.5.0、2.0.0 |

## 运行 / Запуск

在本目录执行 / Из этой папки:

```bash
cd code
EMPLOYEE_MODULE=employees_original python3 -m unittest -v test_employees.py
python3 -m unittest -v test_employees.py
cd ../tax-calculator
python3 -m unittest -v test_tax_calculator.py
python3 tax_calculator.py --amount 10000 --rate 13
```

已实际执行：原代码 2/2、重构代码 2/2、计算器 4/4；日志保存在 artifacts。计算器使用用户提供的百分比，13% 仅是教学示例。 / Выполнено: исходный код 2/2, изменённый код 2/2, калькулятор 4/4. Журналы находятся в artifacts. Ставку задаёт пользователь; 13% — учебный пример.

## 文档重建 / Пересборка документа

work/content.json 为要求清单，work/build_report.py 同时生成 Markdown 和 Word。渲染使用随工作区提供的 Python 和 render_docx.py，并设置 FONTCONFIG_FILE 指向 work/fonts.conf。 / work/content.json содержит перечень требований; work/build_report.py создаёт Markdown и Word из одного источника. Для визуальной проверки используются Python и render_docx.py из среды рабочего пространства с FONTCONFIG_FILE, указывающим на work/fonts.conf.

版本规则核对来源 / Источник правил версий：[Semantic Versioning 2.0.0](https://semver.org/lang/zh-CN/)。
