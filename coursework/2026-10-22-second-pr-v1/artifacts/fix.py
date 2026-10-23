from workflow import *

I = json.loads((ART / 'initial.json').read_text())
review = json.loads((ART / 'review-posted.json').read_text())
assert review['state'] == 'COMMENTED' and review['commit_id'] == I['head']
assert run(['git', 'rev-parse', 'HEAD']) == I['head']
assert run(['git', 'status', '--porcelain=v1']) == ''
p = B / 'docs/index.md'
old = p.read_text()
correction = '''请另行扫描所有受 Git 跟踪的 Markdown 文件，检查已提交内容中的冲突标记。下列命令返回 1 表示无匹配、检查通过；返回 0 表示发现标记，应停止并处理；大于 1 表示命令错误，不能视为通过。

Отдельно проверьте все Markdown-файлы под контролем Git на маркеры, в том числе в уже закоммиченном тексте. Для команды ниже код 1 означает отсутствие совпадений и успешную проверку; код 0 означает найденные маркеры — остановитесь и исправьте их; код больше 1 означает ошибку команды, а не успешную проверку.

```bash
git grep -n -E '^(<{7}|={7}|>{7})( |$)' -- '*.md'
```

'''
assert '## 4 用户指南' in old and correction not in old
p.write_text(old.replace('## 4 用户指南', correction + '## 4 用户指南'))
validation = validate('corrected')
assert 'Markdown-файлы' in (B / 'site/index.html').read_text()
(ART / 'correction.diff').write_text(run(['git', 'diff', '--', 'docs/index.md']) + '\n')
assert run(['git', 'diff', '--name-only']) == 'docs/index.md'
run(['git', 'add', '--', 'docs/index.md'])
run(['git', 'commit', '-m', 'docs: add explicit marker scan requested in review'])
head = run(['git', 'rev-parse', 'HEAD'])
assert run(['git', 'rev-list', '--count', I['head'] + '..HEAD']) == '1'
assert run(['git', 'status', '--porcelain=v1']) == ''
save('correction.json', dict(head=head, parent=I['head'], review_id=review['id'],
     changed_files=['docs/index.md'], correction_count=1, validation=validation))
print(head)
