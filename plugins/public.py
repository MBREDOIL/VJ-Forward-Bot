# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
import asyncio 
from .utils import STS
from database import Db, db
from config import temp 
from script import Script
from config import Config
from pyrogram import Client, filters, enums
from pyrogram.enums import ChatAction
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChatAdminRequired
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate as PrivateChat
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified, ChannelPrivate
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def forward_messages(client: Client, message: Message, target_chat_id: int):
    """एक्सेप्शन हैंडलिंग के साथ मैसेज फॉरवर्ड करे"""
    try:
        # Try forwarding first
        await message.forward(target_chat_id)
    except Exception as e:
        # If forwarding fails, try copying
        try:
            await message.copy(target_chat_id)
        except Exception as copy_error:
            print(f"Failed to copy message: {copy_error}")
            await message.reply(f"❌ Failed to forward/copy message: {copy_error}")


@Client.on_message(filters.private & filters.command(["forward"]))
async def run(bot, message):
    user_id = message.from_user.id
    
    # Authorization Check (Owner and Sudo)
    if user_id != Config.BOT_OWNER and not await db.is_sudo(user_id):
        return await message.reply("<b>🚫 This command is not allowed to use!</b>")
    buttons = []
    btn_data = {}
    user_id = message.from_user.id
    _bot = await db.get_bot(user_id)
    if not _bot:
      _bot = await db.get_userbot(user_id)
      if not _bot:
          return await message.reply("<code>You didn't added any bot. Please add a bot using /settings !</code>")
    channels = await db.get_user_channels(user_id)
    if not channels:
       return await message.reply_text("please set a to channel in /settings before forwarding")
    if len(channels) > 1:
       for channel in channels:
          buttons.append([KeyboardButton(f"{channel['title']}")])
          btn_data[channel['title']] = channel['chat_id']
       buttons.append([KeyboardButton("cancel")]) 
       _toid = await bot.ask(message.chat.id, Script.TO_MSG.format(_bot['name'], _bot['username']), reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
       if _toid.text.startswith(('/', 'cancel')):
          return await message.reply_text(Script.CANCEL, reply_markup=ReplyKeyboardRemove())
       to_title = _toid.text
       toid = btn_data.get(to_title)
       if not toid:
          return await message.reply_text("wrong channel choosen !", reply_markup=ReplyKeyboardRemove())
    else:
       toid = channels[0]['chat_id']
       to_title = channels[0]['title']
    fromid = await bot.ask(message.chat.id, Script.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'):
        await message.reply(Script.CANCEL)
        return 
    if fromid.text and not fromid.forward_date:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text.replace("?single", ""))
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif fromid.forward_from_chat.type in [enums.ChatType.CHANNEL, 'supergroup']:
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
        if last_msg_id == None:
           return await message.reply_text("**This may be a forwarded message from a group and sended by anonymous admin. instead of this please send last message link from group**")
    else:
        await message.reply_text("**invalid !**")
        return 
    try:
        title = (await bot.get_chat(chat_id)).title
  #  except ChannelInvalid:
        #return await fromid.reply("**Given source chat is copyrighted channel/group. you can't forward messages from there**")
    except (PrivateChat, ChannelPrivate, ChannelInvalid):
        title = "private" if fromid.text else fromid.forward_from_chat.title
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')
    skipno = await bot.ask(message.chat.id, Script.SKIP_MSG)
    if skipno.text.startswith('/'):
        await message.reply(Script.CANCEL)
        return
    forward_id = f"{user_id}-{skipno.id}"
    buttons = [[
        InlineKeyboardButton('Yes', callback_data=f"start_public_{forward_id}"),
        InlineKeyboardButton('No', callback_data="close_btn")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=Script.DOUBLE_CHECK.format(botname=_bot['name'], botuname=_bot['username'], from_chat=title, to_chat=to_title, skip=skipno.text),
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    STS(forward_id).store(chat_id, toid, int(skipno.text), int(last_msg_id))

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01



# Owner के लिए Sudo Add/Remove Commands
@Client.on_message(filters.command("addsudo") & filters.user(Config.BOT_OWNER))
async def add_sudo_user(_, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ **Usage:** /addsudo user_id")
    
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply("❌ **Invalid user ID.**")
    
    if await db.is_sudo(user_id):
        return await message.reply("ℹ️ The user is already Sudo.")
    
    await db.add_sudo(user_id)
    try:
        user = await Client.get_users(user_id)
        await message.reply(f"✅ {user.mention} has been made a sudo user!")
    except Exception as e:
        await message.reply(f"✅ {user_id} has been made a sudo user, but could not fetch user details. Error: {str(e)}")
    
@Client.on_message(filters.command("delsudo") & filters.user(Config.BOT_OWNER))
async def remove_sudo_user(_, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ **Usage:** /delsudo user_id")
    
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply("❌ **Invalid user ID.**")
    
    if not await db.is_sudo(user_id):
        return await message.reply("ℹ️ User is not a Sudo user.")
    
    await db.remove_sudo(user_id)
    await message.reply(f"✅ The user {user_id }'s Sudo access has been removed.")

# To see the list of all Sodo users
@Client.on_message(filters.command("sudolist") & filters.user(Config.BOT_OWNER))
async def list_sudo_users(_, message):
    sudo_users = await db.get_all_sudo()
    text = "📜 **List of Sudo Users:**\n\n"
    
    for user_id in sudo_users:
        try:
            user = await Client.get_users(user_id)
            text += f"• {user.mention} (`{user_id}`)\n"
        except:
            text += f"• Unknown User (`{user_id}`)\n"
    
    await message.reply(text)

@Client.on_message(filters.command(["startforward"]) & filters.user(Config.BOT_OWNER))
async def start_forwarding(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ **Usage:** /startforward channel_id\nExample: /startforward -100123456789")
    
    try:
        target_chat_id = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Invalid Channel ID. Must be integer like -100123456789")
    
    # Check if bot can send messages in target channel
    try:
        send_message = await client.send_message(chat_id=target_chat_id, text="Testing message")

    except ChatAdminRequired:
        return await message.reply("❌ Bot needs admin permissions in the target channel!")
    except Exception as e:
        return await message.reply(f"❌ Bot doesn't have access to target channel: {e}")
    
    await db.start_forward_session(message.from_user.id, target_chat_id)
    await message.reply(f"✅ Auto Forward Started!\nAll messages will be sent to: {target_chat_id}")

@Client.on_message(filters.command(["stopforward"]) & filters.user(Config.BOT_OWNER))
async def stop_forwarding(_, message):
    await db.stop_forward_session(message.from_user.id)
    await message.reply("❌ Auto Forwarding Stopped!")

@Client.on_message(filters.all & ~filters.service & ~filters.me)
async def handle_all_messages(client, message):
    # Check if any active forward session
    forward_session = await db.get_forward_session(message.from_user.id)
    if forward_session or forward_session.get('is_active'):

            # फॉरवर्डिंग को अलग टास्क में रन करें
            asyncio.create_task(
                forward_messages(client, message, forward_session['target_chat_id'])
            )
