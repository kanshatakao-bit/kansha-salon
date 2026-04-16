"""
残り6枚: キーワード変更 + ライセンス拡張 + HuggingFace Spaces fallback
"""
import urllib.request, urllib.parse, urllib.error
import json, os, sys, time, base64

sys.stdout.reconfigure(encoding='utf-8')
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

REMAINING = [
    {
        "file": "perm.jpg",
        "label": "パーマ",
        "queries": ["curly hair woman portrait", "wavy hair woman beautiful", "afro curly woman hair"],
    },
    {
        "file": "digital-perm.jpg",
        "label": "デジタルパーマ",
        "queries": ["wavy hair woman portrait", "long wavy hair woman", "wave hairstyle woman"],
    },
    {
        "file": "treatment.jpg",
        "label": "トリートメント",
        "queries": ["long hair woman beautiful portrait", "woman hair flowing beautiful", "beautiful hair woman portrait"],
    },
    {
        "file": "headspa.jpg",
        "label": "ヘッドスパ",
        "queries": ["head massage woman spa", "scalp massage therapy", "massage relaxation woman"],
    },
    {
        "file": "blow.jpg",
        "label": "シャンプーブロー",
        "queries": ["hair dryer woman", "blow dry hairstyle woman", "hair styling woman salon"],
    },
    {
        "file": "set.jpg",
        "label": "セット",
        "queries": ["elegant updo woman hair", "chignon hairstyle woman", "formal hairstyle woman wedding"],
    },
]

def search_openverse(query, license_type=None):
    params = {"q": query, "page_size": 8, "format": "json"}
    if license_type:
        params["license"] = license_type
    url = f"https://api.openverse.org/v1/images/?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        # 縦長 or 正方形を優先
        for r in results:
            w = r.get("width", 1)
            h = r.get("height", 1)
            if h >= w * 0.75 and r.get("url"):
                return r["url"]
        for r in results:
            if r.get("url"):
                return r["url"]
    except Exception as e:
        print(f"    Openverse err: {e}")
    return None

def download_url(url, save_path):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if len(data) < 8000:
            return False
        with open(save_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    DL err: {e}")
        return False

def try_hf_space(prompt, save_path):
    """HuggingFace Spaces の公開 API を試す"""
    # Gradio API 形式 - いくつかのモデルを試す
    endpoints = [
        ("https://hysts-anime-face-detector.hf.space/run/predict", None),  # dummy
        # stabilityai/sdxl-turbo space
        ("https://stabilityai-sdxl-turbo.hf.space/run/predict",
         {"data": [prompt, 0.0, True]}),
    ]
    # Hugging Face Inference API (anonymous, may work with limits)
    hf_models = [
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4",
    ]
    for model in hf_models:
        url = f"https://api-inference.huggingface.co/models/{model}"
        payload = json.dumps({"inputs": prompt}).encode()
        try:
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            })
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            # 画像バイナリが返ってくる
            if len(data) > 5000 and data[:4] in [b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\x89PNG']:
                with open(save_path, "wb") as f:
                    f.write(data)
                print(f"    HuggingFace ({model}) OK")
                return True
        except urllib.error.HTTPError as e:
            print(f"    HF {model}: HTTP {e.code}")
        except Exception as e:
            print(f"    HF {model}: {e}")
        time.sleep(2)
    return False

# ─── メイン ───
print("残り6枚 画像取得開始\n")
success = 0

for item in REMAINING:
    save_path = os.path.join(IMG_DIR, item["file"])
    print(f"[{item['label']}]")
    found = False

    # Openverse (CC0 のみ)
    for q in item["queries"]:
        for lic in ["cc0", None]:
            print(f"  Openverse({'CC0' if lic else '全ライセンス'}): {q}")
            url = search_openverse(q, lic)
            if url:
                ok = download_url(url, save_path)
                if ok:
                    print(f"  OK ({os.path.getsize(save_path)//1024}KB)")
                    success += 1
                    found = True
                    break
        if found:
            break
        time.sleep(0.4)

    if not found:
        print(f"  HuggingFace Inference API 試行...")
        prompt = item["queries"][0] + ", professional photo, high quality"
        ok = try_hf_space(prompt, save_path)
        if ok:
            success += 1
            found = True

    if not found:
        print(f"  FAIL - グラデーション表示のままにします")

print(f"\n完了: {success}件成功")
