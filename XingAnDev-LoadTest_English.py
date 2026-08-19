import os
import shutil

os.system("cls")

logo = r"""
$$\   $$\ $$\                      $$$$$$\            $$$$$$$\                       
$$ |  $$ |\__|                    $$  __$$\           $$  __$$\                      
\$$\ $$  |$$\ $$$$$$$\   $$$$$$\  $$ /  $$ |$$$$$$$\  $$ |  $$ | $$$$$$\ $$\    $$\  
 \$$$$  / $$ |$$  __$$\ $$  __$$\ $$$$$$$$ |$$  __$$\ $$ |  $$ |$$  __$$\\$$\  $$  | 
 $$  $$<  $$ |$$ |  $$ |$$ /  $$ |$$  __$$ |$$ |  $$ |$$ |  $$ |$$$$$$$$ |\$$\$$  /  
$$  /\$$\ $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$   ____| \$$$  /   
$$ /  $$ |$$ |$$ |  $$ |\$$$$$$$ |$$ |  $$ |$$ |  $$ |$$$$$$$  |\$$$$$$$\   \$  /    
\__|  \__|\__|\__|  \__| \____$$ |\__|  \__|\__|  \__|\_______/  \_______|   \_/     
                        $$\   $$ |                                                   
                        \$$$$$$  |                                                   
                         \______/                                                   
"""

# Get the current terminal width
terminal_width = shutil.get_terminal_size().columns

# Center each line automatically
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
# Configuration
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
U = input(f"{RED}Enter target URL: ")

if not U.lower().startswith(("http://", "https://")):
    U = "https://" + U

print(prompt, end="")
A = int(input(f"{RED}Enter concurrency: "))

print(prompt, end="")
B = int(input(f"{RED}Enter number of rounds: "))

os.system("cls")

print("Target URL:", U)
print("Concurrency:", A)
print("Rounds:", B)

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

print("Too many concurrent requests may exhaust system resources. Use with caution!")


URL = U

input("Press Enter to start...")

# Number of concurrent requests per round
CONCURRENCY = A

# Total number of rounds
ROUNDS = B

# =========================
# Statistics
# =========================

success = 0
errors = {}
lock = Lock()

HTTP_STATUS_EN = {
    200: "Request successful",
    201: "Resource created",
    204: "Request successful, no content",
    301: "Permanent redirect",
    302: "Temporary redirect",
    304: "Resource not modified",
    400: "Bad request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Page not found",
    405: "Method not allowed",
    408: "Request timeout",
    409: "Request conflict",
    412: "Precondition failed",
    413: "Request content too large",
    429: "Too many requests",
    500: "Internal server error",
    501: "Not implemented",
    502: "Bad gateway",
    503: "Service unavailable",
    504: "Gateway timeout",
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

        print(
            f"Status code: {response.status_code} - "
            f"{HTTP_STATUS_EN.get(response.status_code, 'Unknown status code')}"
        )

    except requests.RequestException as e:
        with lock:
            errors["Request exception"] = (
                errors.get("Request exception", 0) + 1
            )

        print("Request exception:", type(e).__name__, e)


# =========================
# Start test
# =========================

with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:

    for i in range(ROUNDS):
        print(f"\n========== Round {i + 1} ==========")

        # Submit CONCURRENCY identical URLs for each round
        list(executor.map(
            get_page,
            repeat(URL, CONCURRENCY)
        ))


# =========================
# Summary
# =========================

total_requests = CONCURRENCY * ROUNDS

print("\n========== Summary ==========")
print("Target:", URL)
print("Concurrency:", CONCURRENCY)
print("Rounds:", ROUNDS)
print("Total requests:", total_requests)
print("Successful:", success)

for code, count in errors.items():
    print(f"{code}: {count} times")

input("Press Enter to exit...")