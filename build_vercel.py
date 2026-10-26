"""Copy only approved public assets. Never publish Python, secrets or private data."""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
PUBLIC.mkdir(exist_ok=True)
assets = ['index.html','app.js','platform.js','learning.js','knowledge.js','market.js',
          'base.css','reference.css','print.css','调整.css','knowledge.css','market.css',
          'guangzhou-jobs.json','cloud.js','cloud-library.js',
          'vendor/jszip.min.js','vendor/pdf.min.mjs','vendor/pdf.worker.min.mjs',
          'vendor/JSZip-LICENSE.md','vendor/PDFjs-LICENSE.txt']
for name in assets:
    (PUBLIC / name).parent.mkdir(parents=True, exist_ok=True)
    source = ROOT / name
    dependencies = {
        'vendor/jszip.min.js': 'jszip/dist/jszip.min.js',
        'vendor/pdf.min.mjs': 'pdfjs-dist/build/pdf.min.mjs',
        'vendor/pdf.worker.min.mjs': 'pdfjs-dist/build/pdf.worker.min.mjs',
        'vendor/JSZip-LICENSE.md': 'jszip/LICENSE.markdown',
        'vendor/PDFjs-LICENSE.txt': 'pdfjs-dist/LICENSE',
    }
    if name in dependencies:
        installed = ROOT / 'node_modules' / dependencies[name]
        if installed.exists():
            source = installed
    shutil.copyfile(source, PUBLIC / name)
p = PUBLIC / 'index.html'
html = p.read_text(encoding='utf-8')
html = html.replace('</body>', '<script src="cloud.js"></script><script src="cloud-library.js"></script></body>')
p.write_text(html, encoding='utf-8')

print("Public build: " + ", ".join(sorted(x.name for x in PUBLIC.iterdir())))
