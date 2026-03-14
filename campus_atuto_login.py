import time
import requests
from playwright.sync_api import sync_playwright

# ===================== 仅需修改这部分配置 =====================
LOGIN_URL = "http://10.10.9.4/"       # 校园网登录地址
USERNAME = "21123610011"              # 你的账号
PASSWORD = "123456!!"                # 你的密码
# 固定点击坐标（根据自己屏幕调整）
USERNAME_CLICK_POS = (965, 240)      # 用户名输入框点击坐标
PASSWORD_CLICK_POS = (965, 279)      # 密码输入框点击坐标
SERVICE_CLICK_POS1 = (964, 314)      # 运营商下拉框点击坐标
SERVICE_CLICK_POS2 = (959, 355)      # 运营商选项点击坐标
LOGIN_BTN_POS = (963, 409)           # 登录按钮点击坐标
# 网络检测配置
CHECK_INTERVAL = 20             # 检测间隔（秒），建议5-10秒
TEST_URL = "https://www.baidu.com"   # 检测网络的地址（断网时访问失败）
TIMEOUT = 5                          # 检测超时时间（秒）
# ==============================================================

def check_network():
    """极简版网络检测：能访问TEST_URL就是联网，否则断网"""
    try:
        # 发送简单请求检测网络
        requests.get(TEST_URL, timeout=TIMEOUT)
        return True  # 联网状态
    except:
        return False # 断网状态

def simple_campus_login():
    """极简版：固定坐标点击+输入，无任何复杂逻辑"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--start-maximized", "--force-device-scale-factor=1"]
            )
            page = browser.new_context(viewport=None).new_page()

            # 1. 打开登录页
            page.goto(LOGIN_URL)
            time.sleep(4)

            # 2. 用户名
            page.mouse.click(*USERNAME_CLICK_POS, delay=100)
            page.keyboard.type(USERNAME, delay=50)
            time.sleep(0.5)

            # 3. 密码
            page.mouse.click(*PASSWORD_CLICK_POS, delay=100)
            page.keyboard.type(PASSWORD, delay=50)
            time.sleep(0.5)

            # 4. 运营商
            page.mouse.click(*SERVICE_CLICK_POS1, delay=100)
            time.sleep(0.5)
            page.mouse.click(*SERVICE_CLICK_POS2, delay=100)
            time.sleep(0.5)

            # 5. 登录
            page.mouse.click(*LOGIN_BTN_POS, delay=100)

            print("✅ 登录操作执行完成！")
            time.sleep(5)
            # 6. 检查网络连通性
            print("\n🔍 开始检查网络连接状态...")
            if check_network():
                print("🎉 网络连接成功！登录验证通过")
            else:
                print("❌ 网络连接失败！可能登录未成功")
            browser.close()
    except Exception as e:
        print(f"❌ 登录执行失败：{str(e)}")

def network_monitor():
    """核心：持续监测网络，断网就执行登录"""
    print(f"🚀 校园网自动重连脚本启动（检测间隔：{CHECK_INTERVAL}秒）")
    print(f"📌 检测地址：{TEST_URL} | 登录地址：{LOGIN_URL}")
    print("="*50)

    # 无限循环监测
    try:
        while True:
            if not check_network():
                print(f"\n⚠️ [{time.strftime('%H:%M:%S')}] 检测到断网，开始自动登录...")
                simple_campus_login()
            else:
                print(f"✅ [{time.strftime('%H:%M:%S')}] 网络正常")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        # 按Ctrl+C停止脚本
        print("\n🛑 脚本已手动停止")

if __name__ == "__main__":
    # 先安装依赖（首次运行前执行）：pip install requests playwright
    # playwright install msedge
    network_monitor()