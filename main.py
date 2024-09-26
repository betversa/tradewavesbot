import discord
from discord.ext import commands
import os
from flask import Flask
import threading

# Initialize the Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Ensure message content intent is enabled
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask app for keeping Replit alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

# Function to run Flask app
def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Function to start Flask in a new thread
def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.start()

# Watchlist command
@bot.command(name="watchlist")
async def watchlist(ctx, *, input_str):
    try:
        stocks = input_str.split(', ')
        message = "🚨 **Daily Watchlist** 🚨\n"

        for stock in stocks:
            stock_data = stock.split(':')
            symbol = stock_data[0].upper()
            entry = float(stock_data[1])

            # Calculate target1, target2, and stop_loss based on the entry price
            target1 = round(entry * 1.05, 2)  # 5% above entry
            target2 = round(entry * 1.10, 2)  # 10% above entry
            stop_loss = round(entry * 0.97, 2)  # 3% below entry

            message += f"**{symbol}**\n"
            message += f"Entry Above: **${entry}**\n"
            message += f"🎯 Targets: **${target1} - ${target2}**\n"
            message += f"🛑 Stop Loss: **${stop_loss}**\n\n"

        message += "@everyone"

        # Disclaimer at the bottom
        message += "⚠️ *Disclaimer: Trading stocks and cryptocurrencies is highly volatile and involves risks. Please trade responsibly and only invest what you can afford to lose.*"

        # Delete user's original message
        await ctx.message.delete()

        # Send the final watchlist message
        await ctx.send(message)

    except Exception as e:
        await ctx.send("Invalid format. Please use the format: stock_symbol:entry_price")

@bot.command(name="dailyrecap")
async def dailyrecap(ctx, *, input_str):
    try:
        stocks = input_str.split(', ')
        message = "@everyone 📊 **Daily Recap** 📊\n"
        total_percent = 0.0  # To accumulate profit or loss
        stock_count = 0  # To count valid stocks for percentage

        for stock in stocks:
            stock_data = stock.split(':')
            symbol = stock_data[0].upper()
            entry_price = float(stock_data[1])

            # Handle the 'noentry' case
            if stock_data[2].lower() == "noentry":
                message += f"⚠️ {symbol} | Did not hit entry price\n"
            else:
                # This is either a profit (max price) or stop loss case
                result_value = float(stock_data[2])
                stock_count += 1  # Count this stock for averaging

                if result_value > entry_price:  # Profit case
                    max_profit = ((result_value - entry_price) / entry_price) * 100
                    total_percent += max_profit
                    message += f"✅ {symbol} | +{max_profit:.2f}% max profit\n"
                else:  # Loss case
                    max_loss = ((entry_price - result_value) / entry_price) * 100
                    total_percent -= max_loss
                    message += f"❌ {symbol} | -{max_loss:.2f}% max loss\n"

        # Delete the user's original message
        await ctx.message.delete()

        # Send the final daily recap message
        await ctx.send(message)

    except Exception as e:
        await ctx.send("Invalid format. Please use one of the formats: "
                       "stock_symbol:entry_price:noentry or "
                       "stock_symbol:entry_price:max_price or "
                       "stock_symbol:entry_price:stop_loss")

# Run both Flask and Discord bot
keep_alive()
bot.run(os.environ['DISCORD_TOKEN'])