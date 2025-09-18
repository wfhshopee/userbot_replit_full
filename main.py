import asyncio
from telethon import TelegramClient, events
from telethon.errors import ChatWriteForbiddenError, FloodWaitError

# API ID & HASH
api_id = 23431128
api_hash = "cf803b20712a741e5cd96897fd3deb2e"

# Buat client userbot
client = TelegramClient("userbot", api_id, api_hash)

# Variabel global
saved_forwards = {}
repeat_task = None
auto_forward = False
default_delay = 2  # delay default detik
PREFIX = "."

# ===== HELP =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}help"))
async def help_cmd(event):
    help_text = f"""
📖 Daftar Perintah Userbot:

{PREFIX}help → Tampilkan bantuan
{PREFIX}ping → Cek apakah bot aktif
{PREFIX}savforward <nama> → Simpan pesan reply sebagai forward
{PREFIX}sendforward <nama> → Kirim pesan forward tersimpan
{PREFIX}autoforward on/off → Aktifkan forward otomatis
{PREFIX}repeat <detik> <teks> → Kirim teks berulang
{PREFIX}stoprepeat → Hentikan repeat
{PREFIX}broadcast <pesan> → Broadcast ke semua chat
{PREFIX}setdelay <detik> → Atur delay default
"""
    await event.respond(help_text)


# ===== PING =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}ping"))
async def ping_cmd(event):
    await event.respond("✅ Bot aktif!")


# ===== Simpan pesan forward =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}savforward (.+)"))
async def savforward_cmd(event):
    if event.is_reply:
        name = event.pattern_match.group(1)
        reply_msg = await event.get_reply_message()
        saved_forwards[name] = reply_msg
        await event.respond(f"✅ Pesan berhasil disimpan sebagai: {name}")
    else:
        await event.respond("⚠️ Reply ke pesan dulu untuk disimpan.")


# ===== Kirim pesan forward =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}sendforward (.+)"))
async def sendforward_cmd(event):
    name = event.pattern_match.group(1)
    if name in saved_forwards:
        msg = saved_forwards[name]
        try:
            await msg.forward_to(event.chat_id)
            await event.respond(f"📨 Pesan '{name}' terkirim.")
        except Exception as e:
            await event.respond(f"⚠️ Gagal kirim: {e}")
    else:
        await event.respond("⚠️ Nama pesan tidak ditemukan.")


# ===== Auto Forward ON/OFF =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}autoforward (on|off)"))
async def autoforward_cmd(event):
    global auto_forward
    action = event.pattern_match.group(1)
    auto_forward = (action == "on")
    await event.respond(f"🔄 Auto Forward: {'Aktif' if auto_forward else 'Mati'}")


# ===== Repeat pesan =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}repeat (\\d+) (.+)"))
async def repeat_cmd(event):
    global repeat_task
    delay = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)

    async def repeater():
        while True:
            try:
                await client.send_message(event.chat_id, text)
            except Exception as e:
                print(f"Gagal repeat: {e}")
            await asyncio.sleep(delay)

    if repeat_task:
        repeat_task.cancel()
    repeat_task = asyncio.create_task(repeater())
    await event.respond(f"🔁 Repeat pesan tiap {delay} detik dimulai.")


# ===== Stop repeat =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}stoprepeat"))
async def stoprepeat_cmd(event):
    global repeat_task
    if repeat_task:
        repeat_task.cancel()
        repeat_task = None
        await event.respond("⛔ Repeat dihentikan.")
    else:
        await event.respond("⚠️ Tidak ada repeat aktif.")


# ===== Broadcast ke semua chat =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}broadcast (.+)"))
async def broadcast_cmd(event):
    global default_delay
    text = event.pattern_match.group(1)
    success, failed = 0, 0
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel or dialog.is_user:
            try:
                await client.send_message(dialog.id, text)
                success += 1
                await asyncio.sleep(default_delay)
            except ChatWriteForbiddenError:
                failed += 1
                continue
            except FloodWaitError as fw:
                print(f"Tunggu {fw.seconds} detik (FloodWait).")
                await asyncio.sleep(fw.seconds)
            except Exception as e:
                failed += 1
                print(f"Gagal kirim ke {dialog.name}: {e}")
    await event.respond(
        f"✅ Broadcast selesai\n"
        f"✔️ Berhasil: {success} grup\n"
        f"❌ Gagal: {failed} grup\n"
        f"✨ Iky Ganteng 😎"
    )


# ===== Set Delay =====
@client.on(events.NewMessage(outgoing=True, pattern=f"\\{PREFIX}setdelay (\\d+)"))
async def setdelay_cmd(event):
    global default_delay
    delay = int(event.pattern_match.group(1))
    default_delay = delay
    await event.respond(f"⏱️ Delay default diatur ke {delay} detik.")


# ===== Jalankan Bot =====
async def main():
    await client.start()
    print("🚀 Userbot aktif...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
