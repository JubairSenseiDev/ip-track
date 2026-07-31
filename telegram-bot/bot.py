import json
import logging
import ipaddress
import sys
import platform
import html
import httpx

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters,
)
from telegram.constants import ParseMode

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Configuration Loading
# -----------------------------------------------------------------------------
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        BOT_TOKEN = config.get("BOT_TOKEN")
        ADMIN_ID = config.get("ADMIN_ID")
        
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing in config.json")
except FileNotFoundError:
    logger.error("config.json file not found. Please create one with BOT_TOKEN and ADMIN_ID.")
    sys.exit(1)
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    sys.exit(1)

# -----------------------------------------------------------------------------
# Global State (In-Memory History)
# -----------------------------------------------------------------------------
# Dictionary mapping user_id -> list of successfully looked up IPs
user_history = {}

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Returns the main menu InlineKeyboardMarkup."""
    keyboard = [
        [
            InlineKeyboardButton("🌍 Lookup IP", callback_data="menu_lookup"),
            InlineKeyboardButton("🌐 My Public IP", callback_data="menu_my_ip")
        ],
        [
            InlineKeyboardButton("📜 Lookup History", callback_data="menu_history"),
            InlineKeyboardButton("ℹ️ About", callback_data="menu_about")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_result_keyboard(lat: float, lon: float) -> InlineKeyboardMarkup:
    """Returns the keyboard shown after a successful IP lookup."""
    maps_url = f"https://maps.google.com/?q={lat},{lon}"
    keyboard = [
        [InlineKeyboardButton("📍 Open Maps", url=maps_url)],
        [
            InlineKeyboardButton("🔍 Lookup Another", callback_data="menu_lookup"),
            InlineKeyboardButton("🏠 Home", callback_data="menu_home")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_home_keyboard() -> InlineKeyboardMarkup:
    """Returns a simple keyboard with just a Home button."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", callback_data="menu_home")]])

async def fetch_ip_data(ip: str) -> dict:
    """Fetches IP data from ip-api.com."""
    url = f"http://ip-api.com/json/{ip}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()

async def fetch_public_ip() -> str:
    """Fetches the bot's/host's public IP using api.ipify.org."""
    url = "https://api.ipify.org?format=json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json().get("ip")

def format_ip_data(data: dict) -> str:
    """Formats the IP-API JSON response into beautiful HTML."""
    if data.get("status") != "success":
        return f"❌ <b>Lookup Failed:</b> {html.escape(str(data.get('message', 'Unknown error')))}"

    return (
        f"<b>🌍 IP Lookup Result</b>\n\n"
        f"<b>• IP:</b> <code>{html.escape(data.get('query', 'N/A'))}</code>\n"
        f"<b>• Country:</b> {html.escape(data.get('country', 'N/A'))} "
        f"({html.escape(data.get('countryCode', 'N/A'))})\n"
        f"<b>• Region:</b> {html.escape(data.get('regionName', 'N/A'))}\n"
        f"<b>• City:</b> {html.escape(data.get('city', 'N/A'))}\n"
        f"<b>• ZIP:</b> {html.escape(data.get('zip', 'N/A'))}\n"
        f"<b>• Latitude:</b> {data.get('lat', 'N/A')}\n"
        f"<b>• Longitude:</b> {data.get('lon', 'N/A')}\n"
        f"<b>• Timezone:</b> {html.escape(data.get('timezone', 'N/A'))}\n"
        f"<b>• ISP:</b> {html.escape(data.get('isp', 'N/A'))}\n"
        f"<b>• Organization:</b> {html.escape(data.get('org', 'N/A'))}\n"
        f"<b>• ASN:</b> {html.escape(data.get('as', 'N/A'))}\n"
    )

def add_to_history(user_id: int, ip: str):
    """Adds a successful lookup to the user's history (max 10)."""
    if user_id not in user_history:
        user_history[user_id] = []
    
    # Avoid duplicate consecutive entries if needed, but for now just append
    user_history[user_id].append(ip)
    
    # Keep only the last 10
    if len(user_history[user_id]) > 10:
        user_history[user_id] = user_history[user_id][-10:]

