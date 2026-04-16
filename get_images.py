"""
美容室KANSHAホームページ用 画像取得スクリプト
1st: Openverse (CC0 著作権フリー写真)
2nd: AI Horde (Stable Diffusion / 完全無料AIイラスト生成)
"""
import urllib.request
import urllib.parse
import urllib.error
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(IMG_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

# ─────────────────────────────────────
# 各メニューの設定
# queries: Openverse 検索ワード（複数試す）
# horde_prompt: AI Horde 生成プロンプト（Openverse失敗時）
# ─────────────────────────────────────
MENU = [
    {
        "file": "cut.jpg",
        "label": "カット",
        "queries": ["woman haircut beauty salon side profile", "stylish bob haircut woman", "hair salon haircut woman"],
        "horde_prompt": "elegant woman with stylish bob haircut, side view, hair salon, professional photo, soft light, white background"
    },
    {
        "file": "color.jpg",
        "label": "カラー",
        "queries": ["hair color salon woman long hair", "hair coloring woman salon", "brown hair color woman beauty"],
        "horde_prompt": "beautiful woman with long glossy brown hair color, warm tone, hair salon professional photo, soft lighting"
    },
    {
        "file": "bleach.jpg",
        "label": "ケアブリーチ",
        "queries": ["blonde hair woman salon bleach", "bleached blonde hair woman", "blonde hair color woman"],
        "horde_prompt": "beautiful woman with bright blonde bleached hair, salon photo, professional, soft warm light"
    },
    {
        "file": "highlight.jpg",
        "label": "ハイライト",
        "queries": ["hair highlights woman salon", "balayage hair highlights woman", "highlighted hair woman"],
        "horde_prompt": "woman with elegant hair highlights balayage, dimensional color, salon photo, natural light"
    },
    {
        "file": "perm.jpg",
        "label": "パーマ",
        "queries": ["curly wavy perm hair woman salon", "wavy perm hairstyle woman", "airy perm hair woman"],
        "horde_prompt": "woman with soft airy wavy perm, shoulder length, fluffy romantic curls, hair salon photo, feminine"
    },
    {
        "file": "digital-perm.jpg",
        "label": "デジタルパーマ",
        "queries": ["digital perm wavy hair woman", "glossy wave hair woman salon", "curly glossy hair woman"],
        "horde_prompt": "woman with digital perm glossy voluminous waves, medium length hair, elegant salon photo"
    },
    {
        "file": "treatment.jpg",
        "label": "トリートメント",
        "queries": ["shiny long hair woman beautiful", "silky smooth long hair woman", "healthy glossy hair woman"],
        "horde_prompt": "beautiful woman with long lustrous shiny silky hair flowing, hair treatment result, salon photo, elegant"
    },
    {
        "file": "headspa.jpg",
        "label": "ヘッドスパ",
        "queries": ["head massage spa salon woman", "scalp massage salon", "head spa hair treatment woman"],
        "horde_prompt": "woman receiving head spa scalp massage treatment at hair salon, relaxing, serene atmosphere, professional"
    },
    {
        "file": "kairyo.jpg",
        "label": "髪質改善",
        "queries": ["healthy hair salon woman beautiful", "hair care treatment woman", "smooth glossy hair woman salon"],
        "horde_prompt": "beautiful woman with healthy glossy smooth hair, hair quality improvement result, salon photo, elegant"
    },
    {
        "file": "blow.jpg",
        "label": "シャンプーブロー",
        "queries": ["blow dry hair salon woman", "blowout hair woman salon", "hair dryer salon woman"],
        "horde_prompt": "woman with beautiful blowout hairstyle, professional salon finishing, elegant, soft warm light"
    },
    {
        "file": "set.jpg",
        "label": "セット",
        "queries": ["updo hairstyle elegant woman", "hair set elegant updo salon", "elegant chignon woman hair"],
        "horde_prompt": "elegant woman with beautiful updo hairstyle, special occasion hair set, salon styling, sophisticated"
    },
]

# ─────────────────────────────────────
# Openverse API 検索・ダウンロード
# ─────────────────────────────────────
def search_openverse(query):
    params = urllib.parse.urlencode({
        "q": query,
        "license": "cc0",
        "page_size": 5,
        "format": "json"
    })
    url = f"https://api.openverse.org/v1/images/?{params}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        # 横長より縦長・正方形を優先（ポートレート向き）
        for r in results:
            w = r.get("width", 0)
            h = r.get("height", 0)
            if h >= w * 0.6 and r.get("url"):
                return r["url"]
        if results and results[0].get("url"):
            return results[0]["url"]
    except Exception as e:
        print(f"    Openverse error: {e}")
    return None

def download_url(url, save_path):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if len(data) < 8000:
            return False
        with open(save_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    Download error: {e}")
        return False

# ─────────────────────────────────────
# AI Horde 生成（Stable Diffusion / 完全無料）
# ─────────────────────────────────────
HORDE_ANON_KEY = "0000000000"
HORDE_API = "https://aihorde.net/api/v2"

def generate_horde(prompt, save_path):
    print(f"    AI Horde で生成中（匿名キー・無料・数分かかる場合があります）...")
    payload = json.dumps({
        "prompt": prompt + ", high quality, professional photography",
        "params": {
            "width": 512,
            "height": 512,
            "steps": 25,
            "sampler_name": "k_euler_a",
            "cfg_scale": 7
        },
        "models": ["Deliberate"],
        "r2": False
    }).encode()

    req = urllib.request.Request(
        f"{HORDE_API}/generate/async",
        data=payload,
        headers={**HEADERS, "apikey": HORDE_ANON_KEY, "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        job_id = result.get("id")
        if not job_id:
            print(f"    AI Horde: ジョブID取得失敗 {result}")
            return False
        print(f"    ジョブID: {job_id} ポーリング中...")

        # 最大5分待つ
        for i in range(60):
            time.sleep(5)
            check_req = urllib.request.Request(
                f"{HORDE_API}/generate/check/{job_id}",
                headers={**HEADERS, "apikey": HORDE_ANON_KEY}
            )
            with urllib.request.urlopen(check_req, timeout=15) as cr:
                check = json.loads(cr.read())
            done = check.get("done", False)
            queue = check.get("queue_position", "?")
            print(f"    待機中... キュー位置:{queue} ({(i+1)*5}秒経過)")
            if done:
                break
        else:
            print("    タイムアウト")
            return False

        status_req = urllib.request.Request(
            f"{HORDE_API}/generate/status/{job_id}",
            headers={**HEADERS, "apikey": HORDE_ANON_KEY}
        )
        with urllib.request.urlopen(status_req, timeout=15) as sr:
            status = json.loads(sr.read())

        generations = status.get("generations", [])
        if not generations:
            print("    画像データなし")
            return False

        img_url = generations[0].get("img")
        if not img_url:
            return False

        # base64 の場合
        if img_url.startswith("data:image"):
            import base64
            b64 = img_url.split(",", 1)[1]
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(b64))
            return True
        else:
            return download_url(img_url, save_path)

    except Exception as e:
        print(f"    AI Horde error: {e}")
        return False

# ─────────────────────────────────────
# メイン処理
# ─────────────────────────────────────
print("=" * 50)
print("画像取得開始")
print("=" * 50)

success = 0
fail = 0
horde_queue = []  # Openverse失敗分をまとめてHordeへ

for item in MENU:
    save_path = os.path.join(IMG_DIR, item["file"])
    print(f"\n[{item['label']}] {item['file']}")

    # --- Step1: Openverse ---
    found = False
    for q in item["queries"]:
        print(f"  Openverse検索: {q}")
        img_url = search_openverse(q)
        if img_url:
            print(f"  URL取得: {img_url[:80]}...")
            ok = download_url(img_url, save_path)
            if ok:
                size = os.path.getsize(save_path) // 1024
                print(f"  OK  Openverse ({size}KB)")
                success += 1
                found = True
                break
        time.sleep(0.5)

    if not found:
        print(f"  Openverse失敗 → AI Horde キューに追加")
        horde_queue.append(item)

print("\n" + "=" * 50)
print(f"Openverse完了: {success}件成功 / {len(horde_queue)}件をAI Hordeへ")
print("=" * 50)

# --- Step2: AI Horde（失敗分のみ）---
for item in horde_queue:
    save_path = os.path.join(IMG_DIR, item["file"])
    print(f"\n[{item['label']}] AI Horde生成...")
    ok = generate_horde(item["horde_prompt"], save_path)
    if ok:
        size = os.path.getsize(save_path) // 1024 if os.path.exists(save_path) else 0
        print(f"  OK  AI Horde ({size}KB)")
        success += 1
    else:
        print(f"  FAIL {item['label']}")
        fail += 1

print("\n" + "=" * 50)
print(f"全完了: 成功{success}件 / 失敗{fail}件")
print(f"保存先: {IMG_DIR}")
print("=" * 50)
