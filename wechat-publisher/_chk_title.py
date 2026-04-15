import json, sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher")
p = json.loads(Path("output/publish_runs/payload_20260415_112323.json").read_text(encoding="utf-8"))
t = p["article"]["title"]
print(f"payload_title_chars={len(t)}")
print(f"payload_title_bytes={len(t.encode('utf-8'))}")
print(repr(t))
