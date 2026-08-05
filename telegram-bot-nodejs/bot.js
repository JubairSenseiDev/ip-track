#!/usr/bin/env node
// JubairZ - Node.js Telegram IP Lookup Bot

const fs = require("fs");
const net = require("net");
const TelegramBot = require("node-telegram-bot-api");

const API = "http://ip-api.com/json/";

let config;
try {
  config = JSON.parse(fs.readFileSync("config.json", "utf8"));
} catch (err) {
  console.error("config.json file not found. Please create one with BOT_TOKEN.");
  process.exit(1);
}

const BOT_TOKEN = config.BOT_TOKEN;
if (!BOT_TOKEN) {
  console.error("BOT_TOKEN is missing in config.json");
  process.exit(1);
}

const bot = new TelegramBot(BOT_TOKEN, { polling: true });

// In-memory state
const userHistory = {};  // userId -> list of last 10 looked up IPs
const awaitingIp = new Set();  // chatIds waiting for an IP input

// -----------------------------------------------------------------------------
// Helper functions
// -----------------------------------------------------------------------------
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function mainMenuKeyboard() {
  return {
    reply_markup: {
      inline_keyboard: [
        [
          { text: "🌍 Lookup IP", callback_data: "menu_lookup" },
          { text: "🌐 My Public IP", callback_data: "menu_my_ip" }
        ],
        [
          { text: "📜 Lookup History", callback_data: "menu_history" },
          { text: "ℹ️ About", callback_data: "menu_about" }
        ]
      ]
    }
  };
}

function homeKeyboard() {
  return {
    reply_markup: {
      inline_keyboard: [[{ text: "🏠 Home", callback_data: "menu_home" }]]
    }
  };
}

function resultKeyboard(lat, lon) {
  const mapsUrl = `https://maps.google.com/?q=${lat},${lon}`;
  return {
    reply_markup: {
      inline_keyboard: [
        [{ text: "📍 Open Maps", url: mapsUrl }],
        [
          { text: "🔍 Lookup Another", callback_data: "menu_lookup" },
          { text: "🏠 Home", callback_data: "menu_home" }
        ]
      ]
    }
  };
}

async function fetchJson(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } finally {
    clearTimeout(timer);
  }
}

const fetchIpData = (ip) => fetchJson(API + ip);

const fetchPublicIp = async () => {
  const data = await fetchJson("https://api.ipify.org?format=json");
  return data.ip;
};

function formatIpData(data) {
  if (data.status !== "success") {
    return `❌ <b>Lookup Failed:</b> ${escapeHtml(data.message || "Unknown error")}`;
  }
  return (
    "<b>🌍 IP Lookup Result</b>\n\n" +
    `<b>• IP:</b> <code>${escapeHtml(data.query || "N/A")}</code>\n` +
    `<b>• Country:</b> ${escapeHtml(data.country || "N/A")} (${escapeHtml(data.countryCode || "N/A")})\n` +
    `<b>• Region:</b> ${escapeHtml(data.regionName || "N/A")}\n` +
    `<b>• City:</b> ${escapeHtml(data.city || "N/A")}\n` +
    `<b>• ZIP:</b> ${escapeHtml(data.zip || "N/A")}\n` +
    `<b>• Latitude:</b> ${data.lat ?? "N/A"}\n` +
    `<b>• Longitude:</b> ${data.lon ?? "N/A"}\n` +
    `<b>• Timezone:</b> ${escapeHtml(data.timezone || "N/A")}\n` +
    `<b>• ISP:</b> ${escapeHtml(data.isp || "N/A")}\n` +
    `<b>• Organization:</b> ${escapeHtml(data.org || "N/A")}\n` +
    `<b>• ASN:</b> ${escapeHtml(data.as || "N/A")}`
  );
}

function addToHistory(userId, ip) {
  if (!userHistory[userId]) userHistory[userId] = [];
  userHistory[userId].push(ip);
  if (userHistory[userId].length > 10) {
    userHistory[userId] = userHistory[userId].slice(-10);
  }
}

async function editMessage(chatId, messageId, text, keyboard) {
  await bot.editMessageText(text, {
    chat_id: chatId,
    message_id: messageId,
    parse_mode: "HTML",
    ...keyboard
  });
}

// -----------------------------------------------------------------------------
// Command handler: /start
// -----------------------------------------------------------------------------
bot.onText(/\/start/, async (msg) => {
  const chatId = msg.chat.id;
  awaitingIp.delete(chatId);

  const welcome =
    "👋 <b>Welcome to the IP Lookup Bot!</b>\n\n" +
    "I can help you find detailed information about any IPv4 or IPv6 address.\n" +
    "Please select an option from the menu below:";

  await bot.sendMessage(chatId, welcome, {
    parse_mode: "HTML",
    ...mainMenuKeyboard()
  });
});

