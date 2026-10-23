"""Keep downloadable copies byte-identical to the final local delivery."""
from pathlib import Path
import shutil
import hashlib

root=Path(__file__).resolve().parent
submission=root/'docs/materials/submission'
submission.mkdir(exist_ok=True)
files=[root/'StudySpace_管理员手册_中俄双语_v0.2.docx',root/'build-evidence.md',root/'review.md',
       root/'artifacts/source-manifest.json',root/'artifacts/sphinx-build.log']
for src in files:
    if not src.exists():continue
    targets=[submission/src.name]
    targets.extend((root/'site/_downloads').glob('*/'+src.name))
    for target in targets:
        shutil.copy2(src,target)
        assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest()
print('Final files and download payloads are identical')
