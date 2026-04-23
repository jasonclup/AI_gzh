"""Generate 糖渍 video V4: upload original six-view front image to Chinese image host,
then use it for true character-consistent image-to-video."""

import json
import sys
import os
import base64 as _b64
import importlib.util

# ---------------------------------------------------------------------------
# Import buddy-cloud module
# ---------------------------------------------------------------------------
SCRIPT_PATH = r"C:\Users\v_junshshi\AppData\Local\Programs\WorkBuddy\resources\app.asar.unpacked\resources\builtin-skills\buddy-multimodal-generation\scripts"
spec = importlib.util.spec_from_file_location("bc", os.path.join(SCRIPT_PATH, "buddy-cloud.py"))
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)

TOKEN = sys.argv[1] if len(sys.argv) > 1 else "tk_Bk6qgr9Q8TeHqnHD9RVWHtaMX6ATWQuk"

# ---------------------------------------------------------------------------
# Step 1: Upload original 糖渍 front-view image to a China-accessible image host
# ---------------------------------------------------------------------------

LOCAL_IMAGE_PATH = r"c:\Users\v_junshshi\WorkBuddy\Claw\douyin-project\cell_0_0.png"


def upload_to_smms(filepath: str) -> str:
    """Upload image to SM.MS v2 (Chinese image hosting). Returns URL."""
    print(f"[INFO] Uploading to SM.MS...", file=sys.stderr)
    with open(filepath, "rb") as f:
        resp = bc.requests.post(
            "https://smms.app/api/v2/upload",
            files={"smfile": (os.path.basename(filepath), f.read(), "image/png")},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=30,
        )
    result = resp.json()
    if result.get("success"):
        url = result.get("data", {}).get("url")
        if url:
            print(f"[INFO] SM.MS OK: {url}", file=sys.stderr)
            return url
    raise RuntimeError(f"SM.MS failed: {result.get('message', result)}")


def upload_to_imgbb(filepath: str) -> str:
    """Upload to imgbb.com (free, no key needed via anonymous form). Returns URL."""
    print(f"[INFO] Trying imgbb fallback...", file=sys.stderr)
    import urllib.parse
    with open(filepath, "rb") as f:
        img_data = f.read()
    # imgbb API v1: POST to https://api.imgbb.com/1/upload with base64 payload
    b64 = _b64.b64encode(img_data).decode()
    resp = bc.requests.post(
        "https://api.imgbb.com/1/upload",
        data={"image": b64, "key": "c6b0cfda229219d315e038f4fe8c6d5f"},
        timeout=60,
    )
    result = resp.json()
    if result.get("success"):
        url = result["data"].get("url")
        if url:
            print(f"[INFO] ImgBB OK: {url}", file=sys.stderr)
            return url
    raise RuntimeError(f"ImgBB failed: {result.get('error', result)}")


def upload_to_litterbox(filepath: str) -> str:
    """Upload to litterbox.catbox.moe (no expiry). Returns URL."""
    print(f"[INFO] Trying litterbox (catbox)...", file=sys.stderr)
    with open(filepath, "rb") as f:
        resp = bc.requests.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data={
                "reqtype": "fileupload",
                "time": "72h",  # 72 hours
            },
            files={"fileToUpload": (os.path.basename(filepath), f.read(), "image/png")},
            timeout=120,
        )
    url = resp.text.strip()
    if url.startswith("http"):
        print(f"[INFO] Litterbox OK: {url}", file=sys.stderr)
        return url
    raise RuntimeError(f"Litterbox failed: {resp.text[:200]}")


def upload_to_0x0(filepath: str) -> str:
    """Upload to 0x0.st (null pointer / file sharing). Returns URL."""
    print(f"[INFO] Trying 0x0.st...", file=sys.stderr)
    with open(filepath, "rb") as f:
        resp = bc.requests.put(
            "https://0x0.st",
            data=f,
            headers={
                "User-Agent": "curl/8.0",
                "Content-Type": "application/octet-stream",
            },
            timeout=120,
        )
    url = resp.text.strip()
    if url.startswith("http"):
        print(f"[INFO] 0x0.st OK: {url}", file=sys.stderr)
        return url
    raise RuntimeError(f"0x0.st failed: {resp.text[:200]}")


# Try multiple image hosts in order of preference
IMAGE_URL = None
for uploader in [upload_to_smms, upload_to_imgbb, upload_to_0x0, upload_to_litterbox]:
    try:
        IMAGE_URL = uploader(LOCAL_IMAGE_PATH)
        break
    except Exception as e:
        print(f"[WARN] {uploader.__name__} failed: {e}", file=sys.stderr)
        continue

if not IMAGE_URL:
    print(json.dumps({"error": "UPLOAD_FAILED", "message": "All image hosts failed"}, ensure_ascii=False))
    sys.exit(1)

# ---------------------------------------------------------------------------
# Step 2: Submit image-to-video job with ORIGINAL character reference
# ---------------------------------------------------------------------------

cfg = bc._PROVIDER_MAP["video"]

body = {
    "Vendor": "Kling",
    "Model": "v2.6",
    # Prompt optimized for action description (character look comes from Image param)
    "Prompt": (
        "This cute cream-orange tabby cat wearing a white baseball cap and red triangular bandana scarf "
        "with green zongzi embroidery yawns widely showing its pink tongue and tiny teeth. "
        "Then it slowly lies down on its belly and curls into a cozy sleeping ball. "
        "While sleeping peacefully, small transparent soap bubbles float up one by one "
        "from its cute pink nose. Soft warm lighting, gentle and dreamy atmosphere."
    ),
    "ModelParam": json.dumps({
        "Duration": 10,
        "AspectRatio": "9:16",
        "Image": IMAGE_URL,
        "Sound": "off",
    }),
    "LogoAdd": 0,
}

print(f"\n[INFO] Submitting 糖渍 V4 image-to-video (original six-view reference)...", file=sys.stderr)
print(f"[INFO] Reference image: {IMAGE_URL[:80]}...", file=sys.stderr)

resp = bc._call_api(
    bc._DEFAULT_ENDPOINT, cfg["provider"], cfg["service"], cfg["version"],
    cfg["submit_action"], body, TOKEN,
)

job_id = resp.get("JobId")
if not job_id:
    print(json.dumps(resp, ensure_ascii=False, indent=2))
    sys.exit(1)

print(f"[INFO] Job submitted: {job_id}", file=sys.stderr)

# ---------------------------------------------------------------------------
# Step 3: Poll for completion & download
# ---------------------------------------------------------------------------

result = bc._poll_job(
    bc._DEFAULT_ENDPOINT, cfg["provider"], cfg["service"], cfg["version"],
    cfg["query_action"], job_id, TOKEN, 5, 600,
)

output = bc._format_output(result, job_id=job_id)
print(json.dumps(output, ensure_ascii=False, indent=2))

# Auto-download if result_url present
if "result_url" in output:
    video_url = output["result_url"]
    out_path = r"c:\Users\v_junshshi\WorkBuddy\Claw\douyin-project\tangzi_yawn_sleep_v4.mp4"
    print(f"\n[INFO] Downloading video to {out_path} ...", file=sys.stderr)
    vr = bc.requests.get(video_url, timeout=120)
    with open(out_path, "wb") as f:
        f.write(vr.content)
    print(f"[INFO] Saved: {out_path} ({len(vr.content)//1024//1024}MB)", file=sys.stderr)
