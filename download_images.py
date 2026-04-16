"""
Beauty Salon KANSHA - Image Download Script
"""
import urllib.request
import os
import sys
import time

# Windows CP932 encoding fix
sys.stdout.reconfigure(encoding='utf-8')

img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(img_dir, exist_ok=True)

images = [
    ("cut.jpg",          "https://loremflickr.com/600/450/haircut,woman,hairstyle/all",    "cut"),
    ("color.jpg",        "https://loremflickr.com/600/450/haircolor,woman,salon/all",      "color"),
    ("bleach.jpg",       "https://loremflickr.com/600/450/blonde,hair,woman/all",          "bleach"),
    ("highlight.jpg",    "https://loremflickr.com/600/450/highlights,hair,woman/all",      "highlight"),
    ("perm.jpg",         "https://loremflickr.com/600/450/curly,hair,woman,wavy/all",      "perm"),
    ("digital-perm.jpg", "https://loremflickr.com/600/450/wavy,hair,woman,glossy/all",    "digital-perm"),
    ("treatment.jpg",    "https://loremflickr.com/600/450/shiny,hair,woman,long/all",      "treatment"),
    ("headspa.jpg",      "https://loremflickr.com/600/450/head,massage,spa/all",           "headspa"),
    ("kairyo.jpg",       "https://loremflickr.com/600/450/beauty,hair,salon,woman/all",    "kairyo"),
    ("blow.jpg",         "https://loremflickr.com/600/450/blowdry,hair,salon,woman/all",  "blow"),
    ("set.jpg",          "https://loremflickr.com/600/450/updo,hairstyle,woman,elegant/all","set"),
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

print("Downloading images...\n")
success = 0
fail = 0

for filename, url, label in images:
    save_path = os.path.join(img_dir, filename)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"  SKIP {label} ({filename}) - too small")
            fail += 1
            continue
        with open(save_path, "wb") as f:
            f.write(data)
        print(f"  OK   {label} ({filename}) - {len(data)//1024}KB saved")
        success += 1
    except Exception as e:
        print(f"  FAIL {label} ({filename}) - {e}")
        fail += 1
    time.sleep(0.8)

print(f"\nDone: {success} OK / {fail} failed")
print(f"Saved to: {img_dir}")
