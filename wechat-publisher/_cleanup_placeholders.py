# -*- coding: utf-8 -*-
"""扫描并清理Pollinations限流占位图"""
import os, hashlib, time

# Windows控制台UTF-8输出
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

IMAGES_DIR = r"C:\Users\v_junshshi\WorkBuddy\Claw\output\images"

# 已知占位图签名
PLACEHOLDER_SIGS = {
    'dd12e9e08638': 122628,  # 隧道图
}
SIZE_TOLERANCE = 2048

def get_md5_prefix(filepath, n=12):
    """计算文件MD5前n位"""
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()[:n]

def main():
    files = [f for f in os.listdir(IMAGES_DIR) if f.endswith('.png')]
    print(f"共 {len(files)} 个PNG文件\n")
    
    placeholders = []
    real_images = []
    
    for fname in sorted(files):
        fpath = os.path.join(IMAGES_DIR, fname)
        fsize = os.path.getsize(fpath)
        mtime = time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(fpath)))
        
        is_placeholder = False
        for sig_md5, expected_size in PLACEHOLDER_SIGS.items():
            if abs(fsize - expected_size) <= SIZE_TOLERANCE:
                actual_md5 = get_md5_prefix(fpath)
                if actual_md5.startswith(sig_md5):
                    is_placeholder = True
                    placeholders.append((fname, fsize, mtime))
                    break
        
        if not is_placeholder:
            real_images.append((fname, fsize, mtime))
    
    print(f"=== 占位图（将被清理）：{len(placeholders)} 张 ===")
    for fname, sz, mt in placeholders:
        print(f"  🗑️ {fname} ({sz//1024}KB, {mt})")
    
    print(f"\n=== 真实配图（保留）：{len(real_images)} 张 ===")
    for fname, sz, mt in real_images:
        print(f"  ✅ {fname} ({sz//1024}KB, {mt})")
    
    # 执行删除
    if placeholders:
        print(f"\n正在删除 {len(placeholders)} 张占位图...")
        deleted = 0
        for fname, sz, mt in placeholders:
            try:
                os.remove(os.path.join(IMAGES_DIR, fname))
                deleted += 1
            except Exception as e:
                print(f"  删除失败 {fname}: {e}")
        print(f"\n完成！已删除 {deleted}/{len(placeholders)} 张占位图")
        
        remaining = len([f for f in os.listdir(IMAGES_DIR) if f.endswith('.png')])
        print(f"剩余文件：{remaining} 张")
    else:
        print("\n没有发现占位图！")

if __name__ == '__main__':
    main()
