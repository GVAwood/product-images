import csv, re
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
folders = sorted([p for p in repo.iterdir() if p.is_dir() and re.match(r'^\d{4}_YESWOOD_Furniture_Store$', p.name)])

out_path = repo / 'data' / '_images_manifest.tsv'
out_path.parent.mkdir(parents=True, exist_ok=True)

rows = []
for folder in folders:
    files = sorted([f for f in folder.iterdir() if f.is_file()])
    for f in files:
        name = f.name
        m = re.match(r'^(\d{2})', name)
        idx = int(m.group(1)) if m else ''
        url = f"https://raw.githubusercontent.com/GVAwood/product-images/main/{folder.name}/{name}"
        rows.append([folder.name, idx, name, url])

with out_path.open('w', newline='', encoding='utf-8') as tsv:
    w = csv.writer(tsv, delimiter='\t')
    w.writerow(['folder','image_index','filename','url'])
    w.writerows(rows)

print(f"Wrote: {out_path}  ({len(rows)} rows)")
