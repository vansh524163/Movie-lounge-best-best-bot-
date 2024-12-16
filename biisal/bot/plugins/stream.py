import os
import asyncio
import requests
import re
import time
from asyncio import TimeoutError
from biisal.bot import StreamBot
from biisal.utils.database import Database
from biisal.utils.human_readable import humanbytes
from biisal.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from biisal.utils.file_properties import get_name, get_hash, get_media_file_size

# Database Initialization
db = Database(Var.DATABASE_URL, Var.name)
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

# Environment Variables
MY_PASS = os.environ.get("MY_PASS", None)

# Template for Message Text
msg_text = """<b>‣ ʏᴏᴜʀ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ! 😎

‣ Fɪʟᴇ ɴᴀᴍᴇ : <i>{}</i>
‣ Fɪʟᴇ ꜱɪᴢᴇ : {}

🔻<a href="{}">𝗙𝗔𝗦𝗧 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗</a>
🔺 <a href="{}">𝗪𝗔𝗧𝗖𝗛 𝗢𝗡𝗟𝗜𝗡𝗘</a>

‣ ɢᴇᴛ <a href="https://t.me/bots_up">ᴍᴏʀᴇ ғɪʟᴇs</a></b> 🤡"""




# Replace with your actual values
class Var:
    BIN_CHANNEL = -1001626107740  # Replace with your BIN_CHANNEL ID
    SECOND_BOTUSERNAME = "File_Press_bot"  # Replace with your bot username

cancel_tasks = False 

@StreamBot.on_message(filters.command("vansh"))
async def handle_vansh_command(c: Client, m):
    global cancel_tasks
    cancel_tasks = False  # Reset cancel flag
    try:
        start_time = time.time()  # Record start time for the process

        # Extract the channel username or ID from the user command
        match = re.search(r"t\.me/(?P<username>[\w\d_]+)", m.text)
        if not match:
            await m.reply_text("Invalid link. Please send a valid Telegram channel link.")
            return

        username_or_id = match.group("username")

        # Determine chat ID
        chat_id = int("-100" + username_or_id) if username_or_id.isdigit() else username_or_id

        # Verify accessibility of the chat
        try:
            chat = await c.get_chat(chat_id)
            await m.reply_text(f"Processing all media files from channel: {chat.title}")
        except Exception as e:
            await m.reply_text(f"Failed to access the chat: {e}")
            return

        # Fetch all messages in the channel
        batch_size = 100  # Number of messages to fetch per batch
        total_limit = 10000  # Total messages to process (adjustable)
        processed_count = 0
        messages = []
        last_message_id = None

        status_message = await m.reply_text(Starting to process files...)
        cancel_button_message = await m.reply_text("Click here to cancel", reply_markup={"inline_keyboard": [[{"text": "Cancel", "callback_data": "cancel"}]]})

        while processed_count < total_limit:
            if cancel_tasks:
                await status_message.edit_text("Process cancelled by user.")
                return

            elapsed_time = int(time.time() - start_time)  # Calculate elapsed time
            try:
                # Fetch a batch of messages
                batch = await c.get_history(chat_id, limit=batch_size, offset_id=last_message_id)
                if not batch:
                    break

                # Filter messages containing media
                media_messages = [msg for msg in batch if hasattr(msg, "media") and msg.media]
                messages.extend(media_messages)
                processed_count += len(media_messages)

                # Update last_message_id for the next batch
                last_message_id = batch[-1].message_id

                # Update status message in real-time
                await status_message.edit_text(
                    f"Processing files...\n\n"
                    f"**Elapsed Time:** {elapsed_time}s\n"
                    f"**Files Processed:** {processed_count}\n"
                    f"**Current Batch Size:** {len(media_messages)}"
                )

                # Stop if no more messages
                if len(batch) < batch_size:
                    break
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await status_message.edit_text(
                    f"**FloodWait Detected**: Retrying after {e.value} seconds..."
                )
            except Exception as e:
                await status_message.edit_text(f"Error during batch fetch: {e}")
                break

        if not messages:
            await status_message.edit_text("No media files found.")
            return

        # Concurrently process files
        total_files = len(messages)
        semaphore = asyncio.Semaphore(10)  # Limit concurrent tasks to 10

        async def process_file(msg, file_num):
            async with semaphore:
                try:
                    await process_message(c, m, msg)
                except Exception as e:
                    await m.reply_text(f"Error in file #{file_num}: {e}")

        tasks = [process_file(msg, i + 1) for i, msg in enumerate(messages)]
        await asyncio.gather(*tasks)

        total_time = int(time.time() - start_time)
        await status_message.edit_text(
            f"Successfully processed {total_files} files in {total_time}s."
        )
    except Exception as e:
        await m.reply_text(f"An error occurred: {e}")

@StreamBot.on_callback_query()
async def handle_cancel_callback(c: Client, cb):
    global cancel_tasks
    if cb.data == "cancel":
        cancel_tasks = True
        await cb.answer("Processing cancelled.")

def get_name(msg):
    if hasattr(msg, "document") and msg.document:
        return msg.document.file_name
    elif hasattr(msg, "video") and msg.video:
        return msg.video.file_name
    return "Unknown"

