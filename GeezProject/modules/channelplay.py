# Bapak kau music bot (Telegram bot project)
# Copyright (C) 2021  Papanda
# Copyright (C) 2021  A§V TEAM (Python_ARQ)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import json
import os
from os import path
from typing import Callable

import aiofiles
import aiohttp
import ffmpeg
import requests
import wget
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import Voice
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Python_ARQ import ARQ
from youtube_search import YoutubeSearch
from GeezProject.modules.play import generate_cover
from GeezProject.modules.play import arq
from GeezProject.modules.play import cb_admin_check
from GeezProject.modules.play import transcode
from GeezProject.modules.play import convert_seconds
from GeezProject.modules.play import time_to_seconds
from GeezProject.modules.play import changeImageSize
from GeezProject.config import BOT_NAME as bn
from GeezProject.config import DURATION_LIMIT
from GeezProject.config import UPDATES_CHANNEL as updateschannel
from GeezProject.config import que
from GeezProject.function.admins import admins as a
from GeezProject.helpers.errors import DurationLimitError
from GeezProject.helpers.decorators import errors
from GeezProject.helpers.admins import get_administrators
from GeezProject.helpers.channelmusic import get_chat_id
from GeezProject.helpers.decorators import authorized_users_only
from GeezProject.helpers.filters import command, other_filters
from GeezProject.helpers.gets import get_file_name
from GeezProject.services.callsmusic import callsmusic
from GeezProject.services.callsmusic.callsmusic import client as USER
from GeezProject.services.converter.converter import convert
from GeezProject.services.downloaders import youtube
from GeezProject.services.queues import queues

chat_id = None



@Client.on_message(filters.command(["channelplaylist","cplaylist"]) & filters.group & ~filters.edited)
async def playlist(client, message):
    try:
      lel = await client.get_chat(message.chat.id)
      lol = lel.linked_chat.id
    except:
      message.reply("Bentar...")
      return
    global que
    queue = que.get(lol)
    if not queue:
        await message.reply_text("Bapak kau jelek")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "**Oke gua nyanyi** in {}".format(lel.linked_chat.title)
    msg += "\n- " + now_playing
    msg += "\noh elu yg request " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**Antri**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n- {name}"
            msg += f"\nOh elu yg request {usr}\n"
    await message.reply_text(msg)


# ============================= Settings =========================================


def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.pytgcalls.active_calls:
        # if chat.id in active_chats:
        stats = "Disetting dulu **{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "Volume : {}%\n".format(vol)
            stats += "Antrian Lagu : `{}`\n".format(len(que))
            stats += "Gua nyanyi : **{}**\n".format(queue[0][0])
            stats += "Nih yg request : {}".format(queue[0][1].mention)
    else:
        stats = None
    return stats


def r_ply(type_):
    if type_ == "play":
        pass
    else:
        pass
    mar = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏹", "cstop"),
                InlineKeyboardButton("⏸", "cpause"),
                InlineKeyboardButton("▶️", "cresume"),
                InlineKeyboardButton("⏭", "cskip"),
            ],
            [
                InlineKeyboardButton("Daftar lagu", "cplaylist"),
            ],
            [InlineKeyboardButton("Tutuplah", "ccls")],
        ]
    )
    return mar


