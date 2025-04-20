import sqlite3
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pycoingecko import CoinGeckoAPI

DATABASE = "bot_users.db"
OWNER_ID = **********


def setup_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            last_name=excluded.last_name
    """, (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()


def save_phone(user_id, phone):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
    conn.commit()
    conn.close()


def view_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

app = Client(
    name="TahaFarashi_bot",
    api_id=********,
    api_hash="**********************************",
    bot_token="******************************************************"
)
cg = CoinGeckoAPI()
pending_phones = {}


setup_database()

@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    save_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    await client.send_photo(
        chat_id=message.chat.id,
        photo="https://img.freepik.com/free-vector/cute-bot-say-users-hello-chatbot-greets-online-consultation_80328-195.jpg",
        caption="Hello, welcome to our bot!",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Ask", callback_data="ask"),
                    InlineKeyboardButton(text="Crypto Price", callback_data="Crypto Price"),
                    InlineKeyboardButton(text="No", callback_data="no")
                ]
            ]
        )
    )

@app.on_message(filters.command("view") & filters.private)
async def view_handler(client, message: Message):
    
    if message.from_user.id != OWNER_ID:
        await message.reply_text("You are not authorized to view this information.")
        return

    users = view_users()
    if users:
        response = "Saved Users:\n"
        for user in users:
            response += f"ID: {user[0]}, Username: {user[1]}, First Name: {user[2]}, Last Name: {user[3]}, Phone: {user[4]}\n"
    else:
        response = "No users found in the database."
    await message.reply_text(response)

@app.on_callback_query()
async def qes(client: Client, callback_query: CallbackQuery):
    if callback_query.data == "ask":
        pending_phones[callback_query.from_user.id] = True
        await client.send_message(
            callback_query.from_user.id,
            "Enter your phone number in international format, for example: +98123456789"
        )
    elif callback_query.data == "Crypto Price":
        all_price = cg.get_price(ids=['bitcoin', 'litecoin', 'ethereum'], vs_currencies='usd')
        price_message = (
            f"Crypto Price List:\n"
            f"Bitcoin (BTC): ${all_price['bitcoin']['usd']}\n"
            f"Litecoin (LTC): ${all_price['litecoin']['usd']}\n"
            f"Ethereum (ETH): ${all_price['ethereum']['usd']}\n"
        )
        await client.send_message(
            callback_query.from_user.id,
            price_message
        )

@app.on_message(filters.text & filters.private)
async def save_phone_handler(client, message: Message):
    user_id = message.from_user.id
    if user_id in pending_phones:
        pending_phones.pop(user_id)
        phone = message.text.strip()
        save_phone(user_id=user_id, phone=phone)
        await message.reply_text(f"Your phone number has been saved: {phone}")

app.run()
