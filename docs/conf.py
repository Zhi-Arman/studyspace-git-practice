project = "StudySpace Git Practice"
author = "StudySpace"
copyright = "2026 StudySpace"
release = "1.0"
extensions = ["myst_parser"]
source_suffix = {".md": "markdown"}
root_doc = "index"
language = "zh_CN"
exclude_patterns = [
    "build-check.md", "README.md", "zh-CN/**", "ru-RU/**", "decisions/**",
    "requirements-register.md", "traceability-matrix.md",
]
html_theme = "alabaster"
html_title = "StudySpace Git 协作练习 / Практика Git"
nitpicky = True