async def process_message(c: Client, m, msg):
    try:
        # Forward the message to the BIN_CHANNEL
        log_msg = await msg.forward(chat_id=Var.BIN_CHANNEL)

        # Generate links for the forwarded message
        file_name = get_name(log_msg)
        stream_link = f"https://ddbots.blogspot.com/p/stream.html?link={log_msg.id}/{quote_plus(file_name)}?hash={get_hash(log_msg)}"
        online_link = f"https://ddbots.blogspot.com/p/download.html?link={log_msg.id}/{quote_plus(file_name)}?hash={get_hash(log_msg)}"
        file_link = f"https://telegram.me/{Var.SECOND_BOTUSERNAME}?start=file_{log_msg.id}"
        share_link = f"https://ddlink57.blogspot.com/{str(log_msg.id)}/{quote_plus(file_name)}?hash={get_hash(log_msg)}"

        # Format file name for a cleaner display
        formatted_name = re.sub(r'[_\.]', ' ', file_name).strip()

        # Prepare data payload for API request
        data = {
            "file_name": formatted_name,
            "share_link": share_link
        }

        # Send data to the external API
        response = requests.post("https://movietop.link/upcoming-movies", json=data, timeout=10)
        if response.status_code != 200:
            print(f"API error ({response.status_code}): {response.text}")

    except requests.exceptions.RequestException as req_error:
        # Handle network errors during the API call
        await m.reply_text(f"Network error while sending data to API: {req_error}")
    except Exception as e:
        # General exception handling for other errors
        await m.reply_text(f"Error processing message: {e}")






# Handler for Private Messages
@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    try:
        # Check if the user exists in the database, if not, add them
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id)
            await c.send_message(
                Var.BIN_CHANNEL,
                f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!"
            )

        # Check for updates channel subscription
        if Var.UPDATES_CHANNEL != "None":
            try:
                user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
                if user.status == "kicked":
                    await c.send_message(
                        chat_id=m.chat.id,
                        text="You are banned!\n\n  **Contact Support [Support](https://t.me/Movielounge_File_Bot), They Will Help You**",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                await c.send_photo(
                    chat_id=m.chat.id,
                    photo="https://telegra.ph/file/5eb253f28ed7ed68cb4e6.png",
                    caption="""<b>Hey there!\n\nPlease join our updates channel to use me! 😊\n\nDue to server overload, only our channel subscribers can use this bot!</b>""",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Join Now 🚩", url=f"https://t.me/{Var.UPDATES_CHANNEL}")]
                        ]
                    ),
                )
                return
            except Exception as e:
                await m.reply_text(f"Error: {str(e)}")
                return

        # Check if the user is banned
        ban_chk = await db.is_banned(int(m.from_user.id))
        if ban_chk:
            return await m.reply(Var.BAN_ALERT)

        # Forward the message to the BIN_CHANNEL
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        # Generate Links
        stream_link = f"https://ddbots.blogspot.com/p/stream.html?link={str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"https://ddbots.blogspot.com/p/download.html?link={str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        file_link = f"https://telegram.me/{Var.SECOND_BOTUSERNAME}?start=file_{log_msg.id}"
        share_link = f"https://ddlink57.blogspot.com/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        
        url = "https://movietop.link/upcoming-movies"
        
        name = format(get_name(log_msg));
        formatted_name = re.sub(r'[_\.]', ' ', name)  # Replace underscores and dots with spaces
        formatted_name = re.sub(r'\s+', ' ', formatted_name).strip()  # Collapse multiple spaces into one


        data = {
            "file_name": formatted_name,
            "share_link": share_link,
        }
        response = requests.post(url, json=data)

    

        # Reply to the user
        await m.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m)), online_link, stream_link),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Stream 🔺", url=stream_link),
                        InlineKeyboardButton('Download 🔻', url=online_link)
                    ],
                    [
                        InlineKeyboardButton('⚡ Share Link ⚡', url=share_link)
                    ],
                    [
                        InlineKeyboardButton('Get File', url=file_link)
                    ]
                ]
            )
        )

        await m.reply_text(
        text="✅ Your request has been processed successfully. Please use the above buttons to proceed!",
        quote=True
    )
        

    except FloodWait as e:
        print(f"Sleeping for {str(e.x)} seconds due to FloodWait")
        await asyncio.sleep(e.x)
    except Exception as e:
        await m.reply_text(f"An error occurred: {e}")

# Handler for Channel Messages
@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BAN_CHNL:
        print("Chat trying to get streaming link is in BAN_CHNL, skipping.")
        return
    ban_chk = await db.is_banned(int(broadcast.chat.id))
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS or ban_chk:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        await log_msg.reply_text(
            text=f"**Channel Name:** `{broadcast.chat.title}`\n**CHANNEL ID:** `{broadcast.chat.id}`\n**Request URL:** {stream_link}",
            quote=True
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Stream 🔺", url=stream_link),
                        InlineKeyboardButton('Download 🔻', url=online_link)
                    ]
                ]
            )
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)} seconds due to FloodWait")
        await asyncio.sleep(w.x)
    except Exception as e:
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"**#ERROR_TRACEBACK:** `{e}`",
            disable_web_page_preview=True
        )
        print(f"Error: {e}. Ensure proper permissions in BIN_CHANNEL.")