@Client.on_message(filters.command(["channelcurrent","ccurrent"]) & filters.group & ~filters.edited)
async def ee(client, message):
    try:
      lel = await client.get_chat(message.chat.id)
      lol = lel.linked_chat.id
      conv = lel.linked_chat
    except:
      await message.reply("Bentar...")
      return
    queue = que.get(lol)
    stats = updated_stats(conv, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("Gak ada vcg aktif disini cuy")


@Client.on_message(filters.command(["channelplayer","cplayer"]) & filters.group & ~filters.edited)
@authorized_users_only
async def settings(client, message):
    playing = None
    try:
      lel = await client.get_chat(message.chat.id)
      lol = lel.linked_chat.id
      conv = lel.linked_chat
    except:
      await message.reply("Bentar...")
      return
    queue = que.get(lol)
    stats = updated_stats(conv, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause"))

        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("GAK ADA VCG AKTIF DISINI")


@Client.on_callback_query(filters.regex(pattern=r"^(cplaylist)$"))
async def p_cb(b, cb):
    global que
    try:
      lel = await client.get_chat(cb.message.chat.id)
      lol = lel.linked_chat.id
      conv = lel.linked_chat
    except:
      return    
    que.get(lol)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(lol)
        if not queue:
            await cb.message.edit("Bapak kau jelek")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**Gua nyanyi** in {}".format(conv.title)
        msg += "\n- " + now_playing
        msg += "\nNih yang request jelek " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Antrian**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\nYang request jelek {usr}\n"
        await cb.message.edit(msg)


@Client.on_callback_query(
    filters.regex(pattern=r"^(cplay|cpause|cskip|cleave|cpuse|cresume|cmenu|ccls)$")
)
@cb_admin_check
async def m_cb(b, cb):
    global que
    if (
        cb.message.chat.title.startswith("Channel Music: ")
        and chat.title[14:].isnumeric()
    ):
        chet_id = int(chat.title[13:])
    else:
      try:
        lel = await b.get_chat(cb.message.chat.id)
        lol = lel.linked_chat.id
        conv = lel.linked_chat
        chet_id = lol
      except:
        return
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat
    

    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "cpause":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Chat nya gak connect goblok", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Halah bodo, yaudah gua diem")
            await cb.message.edit(
                updated_stats(conv, qeue), reply_markup=r_ply("play")
            )

    elif type_ == "cplay":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Chat nya gak connect goblok", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Lanjut nyanyi")
            await cb.message.edit(
                updated_stats(conv, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "cplaylist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Bapak kau jelek")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**Gua nyanyi** in {}".format(cb.message.chat.title)
        msg += "\n- " + now_playing
        msg += "\nYang request jelek" + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Antrian**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\nYang request jelek {usr}\n"
        await cb.message.edit(msg)

    elif type_ == "cresume":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Chat nya gak connect atau ini lagi gua nyanyiin", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("Ini gua lanjut nyanyi cok")
    elif type_ == "cpuse":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Chat nya gak connect atau ini lagi gua nyanyiin", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Oke gua diem asu")
    elif type_ == "ccls":
        await cb.answer("Iya bacot. ini gua tutup")
        await cb.message.delete()

    elif type_ == "cmenu":
        stats = updated_stats(conv, qeue)
        await cb.answer("Menu opened")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏹", "cstop"),
                    InlineKeyboardButton("⏸", "cpuse"),
                    InlineKeyboardButton("▶️", "cresume"),
                    InlineKeyboardButton("⏭", "cskip"),
                ],
                [
                    InlineKeyboardButton("Daftar lagu", "cplaylist"),
                ],
                [InlineKeyboardButton("Tutup aja", "ccls")],
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)
    elif type_ == "cskip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Chat nya gak connect cok", show_alert=True)
        else:
            callsmusic.queues.task_done(chet_id)

            if callsmusic.queues.is_empty(chet_id):
                callsmusic.pytgcalls.leave_group_call(chet_id)

                await cb.message.edit("Males ah gak ada yang request\nGua turun ajalah anjing")
            else:
                callsmusic.pytgcalls.change_stream(
                    chet_id, callsmusic.queues.get(chet_id)["file"]
                )
                await cb.answer("cekip")
                await cb.message.edit((m_chat, qeue), reply_markup=r_ply(the_data))
                await cb.message.reply_text(
                    f"Iya ini gua skip cok\nNih gua nyanyiin lagi tot **{qeue[0][0]}**"
                )

    else:
        if chet_id in callsmusic.pytgcalls.active_calls:
            try:
                callsmusic.queues.clear(chet_id)
            except QueueEmpty:
                pass

            callsmusic.pytgcalls.leave_group_call(chet_id)
            await cb.message.edit("Ngentot, malah ngusir gua si memek")
        else:
            await cb.answer("Chat nya gak connect cok", show_alert=True)


