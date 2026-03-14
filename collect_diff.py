import sys
import time
from playwright.sync_api import sync_playwright

# 强制 stdout 使用 UTF-8，避免 Windows GBK 终端报错
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LOGIN_URL = "http://10.10.9.4/"

collected_coords = []

def _on_click(x, y):
    xi, yi = int(x), int(y)
    label = f"第{len(collected_coords)+1}个"
    print(f"  [{label}] CLICK -> ({xi}, {yi})")
    collected_coords.append((xi, yi))

# 在每个 frame 加载时自动注入点击监听器
JS_INIT = """
(function() {
    if (window._coordListenerAttached) return;
    window._coordListenerAttached = true;

    function getPageCoord(e) {
        // 若在 iframe 内，尝试加上 iframe 在父页面的偏移
        try {
            if (window.frameElement) {
                var rect = window.frameElement.getBoundingClientRect();
                return { x: e.clientX + rect.left, y: e.clientY + rect.top };
            }
        } catch(err) {
            // 跨域时无法访问 frameElement，直接用 clientX/clientY
        }
        return { x: e.clientX, y: e.clientY };
    }

    document.addEventListener('click', function(e) {
        if (typeof window.collectCoord === 'function') {
            var pos = getPageCoord(e);
            window.collectCoord(Math.round(pos.x), Math.round(pos.y));
        }
    }, true);
})();
"""

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--force-device-scale-factor=1"]
        )
        context = browser.new_context(viewport=None)

        # expose_function 在 context 级别注册，所有 page/frame 均可调用
        context.expose_function("collectCoord", _on_click)

        # add_init_script 确保每次新 frame 导航时自动注入监听器
        context.add_init_script(JS_INIT)

        page = context.new_page()
        page.goto(LOGIN_URL)
        time.sleep(4)

        # 对已存在的 frame 补充注入（以防 add_init_script 对首次加载的 frame 未触发）
        for frame in page.frames:
            try:
                frame.evaluate(JS_INIT)
            except Exception:
                pass

        print("✅ （注意先断网）坐标采集就绪，请依次点击以下元素：")
        print("   1. 用户名输入框")
        print("   2. 密码输入框")
        print("   3. 运营商下拉框")
        print("   4. 运营商选项")
        print("   5. 登录按钮")
        print("\n👉 按 Ctrl+C 结束采集\n")

        try:
            while True:
                time.sleep(0.5)
                # 兜底：定期对所有 frame 重注入，防止动态加载的 frame 漏掉
                for frame in page.frames:
                    try:
                        frame.evaluate(JS_INIT)
                    except Exception:
                        pass
        except KeyboardInterrupt:
            print("\n🛑 坐标采集结束")

except Exception as e:
    print(f"❌ 错误：{e}")

finally:
    time.sleep(1)
    print(f"\n📊 共采集 {len(collected_coords)} 个坐标：")
    for i, (x, y) in enumerate(collected_coords, 1):
        print(f"   {i}. ({x}, {y})")

    if collected_coords:
        NAMES = [
            "USERNAME_CLICK_POS",
            "PASSWORD_CLICK_POS",
            "SERVICE_CLICK_POS1",
            "SERVICE_CLICK_POS2",
            "LOGIN_BTN_POS",
        ]
        print("\n📋 复制以下内容到 campus_auto_login.py 的配置区：")
        print("-" * 40)
        for i, (x, y) in enumerate(collected_coords):
            name = NAMES[i] if i < len(NAMES) else f"POS_{i+1}"
            print(f"{name} = ({x}, {y})")
        print("-" * 40)
