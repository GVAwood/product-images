import csv
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
src_path = repo / 'data' / 'ecrater_bulk_FROM_GIGA_clean.txt'
manifest_path = repo / 'data' / '_images_manifest.tsv'
out_path = repo / 'data' / 'ecrater_bulk_GITHUB_ready.txt'

# 1) читаем манифест: folder -> [urls... (по порядку)]
manifest = {}
with manifest_path.open('r', encoding='utf-8', newline='') as f:
    r = csv.DictReader(f, delimiter='\t')
    for row in r:
        folder = row['folder']
        url = row['url']
        manifest.setdefault(folder, []).append(url)

# 2) читаем исходный файл, заменяем колонку image_url (5-я)
rows_out = []
with src_path.open('r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f, delimiter='\t')
    rows = list(reader)

# заголовок как есть (если есть)
header = rows[0]
has_header = 'image_url' in header
start_idx = 1 if has_header else 0
if has_header:
    rows_out.append(header)

# построчно: i -> 000i_YESWOOD_Furniture_Store
for i, row in enumerate(rows[start_idx:], start=1):
    folder = f"{i:04d}_YESWOOD_Furniture_Store"
    urls = manifest.get(folder, [])
    url_str = ', '.join(urls)

    # гарантируем наличие хотя бы 5 колонок
    if len(row) < 5:
        row = row + ['']*(5 - len(row))

    row[4] = url_str  # image_url
    rows_out.append(row)

# 3) пишем результат
with out_path.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t', lineterminator='\n')
    w.writerows(rows_out)

print(f"OK: {out_path} | items: {len(rows_out) - (1 if has_header else 0)}")