@Client.on_message(filters.command(["channelplay","cplay"])  & filters.group & ~filters.edited)
@authorized_users_only
async def play(_, message: Message):
    global que
    lel = await message.reply(" **Sabar ya syg**")

    try:
      conchat = await _.get_chat(message.chat.id)
      conv = conchat.linked_chat
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("ha maksud?")
      return
    try:
      administrators = await get_administrators(conv)
    except:
      await message.reply("Gua udah dijadiin admin belom si cok?")
    try:
        user = await USER.get_me()
    except:
        user.first_name = "helper"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>Jangan lupa tambahin kawan gua</b>",
                    )
                    pass

                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Jadiin gua admin di channel lo goblok</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        "<b>Akhirnya kawan gua udah masuk juga</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b> error blok goblok \nUser {user.first_name} kan error, jangan banyak bacot maknaya kontol, jangan jangan kawan gua dibanned cok"
                        "\n\nAtau lu tambahin sendiri deh kawan gua kemari</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> {user.first_name} Kawan gua gak disini, suruh admin pake cmd /play atau tambahinn kawam gua {user.first_name} sendiri</i>"
        )
        return
    message.from_user.id
    text_links = None
    message.from_user.first_name
    await lel.edit("🔎 **Bentar asu, gua cariin dulu**")
    message.from_user.id
    user_id = message.from_user.id
    message.from_user.first_name
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    if message.reply_to_message:
        entities = []
        toxt = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.entities:
            entities = message.reply_to_message.entities + entities
        elif message.reply_to_message.caption_entities:
            entities = message.reply_to_message.entities + entities
        urls = [entity for entity in entities if entity.type == 'url']
        text_links = [
            entity for entity in entities if entity.type == 'text_link'
        ]
    else:
        urls=None
    if text_links:
        urls = True    
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"Jangaj request yang kelamaan goblok, jgn lebih dari {DURATION_LIMIT} menit(s) atau gak baklan gua nyanyiin"
            )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Daftar Lagu", callback_data="cplaylist"),
                    InlineKeyboardButton("Menu ", callback_data="cmenu"),
                ],
                [InlineKeyboardButton(text="tutup aja ah", callback_data="ccls")],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/f6086f8909fbfeb0844f2.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("🎵 **sabar ya memek**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "Lu request apaan dah?. kaga nemu gua su!"
            )
            print(str(e))
            return
        dlurl = url
        dlurl=dlurl.replace("youtube","youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Daftar Lagu", callback_data="cplaylist"),
                    InlineKeyboardButton("Menu ", callback_data="cmenu"),
                ],
                [
                    InlineKeyboardButton(text="🎬 YouTube", url=f"{url}"),
                    InlineKeyboardButton(text="Download 📥", url=f"{dlurl}"),
                ],
                [InlineKeyboardButton(text="Tutup aja ah", callback_data="ccls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))        
    else:
        query = ""
        for i in message.command[1:]:
            query += " " + str(i)
        print(query)
        await lel.edit("🎵 **Bentar...**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "Lu request apaan dah?. Kaga nemu gua cok"
            )
            print(str(e))
            return

        dlurl = url
        dlurl=dlurl.replace("youtube","youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Daftar Lagu", callback_data="cplaylist"),
                    InlineKeyboardButton("Menu ", callback_data="cmenu"),
                ],
                [
                    InlineKeyboardButton(text="🎬 YouTube", url=f"{url}"),
                    InlineKeyboardButton(text="Download 📥", url=f"{dlurl}"),
                ],
                [InlineKeyboardButton(text="Tutup aja ah", callback_data="ccls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))
    chat_id = chid
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption=f"#⃣ Requestan lu  **Ngantri** di urutan ke {position}!",
            reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        chat_id = chid
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption=" **Gua nyanyiin** the song requested by {} via nyolong".format(
                message.from_user.mention()
            ),
        )
        os.remove("final.png")
        return await lel.delete()


@Client.on_message(filters.command(["channeldplay","cdplay"]) & filters.group & ~filters.edited)
@authorized_users_only
async def deezer(client: Client, message_: Message):
    global que
    lel = await message_.reply(" **Sabar...**")

    try:
      conchat = await client.get_chat(message_.chat.id)
      conid = conchat.linked_chat.id
      conv = conchat.linked_chat
      chid = conid
    except:
      await message_.reply("Bapak kau jelek")
      return
    try:
      administrators = await get_administrators(conv)
    except:
      await message.reply("Gua udah dijadiin admin belom sih?") 
    try:
        user = await USER.get_me()
    except:
        user.first_name = "musiknya bapak kau"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>Jangan lupa tambahin kawan gua kemari</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Jadiin gua dmin dulu lah ngentot</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        "<b>Akhirnya kawan gua masuk sini</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>ngeleg cok \nkawan gua ini {user.first_name} Kaga bisa masuk sini, apa jangan jangan udah lu banned"
                        "\n\nKalo lu mau nambahin dia sendiri yaudah si</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i> {user.first_name} Kawan gua gak disini, Suruh admin lu buat ketik cmd /play atau tambahin kawan guanini {user.first_name} sendiri</i>"
        )
        return
    requested_by = message_.from_user.first_name

    text = message_.text.split(" ", 1)
    queryy = text[1]
    query=queryy
    res = lel
    await res.edit(f"Bentar gua nyari `{queryy}` di pasar")
    try:
        songs = await arq.deezer(query,1)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        title = songs.result[0].title
        url = songs.result[0].url
        artist = songs.result[0].artist
        duration = songs.result[0].duration
        thumbnail = songs.result[0].thumbnail
    except:
        await res.edit("Kaga nemu apa apa gua. pake bahasa inggris lah tot kan gua orang jepang")
        return
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Daftar Lagu", callback_data="cplaylist"),
                InlineKeyboardButton("Me", callback_data="cmenu"),
            ],
            [InlineKeyboardButton(text="Dengerin di pasar", url=f"{url}")],
            [InlineKeyboardButton(text="Tutup aja ah", callback_data="ccls")],
        ]
    )
    file_path = await convert(wget.download(url))
    await res.edit("Sabar mek")
    await generate_cover(requested_by, title, artist, duration, thumbnail)
    chat_id = chid
    if chat_id in callsmusic.pytgcalls.active_calls:
        await res.edit("Gua tambahin ke antrian")
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.edit_text(f"{bn}= #️masuk antrian nomor {position}")
    else:
        await res.edit_text(f"{bn}=▶️ nyanyi")

        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        callsmusic.pytgcalls.join_group_call(chat_id, file_path)

    await res.delete()

    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"nyanyi [{title}]({url}) cover suara gua sangat amat merdu",
    )
    os.remove("final.png")


