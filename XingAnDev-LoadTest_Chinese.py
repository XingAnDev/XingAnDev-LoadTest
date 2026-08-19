import os
import shutil

os.system("cls")

logo = r"""
$$\   $$\ $$\                      $$$$$$\            $$$$$$$\                      
$$ |  $$ |\__|                    $$  __$$\           $$  __$$\                     
\$$\ $$  |$$\ $$$$$$$\   $$$$$$\  $$ /  $$ |$$$$$$$\  $$ |  $$ | $$$$$$\ $$\    $$\ 
 \$$$$  / $$ |$$  __$$\ $$  __$$\ $$$$$$$$ |$$  __$$\ $$ |  $$ |$$  __$$\\$$\  $$  |
 $$  $$<  $$ |$$ |  $$ |$$ /  $$ |$$  __$$ |$$ |  $$ |$$ |  $$ |$$$$$$$$ |\$$\$$  / 
$$  /\$$\ $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$   ____| \$$$  /  
$$ /  $$ |$$ |$$ |  $$ |\$$$$$$$ |$$ |  $$ |$$ |  $$ |$$$$$$$  |\$$$$$$$\   \$  /   
\__|  \__|\__|\__|  \__| \____$$ |\__|  \__|\__|  \__|\_______/  \_______|   \_/    
                        $$\   $$ |                                                  
                        \$$$$$$  |                                                  
                         \______/                                                   """

# 获取当前终端尺寸
terminal_width = shutil.get_terminal_size().columns

# 每行自动居中
for line in logo.splitlines():
    if line.strip():
        print(line.center(terminal_width))
    else:
        print()


import requests
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from threading import Lock

# =========================
# 配置
# =========================
import winreg
from colorama import init, Fore

user = os.getenv("USER") or os.getenv("USERNAME") or "user"
path = os.getcwd()


def get_windows_version():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        )

        build, _ = winreg.QueryValueEx(key, "CurrentBuild")
        winreg.CloseKey(key)

        build = int(build)

        if build >= 22000:
            return "Windows11"
        elif build >= 10240:
            return "Windows10"
        else:
            return "Windows"

    except Exception:
        return "Windows"


host = get_windows_version()

init()

BLUE = Fore.BLUE
RED = Fore.RED
WHITE = Fore.WHITE
RESET = Fore.RESET


def kali_prompt(user, host, path):
    return (
        f"{BLUE}┌──({RED}{user}㉿{host}{BLUE})-["
        f"{WHITE}{path}"
        f"{BLUE}]{RESET}\n"
        f"{BLUE}└─{RED}#{RESET} "
    )


prompt = kali_prompt(user, host, path)

print(prompt, end="")
U = input(f"{RED}请输入目标地址: ")

if not U.lower().startswith(("http://", "https://")):
    U = "https://" + U

print(prompt, end="")
A = int(input(f"{RED}请输入并发数: "))

print(prompt, end="")
B = int(input(f"{RED}请输入轮数: "))

os.system("cls")
print("目标地址: ", U)
print("并发数: ", A)
print("轮数: ", B)
import platform
import psutil

cpu = platform.processor()
memory = psutil.virtual_memory().total / (1024 ** 3)
os_name = platform.system()
os_version = platform.version()

print(f"CPU: {cpu}")
print(f"RAM: {memory:.1f} GB")
print(f"OS: {os_name}")
print(f"Version: {os_version}")
print("过多的并发请求可能会导致系统资源耗尽，请谨慎操作！")


URL = U

input("按回车键开始...")

# 每轮并发请求数
CONCURRENCY = A

# 总轮数
ROUNDS = B

# =========================
# 统计
# =========================

success = 0
errors = {}
lock = Lock()
HTTP_STATUS_CN = {
    200: "请求成功",
    201: "创建成功",
    204: "请求成功，无内容",
    301: "永久重定向",
    302: "临时重定向",
    304: "资源未修改",
    400: "请求错误",
    401: "未授权",
    403: "禁止访问",
    404: "页面不存在",
    405: "请求方法不允许",
    408: "请求超时",
    409: "请求冲突",
    412: "先决条件失败",
    413: "请求内容过大",
    429: "请求过多",
    500: "服务器内部错误",
    501: "服务器不支持该功能",
    502: "网关错误",
    503: "服务器不可用",
    504: "网关超时",
}

def get_page(url):
    global success

    try:
        response = requests.get(url, timeout=100)

        with lock:
            if response.status_code == 200:
                success += 1
            else:
                errors[response.status_code] = (
                    errors.get(response.status_code, 0) + 1
                )

        print(f"状态码: {response.status_code} - {HTTP_STATUS_CN.get(response.status_code, '未知状态码')}")

    except requests.RequestException as e:
        with lock:
            errors["请求异常"] = errors.get("请求异常", 0) + 1

        print("请求异常:", type(e).__name__, e)


# =========================
# 开始测试
# =========================

with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:

    for i in range(ROUNDS):
        print(f"\n========== 第 {i + 1} 轮 ==========")

        # 每轮提交 CONCURRENCY 个相同 URL
        list(executor.map(
            get_page,
            repeat(URL, CONCURRENCY)
        ))


# =========================
# 总结
# =========================

total_requests = CONCURRENCY * ROUNDS

print("\n========== 总结 ==========")
print("目标:", URL)
print("并发数:", CONCURRENCY)
print("轮数:", ROUNDS)
print("总请求:", total_requests)
print("成功:", success)

for code, count in errors.items():
    print(f"{code}: {count} 次")
input("按回车键退出...")