# -----------------------------------------------------------------------------
# Handlers
# -----------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    # Reset any pending state
    context.user_data["awaiting_ip"] = False
    
    welcome_text = (
        "👋 <b>Welcome to the IP Lookup Bot!</b>\n\n"
        "I can help you find detailed information about any IPv4 or IPv6 address.\n"
        "Please select an option from the menu below:"
    )
    await update.message.reply_text(
        text=welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu_keyboard()
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == "menu_home":
        context.user_data["awaiting_ip"] = False
        text = (
            "🏠 <b>Main Menu</b>\n\n"
            "Please select an option below:"
        )
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu_keyboard()
        )

    elif data == "menu_lookup":
        context.user_data["awaiting_ip"] = True
        text = (
            "🌍 <b>Lookup IP</b>\n\n"
            "Please send me the IPv4 or IPv6 address you want to look up."
        )
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_home_keyboard()
        )

    elif data == "menu_my_ip":
        context.user_data["awaiting_ip"] = False
        await query.edit_message_text(
            text="⏳ Fetching your public IP address...",
            parse_mode=ParseMode.HTML
        )
        
        try:
            public_ip = await fetch_public_ip()
            ip_data = await fetch_ip_data(public_ip)
            
            if ip_data.get("status") == "success":
                add_to_history(user_id, public_ip)
                lat = ip_data.get("lat", 0.0)
                lon = ip_data.get("lon", 0.0)
                keyboard = get_result_keyboard(lat, lon)
            else:
                keyboard = get_home_keyboard()

            result_text = format_ip_data(ip_data)
            await query.edit_message_text(
                text=result_text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error fetching my public IP: {e}")
            await query.edit_message_text(
                text="❌ <b>An error occurred while fetching your IP data.</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=get_home_keyboard()
            )

    elif data == "menu_history":
        context.user_data["awaiting_ip"] = False
        history = user_history.get(user_id, [])
        
        if not history:
            text = "📜 <b>Lookup History</b>\n\nYou haven't looked up any IPs yet."
        else:
            text = "📜 <b>Lookup History (Last 10)</b>\n\n"
            for idx, ip in enumerate(reversed(history), 1):
                text += f"{idx}. <code>{html.escape(ip)}</code>\n"
                
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_home_keyboard()
        )

    elif data == "menu_about":
        context.user_data["awaiting_ip"] = False
        py_ver = platform.python_version()
        text = (
            "ℹ️ <b>About This Bot</b>\n\n"
            "<b>• Project:</b> Telegram IP Lookup Bot\n"
            "<b>• Developer:</b> Senior Python Developer\n"
            f"<b>• Python Version:</b> {py_ver}\n"
            "<b>• API Used:</b> ip-api.com & ipify.org\n"
            "<b>• GitHub:</b> <a href='https://github.com'>Link to Repository</a>\n"
        )
        await query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=get_home_keyboard()
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming text messages, primarily for IP input."""
    if not context.user_data.get("awaiting_ip"):
        # If the bot is not expecting an IP, just ignore or prompt them to use the menu.
        return

    user_text = update.message.text.strip()
    user_id = update.message.from_user.id

    # Validate IP
    try:
        ip_obj = ipaddress.ip_address(user_text)
        ip_str = str(ip_obj)
    except ValueError:
        await update.message.reply_text(
            text="❌ <b>Invalid IP Address.</b>\nPlease provide a valid IPv4 or IPv6 address.",
            parse_mode=ParseMode.HTML,
            reply_markup=get_home_keyboard()
        )
        return

    # Acknowledge and fetch data
    processing_msg = await update.message.reply_text(
        text=f"⏳ Looking up <code>{ip_str}</code>...",
        parse_mode=ParseMode.HTML
    )

    try:
        ip_data = await fetch_ip_data(ip_str)
        
        if ip_data.get("status") == "success":
            add_to_history(user_id, ip_str)
            lat = ip_data.get("lat", 0.0)
            lon = ip_data.get("lon", 0.0)
            keyboard = get_result_keyboard(lat, lon)
        else:
            keyboard = get_home_keyboard()

        result_text = format_ip_data(ip_data)
        await processing_msg.edit_text(
            text=result_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error fetching IP data for {ip_str}: {e}")
        await processing_msg.edit_text(
            text="❌ <b>An error occurred while fetching the IP data.</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=get_home_keyboard()
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and notify the developer/user if possible."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Optionally notify the user if the update is a valid message update
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ An unexpected error occurred. The developer has been notified.",
                reply_markup=get_home_keyboard()
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------
def main() -> None:
    """Builds the application and starts the bot."""
    logger.info("Initializing bot...")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Register global error handler
    application.add_error_handler(error_handler)

    logger.info("Bot started successfully. Polling for updates...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
