"""Copy only approved public assets. Never publish Python, secrets or private data."""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
PUBLIC.mkdir(exist_ok=True)
assets = ['index.html','app.js','platform.js','learning.js','knowledge.js','market.js',
          'base.css','reference.css','print.css','调整.css','knowledge.css','market.css',
          'guangzhou-jobs.json','cloud.js']
for name in assets:
    shutil.copyfile(ROOT / name, PUBLIC / name)
p = PUBLIC / 'index.html'
html = p.read_text(encoding='utf-8')
html = html.replace('</body>', '<script src="cloud.js"></script></body>')
p.write_text(html, encoding='utf-8')

print("Public build: " + ", ".join(sorted(x.name for x in PUBLIC.iterdir())))
