# -*- coding: utf-8 -*-
"""Launch wrapper - redirects all output to log file"""
import sys, os, subprocess
from datetime import datetime

log_path = r"c:\Users\v_junshshi\WorkBuddy\Claw\output\feishu_run.log"
script = r"c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\_run_with_feishu.py"

with open(log_path, "w", encoding="utf-8") as f:
    f.write(f"=== Run at {datetime.now()} ===\n")
    f.flush()

result = subprocess.run(
    [sys.executable, script],
    cwd=r"c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher",
    capture_output=True, text=True, encoding='utf-8', errors='replace',
    timeout=120
)

with open(log_path, "a", encoding="utf-8") as f:
    f.write("\n=== STDOUT ===\n")
    f.write(result.stdout)
    f.write("\n=== STDERR ===\n")
    f.write(result.stderr)
    f.write(f"\n=== Return code: {result.returncode} ===\n")

print(f"Done! Log saved to: {log_path}")
print(f"Return code: {result.returncode}")