@Client.on_message(filters.command(["channelsplay","csplay"]) & filters.group & ~filters.edited)
@authorized_users_only
async def jiosaavn(client: Client, message_: Message):
    global que
    lel = await message_.reply("🔄 **Bentar...**")
    try:
      conchat = await client.get_chat(message_.chat.id)
      conid = conchat.linked_chat.id
      conv = conchat.linked_chat
      chid = conid
    except:
      await message_.reply("Bapak kau jelek")
      return
    try:
      administrators = await get_administrators(conv)
    except:
      await message.reply("Gua udah di adminin belom si")
    try:
        user = await USER.get_me()
    except:
        user.first_name = "Musiknya nyokap lu"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        "<b>Jangan lupa tambahin kawan gua kemari</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Jadiin gua admin dulu cok</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        "<b>Akhirnya kawan gua masuk sini juga</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>Kok lag cok?\ndia {user.first_name} kaga bisa masuk sini, apa jangan jangan lu banned kawan hua"
                        "\n\nAtau masukin sendiri dah kemari </b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            "<i> Kawan gua gak ada dimari, buruan add dia kemari biar bisa gua nyayiin</i>"
        )
        return
    requested_by = message_.from_user.first_name
    chat_id = message_.chat.id
    text = message_.text.split(" ", 1)
    query = text[1]
    res = lel
    await res.edit(f"Lagi nyari `{query}` di selokan")
    try:
        songs = await arq.saavn(query)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        sname = songs.result[0].song
        slink = songs.result[0].media_url
        ssingers = songs.result[0].singers
        sthumb = "https://telegra.ph/file/f6086f8909fbfeb0844f2.png"
        sduration = int(songs.result[0].duration)
    except Exception as e:
        await res.edit("Gak nemu apa apa gua, makanya pake bahasa inggris tot kan gua dari jepang")
        print(str(e))
        return
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Daftar Lagu", callback_data="cplaylist"),
                InlineKeyboardButton("Menu", callback_data="cmenu"),
            ],
            [
                InlineKeyboardButton(
                    text="Join Updates Channel", url=f"https://t.me/asupanviralid"
                )
            ],
            [InlineKeyboardButton(text="Tutup", callback_data="ccls")],
        ]
    )
    file_path = await convert(wget.download(slink))
    chat_id = chid
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = sname
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.delete()
        m = await client.send_photo(
            chat_id=message_.chat.id,
            reply_markup=keyboard,
            photo="final.png",
            caption=f"{bn}=#️Masuk antrian nomor {position}",
        )

    else:
        await res.edit_text(f"{bn}=Lagi nyannyi")
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = sname
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        callsmusic.pytgcalls.join_group_call(chat_id, file_path)
    await res.edit("Generating Thumbnail.")
    await generate_cover(requested_by, sname, ssingers, sduration, sthumb)
    await res.delete()
    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"Lagi nyanyi {sname} Cover auara gua yang sangat amat merdu ini",
    )
    os.remove("final.png")


# Have u read all. If read RESPECT :-)
