import sys, os, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Run pipeline, capture to log file via Python's own redirection
result = subprocess.run(
    [sys.executable, '_run_full_pipeline_v2.py'],
    capture_output=True, text=False,
    encoding=None  # raw bytes
)
log_path = '_v3_run.log'
with open(log_path, 'wb') as f:
    f.write(result.stdout or b'')
    f.write(result.stderr or b'')

# Read back and print (skip CLIXML noise)
try:
    with open(log_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
except:
    with open(log_path, 'rb') as f:
        raw = f.read()
    lines = raw.decode('utf-8', errors='replace').splitlines(True)

for l in lines[-80:]:
    s = l.strip()
    if not s or s.startswith('<Objs') or s.startswith('</Objs'):
        continue
    # Skip pure XML noise lines
    if s.startswith('<') and ('Version' in s or 'xmlns' in s):
        continue
    try:
        print(l, end='')
    except UnicodeEncodeError:
        print(l.encode('ascii', errors='replace').decode('ascii'), end='')
