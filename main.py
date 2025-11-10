# ======================================================
# 🤖 Gopher Explore Bot
# Author: Gurlized
# Description: Telegram bot to explore live data from Gopher AI
# ======================================================

import os
import json
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === LOAD .env FILE ===
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOPHER_API_KEY = os.getenv("GOPHER_API_KEY")

# === BASIC COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await update.message.reply_text(
        "👋 *Welcome to Gopher Explore Bot!*\n\n"
        "Search live data from Twitter, Reddit, and TikTok using Gopher AI.\n\n"
        "Try typing:\n"
        "`/search AI`\n\n"
        "or `/help` to see all commands.",
        parse_mode="Markdown",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "🧠 *Available Commands:*\n\n"
        "/start — Start the bot\n"
        "/help — Show this help menu\n"
        "/info — Show bot information\n"
        "/search <keyword> — Search Gopher data by keyword",
        parse_mode="Markdown",
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot info"""
    await update.message.reply_text(
        "🤖 *Gopher Explore Bot*\n"
        "Version: 1.0.0\n"
        "Powered by [Gopher AI](https://data.gopher-ai.com)",
        parse_mode="Markdown",
    )

# === SEARCH COMMAND ===
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /search command"""
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/search <keyword>`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔎 Searching for `{query}`...", parse_mode="Markdown")

    url = "https://data.gopher-ai.com/api/v1/search/live"
    headers = {
        "Authorization": f"Bearer {GOPHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "twitter",
        "arguments": {
            "type": "searchbyquery",
            "query": query,
            "max_results": 5
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])

            if not results:
                await update.message.reply_text("⚠️ No results found or invalid response.")
                return

            message = "🔍 *Search Results:*\n\n"
            for idx, item in enumerate(results[:5], start=1):
                text = item.get("text") or str(item)
                message += f"{idx}. {text[:200]}...\n\n"

            await update.message.reply_text(message[:4000], parse_mode="Markdown")

        else:
            await update.message.reply_text(
                f"❌ API Error ({response.status_code})\n{response.text[:500]}"
            )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Request failed: {str(e)}")

# === ECHO HANDLER ===
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo any user message"""
    user_message = update.message.text
    await update.message.reply_text(f"💬 You said:\n\n_{user_message}_", parse_mode="Markdown")

# === UNKNOWN COMMAND ===
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catch unrecognized commands"""
    await update.message.reply_text("❌ Unknown command. Type /help to see available options.")

# === MAIN FUNCTION ===
def main():
    """Main function to run the bot"""
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment!")
        return

    # Create app
    app = Application.builder().token(BOT_TOKEN).build()

    # Register commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("search", search_command))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    print("🤖 Gopher Explore Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
