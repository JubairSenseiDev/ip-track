<div align="center">

# 🤖 Telegram IP Track Bot (Node.js)

A simple and modern Telegram bot for IP address lookup, built with **Node.js**.

Same features as the Python bot, made for **Termux basic students**.

</div>

---

## ✨ Features

- 🌍 Lookup any IPv4 & IPv6 address
- 🌐 Server Public IP
- 📜 Lookup History
- 📍 Google Maps Link
- ⚡ Fast Response
- 🛡️ IP Validation
- 🐧 Linux & Termux Compatible

---

# 🚀 Installation

## 1️⃣ Update Package Lists

```bash
apt update && apt upgrade
```

**What it does:**
- `apt update` → Downloads the latest package list from repositories.
- `apt upgrade` → Updates installed packages to their latest versions.

---

## 2️⃣ Install Required Packages

```bash
apt install nodejs git
```

**What it does:**
- `nodejs` → Installs Node.js to run the bot.
- `git` → Installs Git to download the project.

---

## 3️⃣ Clone Repository

```bash
git clone https://github.com/JubairSenseiDev/ip-track
```

**What it does:**
Downloads the latest source code from GitHub to your device.

---

## 4️⃣ Open Bot Folder

```bash
cd ip-track/telegram-bot-nodejs
```

**What it does:**
Moves into the bot directory.

---

## 5️⃣ Install Dependencies

```bash
npm install
```

**What it does:**
Installs the required Node.js package `node-telegram-bot-api`, which talks to the Telegram API for you.

---

## 6️⃣ Configure Bot

Edit **config.json**:

```json
{
    "BOT_TOKEN": "YOUR_BOT_TOKEN"
}
```

**How to get a token:**
1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the instructions.
3. Copy the token BotFather gives you and paste it into `config.json`.

> Need your Python bot's token? Copy it from `telegram-bot/config.json`.

---

## 7️⃣ Run the Bot

```bash
node bot.js
```

or

```bash
npm start
```

**What it does:**
Starts the Telegram bot and begins listening for messages.

> Press `CTRL + C` to stop the bot.

---

# 📱 Main Menu

- 🌍 Lookup IP
- 🌐 Server Public IP
- 📜 Lookup History
- ℹ️ About

---

# 📋 Requirements

- Node.js 18.x or newer
- Internet Connection
- Telegram Bot Token
- Linux / Termux

---

# 📂 Project Structure

```text
telegram-bot-nodejs/
├── bot.js
├── config.json
├── package.json
└── README.md
```

---

# 📡 APIs

| API | Purpose |
|------|---------|
| ip-api.com | IP Geolocation |
| api.ipify.org | Server Public IP |

---

# 🤖 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |

---

# 🐍 Prefer Python?

Check out the Python Telegram bot:

```bash
cd ip-track/telegram-bot
pip install -r requirements.txt
python3 bot.py
```

---

# ❤️ Developer

**JubairSenseiDev**

GitHub:
https://github.com/JubairSenseiDev

---

## 📄 License

This project is released under the MIT License.

---

<div align="center">

Made with ❤️ using Node.js

</div>
