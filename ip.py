import os
import requests
from colorama import Fore, Style, init

init(autoreset=True)

API = "http://ip-api.com/json/"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print(Fore.CYAN + "=" * 55)
    print(Fore.GREEN + r"""
   _____ _____    _______             _
  |_   _|  __ \  |__   __|           | |
    | | | |__) |    | |_ __ __ _  ___| | _____ _ __
    | | |  ___/     | | '__/ _` |/ __| |/ / _ \ '__|
   _| |_| |         | | | | (_| | (__|   <  __/ |
  |_____|_|         |_|_|  \__,_|\___|_|\_\___|_|

""")
    print(Fore.YELLOW + "      Public IP Information Lookup Tool")
    print(Fore.CYAN + "=" * 55)


def lookup(ip):
    try:
        r = requests.get(API + ip, timeout=5)
        data = r.json()

        if data["status"] != "success":
            print(Fore.RED + "\n[-] Invalid IP Address!\n")
            return

        print(Fore.GREEN + "\n========== RESULT ==========\n")
        print(Fore.CYAN + f"IP        : {data.get('query')}")
        print(Fore.YELLOW + f"Country   : {data.get('country')}")
        print(Fore.YELLOW + f"Region    : {data.get('regionName')}")
        print(Fore.YELLOW + f"City      : {data.get('city')}")
        print(Fore.MAGENTA + f"ZIP       : {data.get('zip')}")
        print(Fore.BLUE + f"ISP       : {data.get('isp')}")
        print(Fore.GREEN + f"Org       : {data.get('org')}")
        print(Fore.CYAN + f"Timezone  : {data.get('timezone')}")
        print(Fore.RED + f"Latitude  : {data.get('lat')}")
        print(Fore.RED + f"Longitude : {data.get('lon')}")
        print(Fore.WHITE + f"AS        : {data.get('as')}")
        print(Fore.GREEN + "\n============================\n")

    except Exception as e:
        print(Fore.RED + f"Error: {e}")


def menu():
    while True:
        clear()
        banner()

        print(Fore.YELLOW + "[1] Lookup IP Address")
        print(Fore.CYAN + "[2] My Public IP")
        print(Fore.RED + "[3] Exit")

        choice = input(Fore.GREEN + "\nSelect: ")

        if choice == "1":
            ip = input(Fore.CYAN + "Enter IP: ")
            lookup(ip)
            input(Fore.YELLOW + "\nPress Enter...")

        elif choice == "2":
            try:
                ip = requests.get("https://api.ipify.org").text
                lookup(ip)
            except:
                print(Fore.RED + "Failed to get your public IP.")
            input(Fore.YELLOW + "\nPress Enter...")

        elif choice == "3":
            print(Fore.GREEN + "Goodbye!")
            break

        else:
            print(Fore.RED + "Invalid Choice!")
            input("Press Enter...")


if __name__ == "__main__":
    menu()
