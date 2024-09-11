import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from biisal.vars import Var
from IllegalDeveloper.secondbot_database import add_user, del_user, full_userbase, present_user

API_ID = Var.API_ID
API_HASH = Var.API_HASH
BOT_TOKEN = Var.FILE_BOT_TOKEN

IllegalDeveloper = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def is_admin(user):    
    return user.id in Var.OWNER_ID
    
# Define a function to handle incoming messages
@IllegalDeveloper.on_message(filters.command("start"))
async def start_command(client, message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    if len(message.command) != 2 or (len(message.command) == 2 and message.command[1] == "start"):
        await message.reply_text("<b>Hello! I'm A File Sender Bot 😉</b>")
        return
    msg = message.command[1]

    if msg.startswith("file"):
        _, file_id = msg.split("_", 1)
        return await client.copy_message(chat_id=message.from_user.id, from_chat_id=int(Var.BIN_CHANNEL), message_id=int(file_id))


@IllegalDeveloper.on_message(filters.command("users"))
async def get_users(client, message):
    user = message.from_user
    is_admin_user = await is_admin(user)

    if not is_admin_user:
        await message.reply_text("You Don't Permission To Use This Command.")
        return
    msg = await client.send_message(chat_id=message.chat.id, text="<b>Processing ...</b>")
    users = await full_userbase()
    await msg.edit(f"{len(users)} USers Are Useing This Bot")


@IllegalDeveloper.on_message(filters.command("broadcast"))
async def send_text(client, message):
    user = message.from_user
    is_admin_user = await is_admin(user)

    if not is_admin_user:
        await message.reply_text("You Don't Have Permission To Use This Command.")
        return
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This Will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed</u> 

Total Users: <code>{total}</code> 
Successful: <code>{successful}</code> 
Blocked Users: <code>{blocked}</code> 
Deleted Accounts: <code>{deleted}</code> 
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply("<code>Use This Command As A Replay To Any Telegram Message Without Any Spaces.</code>")
        await asyncio.sleep(8)
        await msg.delete()
