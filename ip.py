#!/usr/bin/env python3

import os
import ipaddress
import requests
from colorama import Fore, Style, init

init(autoreset=True)

API = "http://ip-api.com/json/"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + r"""
   _____ _____    _______             _
  |_   _|  __ \  |__   __|           | |
    | | | |__) |    | |_ __ __ _  ___| | _____ _ __
    | | |  ___/     | | '__/ _` |/ __| |/ / _ \ '__|
   _| |_| |         | | | | (_| | (__|   <  __/ |
  |_____|_|         |_|_|  \__,_|\___|_|\_\___|_|

""")
    print(Fore.YELLOW + "          Public IP Information Lookup Tool")
    print(Fore.CYAN + "=" * 60)


def save_result(data):
    with open("results.txt", "a", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        for k, v in data.items():
            f.write(f"{k}: {v}\n")
        f.write("=" * 50 + "\n\n")


def lookup(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        print(Fore.RED + "\n[-] Invalid IP Address!\n")
        return

    try:
        response = requests.get(API + ip, timeout=5)
        data = response.json()

        if data.get("status") != "success":
            print(Fore.RED + "\n[-] Lookup Failed!\n")
            return

        result = {
            "IP": data.get("query"),
            "Country": data.get("country"),
            "Country Code": data.get("countryCode"),
            "Region": data.get("regionName"),
            "City": data.get("city"),
            "ZIP": data.get("zip"),
            "Latitude": data.get("lat"),
            "Longitude": data.get("lon"),
            "Timezone": data.get("timezone"),
            "ISP": data.get("isp"),
            "Organization": data.get("org"),
            "ASN": data.get("as"),
            "Google Maps": f"https://maps.google.com/?q={data.get('lat')},{data.get('lon')}",
        }

        print(Fore.GREEN + "\n========== RESULT ==========\n")

        colors = [
            Fore.CYAN,
            Fore.YELLOW,
            Fore.GREEN,
            Fore.MAGENTA,
            Fore.BLUE,
            Fore.WHITE,
        ]

        i = 0
        for key, value in result.items():
            print(colors[i % len(colors)] + f"{key:<15}: {value}")
            i += 1

        print(Fore.GREEN + "\n============================\n")

        save_result(result)
        print(Fore.YELLOW + "✔ Result saved to results.txt")

    except requests.exceptions.Timeout:
        print(Fore.RED + "\nRequest Timeout!")

    except requests.exceptions.ConnectionError:
        print(Fore.RED + "\nNo Internet Connection!")

    except Exception as e:
        print(Fore.RED + f"\nError: {e}")


def my_public_ip():
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
        print(Fore.GREEN + f"\nYour Public IP: {ip}")
        lookup(ip)
    except Exception:
        print(Fore.RED + "Failed to fetch Public IP.")


def menu():
    while True:
        clear()
        banner()

        print(Fore.YELLOW + "[1] Lookup IP Address")
        print(Fore.CYAN + "[2] My Public IP")
        print(Fore.MAGENTA + "[3] About")
        print(Fore.RED + "[4] Exit")

        choice = input(Fore.GREEN + "\nSelect Option: ").strip()

        if choice == "1":
            ip = input(Fore.CYAN + "\nEnter IP Address: ").strip()
            lookup(ip)
            input(Fore.YELLOW + "\nPress Enter to continue...")

        elif choice == "2":
            my_public_ip()
            input(Fore.YELLOW + "\nPress Enter to continue...")

        elif choice == "3":
            clear()
            banner()
            print(Fore.GREEN + "Developer : Your Name")
            print(Fore.CYAN + "Version   : 2.0")
            print(Fore.YELLOW + "Language  : Python")
            print(Fore.MAGENTA + "API       : ip-api.com")
            input(Fore.YELLOW + "\nPress Enter to continue...")

        elif choice == "4":
            print(Fore.GREEN + "\nGoodbye!\n")
            break

        else:
            print(Fore.RED + "\nInvalid Option!")
            input(Fore.YELLOW + "\nPress Enter...")


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\nProgram Interrupted!")
