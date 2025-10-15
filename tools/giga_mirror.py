#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
giga_mirror.py — mirror GIGA image URLs and rewrite eCRATER bulk file to GitHub RAW.

Usage example:
  python3 giga_mirror.py \
    --input ecrater_bulk_FROM_GIGA_clean.txt \
    --out   ecrater_bulk_FROM_GITHUB.txt \
    --repo-base https://raw.githubusercontent.com/GVAwood/product-images/main/giga_mirror \
    --root giga_mirror
"""
import argparse, csv, os, re, sys, time, urllib.request
from pathlib import Path

def slugify(text: str, max_len: int = 50) -> str:
    text = re.sub(r"\s+", " ", text, flags=re.S).strip().lower()
    text = re.sub(r"[^a-z0-9\- _]+", "", text)
    text = text.replace(" ", "-")
    text = re.sub(r"-{2,}", "-", text).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text or "item"

def split_urls(field: str):
    return [u.strip() for u in field.split(",")] if field else []

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def ext_from_url(url: str) -> str:
    m = re.search(r"\.([a-zA-Z0-9]{3,4})(?:$|\?)", url)
    return ("." + m.group(1).lower()) if m else ".jpg"

def download(url: str, dest: Path, retries: int = 3, timeout: int = 30):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            return
        except Exception as e:
            last = e
            time.sleep(1.5 * (i+1))
    raise last

def process_row_images(row_idx: int, title: str, image_field: str, root: Path):
    slug = slugify(title or f"item_{row_idx:04d}")
    rel_folder = f"item_{row_idx:04d}_{slug}"
    folder = root / rel_folder
    ensure_dir(folder)

    urls = [u for u in split_urls(image_field) if u]
    local_rel_paths = []
    for i, url in enumerate(urls, start=1):
        ext = ext_from_url(url)
        name = f"{i:02d}{ext}"
        dest = folder / name
        if not dest.exists():
            try:
                download(url, dest)
            except Exception as e:
                print(f"[WARN] row {row_idx}: failed to download {url}: {e}", file=sys.stderr)
                continue
        local_rel_paths.append(str(Path(rel_folder) / name))
    return local_rel_paths

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--repo-base", required=True)
    ap.add_argument("--root", default="giga_mirror")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    inp, outp, root = Path(a.input), Path(a.out), Path(a.root)
    ensure_dir(root)

    with open(inp, "r", encoding="utf-8", newline="") as fin:
        reader = csv.reader(fin, dialect=csv.excel_tab)
        rows = list(reader)

    if not rows:
        print("Empty input", file=sys.stderr); sys.exit(2)

    header = rows[0]
    try:
        i_title = header.index("title")
        i_img = header.index("image_url")
    except ValueError:
        print("Header must contain 'title' and 'image_url'", file=sys.stderr); sys.exit(2)

    out_rows = [header]
    for idx, row in enumerate(rows[1:], start=2):
        if len(row) < len(header): row += [""] * (len(header)-len(row))
        if len(row) > len(header): row = row[:len(header)]
        title, img_field = row[i_title], row[i_img]
        if a.dry_run:
            slug = slugify(title or f"row_{idx}")
            urls = [u for u in split_urls(img_field) if u]
            gh_urls = [f"{a.repo_base}/item_{idx:04d}_{slug}/{n:02d}{ext_from_url(u)}" for n,u in enumerate(urls, start=1)]
        else:
            rels = process_row_images(idx, title, img_field, root)
            gh_urls = [f"{a.repo_base}/{p.replace(os.sep,'/')}" for p in rels]
        row[i_img] = ", ".join(gh_urls)
        out_rows.append(row)

    with open(outp, "w", encoding="utf-8", newline="") as fout:
        csv.writer(fout, dialect=csv.excel_tab).writerows(out_rows)
    print("OK")

if __name__ == "__main__":
    main()
