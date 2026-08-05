#!/usr/bin/env node
// JubairZ

const fs = require("fs");
const net = require("net");
const path = require("path");
const readline = require("readline");

const API = "http://ip-api.com/json/";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const lines = [];
let waitingResolve = null;

rl.on("line", (line) => {
  if (waitingResolve) {
    const resolve = waitingResolve;
    waitingResolve = null;
    resolve(line);
  } else {
    lines.push(line);
  }
});

function ask(question) {
  process.stdout.write(question);
  if (lines.length > 0) {
    return Promise.resolve(lines.shift());
  }
  return new Promise((resolve) => {
    waitingResolve = resolve;
  });
}

const clear = () => {
  process.stdout.write(process.platform === "win32" ? "\x1b[2J\x1b[0f" : "\x1b[2J\x1b[H");
};

function color(code) {
  return (text) => `\x1b[${code}m${text}\x1b[0m`;
}

const CYAN = color(36);
const GREEN = color(32);
const YELLOW = color(33);
const RED = color(31);
const MAGENTA = color(35);
const BLUE = color(34);
const WHITE = color(37);

function banner() {
  console.log(CYAN("=".repeat(60)));
  console.log(GREEN(`
   _____ _____    _______             _
  |_   _|  __ \\  |__   __|           | |
    | | | |__) |    | |_ __ __ _  ___| | _____ _ __
    | | |  ___/     | | '__/ _\` |/ __| |/ / _ \\ '__|
   _| |_| |         | | | | (_| | (__|   <  __/ |
  |_____|_|         |_|_|  \\__,_|\\___|_|\\_\\___|_|

`));
  console.log(YELLOW("          Public IP Information Lookup Tool"));
  console.log(CYAN("=".repeat(60)));
}

function saveResult(data) {
  const lines = ["=".repeat(50)];
  for (const [key, value] of Object.entries(data)) {
    lines.push(`${key}: ${value}`);
  }
  lines.push("=".repeat(50), "");
  fs.appendFileSync(path.join(__dirname, "..", "results.txt"), lines.join("\n"), "utf8");
}

function isValidIP(ip) {
  return net.isIP(ip) !== 0;
}

async function lookup(ip) {
  if (!isValidIP(ip)) {
    console.log(RED("\n[-] Invalid IP Address!\n"));
    return;
  }

  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(API + ip, { signal: controller.signal });
    clearTimeout(timer);
    const data = await response.json();

    if (data.status !== "success") {
      console.log(RED("\n[-] Lookup Failed!\n"));
      return;
    }

    const result = {
      IP: data.query,
      Country: data.country,
      "Country Code": data.countryCode,
      Region: data.regionName,
      City: data.city,
      ZIP: data.zip,
      Latitude: data.lat,
      Longitude: data.lon,
      Timezone: data.timezone,
      ISP: data.isp,
      Organization: data.org,
      ASN: data.as,
      "Google Maps": `https://maps.google.com/?q=${data.lat},${data.lon}`,
    };

    console.log(GREEN("\n========== RESULT ==========\n"));

    const colors = [CYAN, YELLOW, GREEN, MAGENTA, BLUE, WHITE];
    let i = 0;
    for (const [key, value] of Object.entries(result)) {
      console.log(colors[i % colors.length](`${String(key).padEnd(15)}: ${value}`));
      i++;
    }

    console.log(GREEN("\n============================\n"));

    saveResult(result);
    console.log(YELLOW("✔ Result saved to results.txt"));

  } catch (err) {
    if (err.name === "AbortError") {
      console.log(RED("\nRequest Timeout!"));
    } else if (err.cause && err.cause.code === "ECONNREFUSED") {
      console.log(RED("\nNo Internet Connection!"));
    } else {
      console.log(RED(`\nError: ${err.message}`));
    }
  }
}

async function myPublicIp() {
  try {
    const response = await fetch("https://api.ipify.org", { signal: AbortSignal.timeout(5000) });
    const ip = (await response.text()).trim();
    console.log(GREEN(`\nYour Public IP: ${ip}`));
    await lookup(ip);
  } catch (err) {
    console.log(RED("Failed to fetch Public IP."));
  }
}

async function menu() {
  while (true) {
    clear();
    banner();

    console.log(YELLOW("[1] Lookup IP Address"));
    console.log(CYAN("[2] My Public IP"));
    console.log(MAGENTA("[3] About"));
    console.log(RED("[4] Exit"));

    const choice = (await ask(GREEN("\nSelect Option: "))).trim();

    if (choice === "1") {
      const ip = (await ask(CYAN("\nEnter IP Address: "))).trim();
      await lookup(ip);
      await ask(YELLOW("\nPress Enter to continue..."));
    } else if (choice === "2") {
      await myPublicIp();
      await ask(YELLOW("\nPress Enter to continue..."));
    } else if (choice === "3") {
      clear();
      banner();
      console.log(GREEN("Developer : Your Name"));
      console.log(CYAN("Version   : 2.0"));
      console.log(YELLOW("Language  : Node.js"));
      console.log(MAGENTA("API       : ip-api.com"));
      await ask(YELLOW("\nPress Enter to continue..."));
    } else if (choice === "4") {
      console.log(GREEN("\nGoodbye!\n"));
      rl.close();
      break;
    } else {
      console.log(RED("\nInvalid Option!"));
      await ask(YELLOW("\nPress Enter..."));
    }
  }
}

menu().catch(() => {
  console.log(RED("\n\nProgram Interrupted!"));
  process.exit(1);
});
