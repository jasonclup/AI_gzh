# -*- coding: utf-8 -*-
"""Self-check: verify all 3 layers work correctly."""
import urllib.request, socket, json, time

socket.setdefaulttimeout(8)
BASE = "http://127.0.0.1:8080"
results = []

def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append(f"  [{status}] {name} - {detail}")
    print(f"[{status}] {name}")

# ── Check 1: Server is running ──
try:
    r = urllib.request.urlopen(BASE + "/", timeout=5)
    check("Server alive", r.status == 200, f"status={r.status}")
except Exception as e:
    check("Server alive", False, str(e)[:60])

# ── Check 2: Topics page loads (static HTML) ──
try:
    r = urllib.request.urlopen(BASE + "/topics", timeout=5)
    html = r.read().decode("utf-8", errors="replace")
    has_data = "FALLBACK" in html or "热门话题" in html
    check("Topics page HTML", has_data, f"{len(html)} bytes")
except Exception as e:
    check("Topics page HTML", False, str(e)[:60])

# ── Check 3: API returns data (with network fetch) ──
t0 = time.time()
try:
    r = urllib.request.urlopen(BASE + "/api/topics/fetch", timeout=15)
    elapsed = time.time() - t0
    data = json.loads(r.read().decode("utf-8"))
    count = len(data.get("data", []))
    source = data.get("data", [{}])[0].get("source", "N/A") if count > 0 else "empty"
    title_preview = ""
    if count > 0:
        title_preview = data["data"][0].get("title", "")[:30]
    
    is_ok = count > 0 and elapsed < 15
    check(f"API real-time data", is_ok, 
          f"count={count}, source='{source}', time={elapsed:.1f}s, title='{title_preview}'")
except Exception as e:
    elapsed = time.time() - t0
    check("API real-time data", False, f"time={elapsed:.1f}s, err={str(e)[:50]}")

# ── Summary ──
print("\n=== SELF-CHECK SUMMARY ===")
passed = sum(1 for r in results if "[PASS]" in r)
total = len(results)
print(f"Passed: {passed}/{total}")

with open("_selfcheck.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
    f.write(f"\n\nTotal: {passed}/{total} passed\n")
