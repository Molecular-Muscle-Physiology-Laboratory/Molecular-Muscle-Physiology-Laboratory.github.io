"""
Compress all images in img/otl/ for the MMP Lab website.
Reduces 3-8MB phone photos down to ~200-400KB while keeping them looking great.

HOW TO USE:
1. Make sure Python is installed (python.org)
2. Open a terminal/command prompt
3. Install Pillow: pip install Pillow
4. Navigate to your repo folder (where index.html is): cd path/to/repo
5. Run: python compress_images.py

The script will compress all photos in img/otl/ in place.
A backup of each original is saved to img/otl/_originals/ just in case.
"""

from PIL import Image, ImageOps
from pathlib import Path
import shutil

# ── CONFIG ────────────────────────────────────────
OTL_DIR = Path("img/otl")
BACKUP_DIR = OTL_DIR / "_originals"
MAX_WIDTH = 1400     # plenty for web display at 300px card height even on retina screens
JPEG_QUALITY = 82    # sweet spot: great visual quality, big size savings
# ──────────────────────────────────────────────────

if not OTL_DIR.exists():
    print(f"ERROR: {OTL_DIR} not found. Run this from the folder containing 'img/'")
    exit(1)

BACKUP_DIR.mkdir(exist_ok=True)

# Find all images (skip the backup folder)
exts = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
images = [f for f in OTL_DIR.iterdir()
          if f.is_file() and f.suffix in exts and f.parent.name != '_originals']

print(f"Found {len(images)} images to compress\n")

total_before = 0
total_after = 0

for i, img_path in enumerate(images, 1):
    try:
        size_before = img_path.stat().st_size

        # Backup original if not already backed up
        backup_path = BACKUP_DIR / img_path.name
        if not backup_path.exists():
            shutil.copy2(img_path, backup_path)

        # Open and auto-rotate based on EXIF orientation
        img = Image.open(img_path)
        img = ImageOps.exif_transpose(img)

        # Convert to RGB if needed (strips alpha for JPEG)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if wider than MAX_WIDTH
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_h = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)

        # Save as JPEG (overwrite original)
        # If original was .png, we keep the extension but write JPEG bytes — works fine
        # But it's cleaner to save all as .jpg. We'll keep the existing extension to avoid breaking references.
        img.save(img_path, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)

        size_after = img_path.stat().st_size
        total_before += size_before
        total_after += size_after

        pct = (1 - size_after / size_before) * 100
        print(f"[{i}/{len(images)}] {img_path.name:60s} "
              f"{size_before/1024:>6.0f}KB → {size_after/1024:>5.0f}KB  (-{pct:.0f}%)")

    except Exception as e:
        print(f"[{i}/{len(images)}] FAILED: {img_path.name} — {e}")

print(f"\n{'='*70}")
print(f"Total: {total_before/1024/1024:.1f}MB → {total_after/1024/1024:.1f}MB "
      f"({(1-total_after/total_before)*100:.0f}% smaller)")
print(f"Originals backed up to: {BACKUP_DIR}")
print(f"Done.")
