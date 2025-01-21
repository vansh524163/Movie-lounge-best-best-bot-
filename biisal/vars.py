# (c) adarsh-goel (c) @biisal
import os
from os import getenv, environ
from dotenv import load_dotenv



load_dotenv()
bot_name = "Bɪɪsᴀʟ Fɪʟᴇ2Lɪɴᴋ Bᴏᴛ"
bisal_channel = "https://t.me/+FlSEuwbe-l03Zjhl"
bisal_grp = "https://t.me/movie_hub_094"

class Var(object):
    MULTI_CLIENT = False
    API_ID = int(getenv('API_ID', '21956488 '))
    API_HASH = str(getenv('API_HASH', '812529f879f06436925c7d62eb49f5d1'))
    BOT_TOKEN = str(getenv('BOT_TOKEN' , '6992436830:AAHxSurOyULZv-Lv2nGtB38kXeHPLsuaeCg'))
    name = str(getenv('name', 'cinema4u_vansh_bot'))
    SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', '60'))
    WORKERS = int(getenv('WORKERS', '4'))
    BIN_CHANNEL = int(getenv('BIN_CHANNEL', '-1001995168865'))
    NEW_USER_LOG = int(getenv('NEW_USER_LOG', '-1001995168865'))
    PORT = int(getenv('PORT', '9097'))
    BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
    OWNER_ID = [int(x) for x in os.environ.get("OWNER_ID", "2020224264").split()]
    NO_PORT = bool(getenv('NO_PORT', False))
    APP_NAME = None
    OWNER_USERNAME = str(getenv('OWNER_USERNAME', 'none_090'))
    if 'DYNO' in environ:
        ON_HEROKU = True
        APP_NAME = str(getenv('APP_NAME')) #dont need to fill anything here
    
    else:
        ON_HEROKU = False
    FQDN = str(getenv('FQDN', 'BIND_ADRESS:PORT')) if not ON_HEROKU or getenv('FQDN', '') else APP_NAME+'.herokuapp.com'
    HAS_SSL=bool(getenv('HAS_SSL',True))
    if HAS_SSL:
        URL = "https://{}/".format(FQDN)
    else:
        URL = "http://{}/".format(FQDN)  
    DATABASE_URL = str(getenv('DATABASE_URL', 'mongodb+srv://yewilis933:SGROmrioybQJAnWj@cluster0.96en1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
    UPDATES_CHANNEL = str(getenv('UPDATES_CHANNEL', 'bots_up')) 
    BANNED_CHANNELS = list(set(int(x) for x in str(getenv("BANNED_CHANNELS", "")).split()))   
    BAN_CHNL = list(set(int(x) for x in str(getenv("BAN_CHNL", "")).split())) 
    BAN_ALERT = str(getenv('BAN_ALERT' , '<b>ʏᴏᴜʀ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.Pʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ @none_090 ᴛᴏ ʀᴇsᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇ!!</b>'))
    DB_URI = str(getenv('DB_URI', 'mongodb+srv://yewilis933:SGROmrioybQJAnWj@cluster0.96en1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
    DB_NAME = str(getenv("DB_NAME", "Vansh"))
    SECOND_BOTUSERNAME = str(getenv("SECOND_BOTUSERNAME", "cinema4u_vansh_bot"))
    FILE_BOT_TOKEN = str(getenv('FILE_BOT_TOKEN', '6992436830:AAHxSurOyULZv-Lv2nGtB38kXeHPLsuaeCg'))