// -----------------------------------------------------------------------------
// Inline keyboard handler
// -----------------------------------------------------------------------------
bot.on("callback_query", async (query) => {
  const chatId = query.message.chat.id;
  const messageId = query.message.message_id;
  const userId = query.from.id;
  await bot.answerCallbackQuery(query.id);

  try {
    if (query.data === "menu_home") {
      awaitingIp.delete(chatId);
      await editMessage(
        chatId,
        messageId,
        "🏠 <b>Main Menu</b>\n\nPlease select an option below:",
        mainMenuKeyboard()
      );
    } else if (query.data === "menu_lookup") {
      awaitingIp.add(chatId);
      await editMessage(
        chatId,
        messageId,
        "🌍 <b>Lookup IP</b>\n\nPlease send me the IPv4 or IPv6 address you want to look up.",
        homeKeyboard()
      );
    } else if (query.data === "menu_my_ip") {
      awaitingIp.delete(chatId);
      await editMessage(chatId, messageId, "⏳ Fetching your public IP address...", null);

      try {
        const publicIp = await fetchPublicIp();
        const ipData = await fetchIpData(publicIp);
        if (ipData.status === "success") addToHistory(userId, publicIp);

        const keyboard = ipData.status === "success"
          ? resultKeyboard(ipData.lat, ipData.lon)
          : homeKeyboard();

        await editMessage(chatId, messageId, formatIpData(ipData), keyboard);
      } catch (err) {
        console.error("Error fetching my public IP:", err);
        await editMessage(
          chatId,
          messageId,
          "❌ <b>An error occurred while fetching your IP data.</b>",
          homeKeyboard()
        );
      }
    } else if (query.data === "menu_history") {
      awaitingIp.delete(chatId);
      const history = userHistory[userId] || [];

      let text;
      if (history.length === 0) {
        text = "📜 <b>Lookup History</b>\n\nYou haven't looked up any IPs yet.";
      } else {
        text = "📜 <b>Lookup History (Last 10)</b>\n\n";
        [...history].reverse().forEach((ip, index) => {
          text += `${index + 1}. <code>${escapeHtml(ip)}</code>\n`;
        });
      }

      await editMessage(chatId, messageId, text, homeKeyboard());
    } else if (query.data === "menu_about") {
      awaitingIp.delete(chatId);
      const about =
        "ℹ️ <b>About This Bot</b>\n\n" +
        "<b>• Project:</b> Telegram IP Lookup Bot\n" +
        "<b>• Developer:</b> JubairSenseiDev\n" +
        `<b>• Node.js Version:</b> ${process.version}\n` +
        "<b>• API Used:</b> ip-api.com & ipify.org\n" +
        "<b>• GitHub:</b> <a href='https://github.com/JubairSenseiDev'>Link to Repository</a>";

      await editMessage(chatId, messageId, about, homeKeyboard());
    }
  } catch (err) {
    console.error("Callback error:", err);
  }
});

// -----------------------------------------------------------------------------
// Message handler: IP input
// -----------------------------------------------------------------------------
bot.on("message", async (msg) => {
  const chatId = msg.chat.id;

  if (!msg.text || msg.text.startsWith("/")) return;
  if (!awaitingIp.has(chatId)) return;

  const userId = msg.from.id;
  const text = msg.text.trim();

  if (net.isIP(text) === 0) {
    await bot.sendMessage(
      chatId,
      "❌ <b>Invalid IP Address.</b>\nPlease provide a valid IPv4 or IPv6 address.",
      { parse_mode: "HTML", ...homeKeyboard() }
    );
    return;
  }

  const processingMsg = await bot.sendMessage(
    chatId,
    `⏳ Looking up <code>${escapeHtml(text)}</code>...`,
    { parse_mode: "HTML" }
  );

  try {
    const ipData = await fetchIpData(text);
    if (ipData.status === "success") addToHistory(userId, text);

    const keyboard = ipData.status === "success"
      ? resultKeyboard(ipData.lat, ipData.lon)
      : homeKeyboard();

    await editMessage(chatId, processingMsg.message_id, formatIpData(ipData), keyboard);
  } catch (err) {
    console.error("Error fetching IP data:", err);
    await editMessage(
      chatId,
      processingMsg.message_id,
      "❌ <b>An error occurred while fetching the IP data.</b>",
      homeKeyboard()
    );
  }
});

// -----------------------------------------------------------------------------
// Start
// -----------------------------------------------------------------------------
bot.on("polling_error", (err) => {
  console.error("Polling error:", err.message);
});

console.log("Bot started. Polling for updates...");
