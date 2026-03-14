"""
环境检查与安装脚本
检查 campus_atuto_login.py 和 collect_diff.py 所需的依赖，缺少则自动安装。
"""
import sys
import subprocess
import importlib

# 强制 stdout 使用 UTF-8，避免 Windows GBK 终端乱码
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_PACKAGES = [
    ("requests", "requests"),
    ("playwright", "playwright"),
]

def check_and_install(import_name, pip_name):
    try:
        importlib.import_module(import_name)
        print(f"[OK] {pip_name} 已安装")
        return True
    except ImportError:
        print(f"[缺少] {pip_name} 未安装，正在安装...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"[OK] {pip_name} 安装成功")
            return True
        else:
            print(f"[失败] {pip_name} 安装失败：\n{result.stderr}")
            return False

def check_playwright_browsers():
    """检查 Playwright Chromium 浏览器是否已安装"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("[OK] Playwright Chromium 浏览器已就绪")
        return True
    except Exception as e:
        if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
            print("[缺少] Playwright 浏览器未安装，正在安装 Chromium...")
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("[OK] Chromium 安装成功")
                return True
            else:
                print(f"[失败] Chromium 安装失败：\n{result.stderr}")
                return False
        else:
            print(f"[警告] Playwright 检查时出错：{e}")
            return False

if __name__ == "__main__":
    print("=" * 40)
    print("检查运行环境...")
    print("=" * 40)

    all_ok = True
    for import_name, pip_name in REQUIRED_PACKAGES:
        if not check_and_install(import_name, pip_name):
            all_ok = False

    if all_ok:
        check_playwright_browsers()

    print("=" * 40)
    if all_ok:
        print("环境检查完成，可以运行脚本了。")
    else:
        print("部分依赖安装失败，请手动检查。")
    print("=" * 40)