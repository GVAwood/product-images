=== GIGA → GitHub mirror & eCRATER bulk rewriter ===

Куда положить файл локально (рекомендуется):
  ~/Documents/product-images/tools/giga_mirror.py

Как запустить из корня репозитория:
  cd ~/Documents/product-images

  python3 tools/giga_mirror.py     --input ecrater_bulk_FROM_GIGA_clean.txt     --out   ecrater_bulk_FROM_GITHUB.txt     --repo-base https://raw.githubusercontent.com/GVAwood/product-images/main/giga_mirror     --root giga_mirror

После:
  - Появится папка 'giga_mirror' с подпапками item_XXXX_<slug>/01.jpg,02.jpg...
  - В файле ecrater_bulk_FROM_GITHUB.txt колонка image_url будет с RAW GitHub ссылками.

Дальше:
  git add giga_mirror ecrater_bulk_FROM_GITHUB.txt
  git commit -m "Mirror GIGA images and rewrite eCRATER bulk file to GitHub RAW"
  git push origin main
