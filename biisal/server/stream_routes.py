# Taken from megadlbot_oss <https://github.com/eyaadh/megadlbot_oss/blob/master/mega/webserver/routes.py>
# Thanks to Eyaadh <https://github.com/eyaadh>
# Thanks to adarsh-goel
# (c) @biisal
import re
import time
import math
import logging
import secrets
import mimetypes

from pyrogram import Client, filters  # Ensure this import is included
from pyrogram.types import Message
from urllib.parse import quote_plus
import requests
from pyrogram.errors import FloodWait, UserNotParticipant

from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from biisal.bot import multi_clients, work_loads, StreamBot
from biisal.server.exceptions import FIleNotFound, InvalidHash
from biisal import StartTime, __version__
from ..utils.time_format import get_readable_time
from ..utils.custom_dl import ByteStreamer
from biisal.utils.render_template import render_page
from biisal.vars import Var

StreamBot = Client("my_bot")
routes = web.RouteTableDef()



class Var:
    BIN_CHANNEL = -1001234567890  # Replace with your channel ID
    CHANNEL_1 = -1001887724395  # Replace with the first channel ID
    CHANNEL_2 = -1001569815531  # Replace with the second channel ID
    UPDATES_CHANNEL = "bots_up"  # Replace with your updates channel username
    BAN_ALERT = "You are banned from using this bot."

def humanbytes(size):
    # Convert file size to a human-readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def format_name(name):
    # Format file name
    name = re.sub(r'[_\.]', ' ', name)  # Replace underscores and dots with spaces
    return re.sub(r'\s+', ' ', name).strip()  # Collapse multiple spaces into one

async def find_files(client, file_name):
    """
    Search two channels for files matching the given file name.
    """
    matched_files = []

    for channel_id in [Var.CHANNEL_1, Var.CHANNEL_2]:
        async for message in client.search_messages(chat_id=channel_id, query=file_name, limit=5):
            if message.document or message.video or message.audio:
                matched_files.append(message)
            if len(matched_files) >= 5:
                break
        if len(matched_files) >= 5:
            break

    return matched_files[:5]

@routes.get("/server1/{file_name}")
async def handle_route(request):
    file_name = request.match_info.get('file_name')
    if not file_name:
        return web.json_response({"status": "error", "message": "File name is required"}, status=400)

    # Search files in channels
    async with StreamBot:
        try:
            files = await find_files(StreamBot, file_name)
            if not files:
                return web.json_response({"status": "error", "message": "No files found"}, status=404)

            # Process files via vansh_handle_req
            response_list = []
            for file_message in files:
                response = await vansh_handle_req(StreamBot, file_message)
                response_list.append(response)

            return web.json_response({"status": "success", "files": response_list})

        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)})

async def vansh_handle_req(c: Client, m: Message):
    """
    Handles a single message and generates file details.
    """
    try:
        # Forward the message to the BIN_CHANNEL
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        # Generate Links
        stream_link = f"https://ddbots.blogspot.com/p/stream.html?link={str(log_msg.id)}/{quote_plus(format_name(log_msg.document.file_name))}"
        online_link = f"https://ddbots.blogspot.com/p/download.html?link={str(log_msg.id)}/{quote_plus(format_name(log_msg.document.file_name))}"

        # Prepare data for response
        response_data = {
            "file_name": format_name(log_msg.document.file_name),
            "file_size": humanbytes(log_msg.document.file_size),
            "stream_link": stream_link,
            "download_link": online_link,
        }

        return response_data

    except FloodWait as e:
        await asyncio.sleep(e.x)
        return {
            "status": "error",
            "message": f"Flood wait triggered, sleeping for {str(e.x)} seconds."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }




# exit()



@routes.get("/", allow_head=True)
async def root_route_handler(_):
    return web.json_response(
        {
            "server_status": "running",
            "uptime": get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + StreamBot.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("bot" + str(c + 1), l)
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "version": __version__,
        }
    )


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return web.Response(text=await render_page(id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    
    if Var.MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    logging.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("after calling get_file_properties")
    
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
