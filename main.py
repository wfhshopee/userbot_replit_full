import asyncio
import nest_asyncio
from telethon import TelegramClient, events

nest_asyncio.apply()

# ===== KONFIGURASI API =====
api_id = 23431128
api_hash = "cf803b20712a741e5cd96897fd3deb2e"
session_name = "userbot"

client = TelegramClient(session_name, api_id, api_hash)

# ===== VARIABEL GLOBAL =====
saved_forwards = {}
auto_forward_name = None
auto_broadcast_on = False
delay_seconds = 3600
text_forward = None
repeat_task = None
repeat_interval = 3600
repeat_name = None

# ===== LOG HELPER =====
def log(msg):
    print(f"[LOG] {msg}")

# ===== LOGIN MANUAL =====
async def manual_login():
    await client.connect()
    if not await client.is_user_authorized():
        phone = input("📱 Masukkan nomor Telegram (contoh: 6281234567890): ")
        await client.send_code_request(phone)
        code = input("🔑 Masukkan kode OTP Telegram: ")
        await client.sign_in(phone, code)
    log("✅ Login berhasil!")

# ===== HELP =====
HELP_TEXT = """
📖 Perintah Userbot:

..savforward <nama>    → Simpan pesan dari Saved Messages
..sendforward <nama>   → Sebar pesan manual ke semua grup
..autoforward <nama>   → Set pesan untuk auto broadcast
..autogcast on/off     → Hidupkan / Matikan auto broadcast
..setdelay <detik>     → Atur delay antar broadcast
..status               → Cek status bot
..setforward <teks>    → Simpan teks untuk forward
..showforward          → Lihat teks/media forward tersimpan
..clearforward         → Hapus semua pesan tersimpan
..repeat <nama> <detik>→ Kirim berulang tiap X detik
..stoprepeat           → Hentikan repeat
..stopbot              → Matikan bot
..restartbot           → Restart bot
..help                 → Tampilkan menu bantuan
"""

# ===== HANDLER PERINTAH =====
@client.on(events.NewMessage(pattern=r"\.\.help"))
async def handler_help(event):
    await event.reply(HELP_TEXT)
    log("Help ditampilkan")

@client.on(events.NewMessage(pattern=r"\.\.savforward (.+)"))
async def handler_savforward(event):
    if not event.is_reply:
        await event.reply("⚠️ Harus reply ke pesan di Saved Messages.")
        return
    name = event.pattern_match.group(1).strip()
    reply_msg = await event.get_reply_message()
    saved_forwards[name] = (reply_msg.chat_id, reply_msg.id)
    await event.reply(f"✅ Pesan disimpan sebagai `{name}`.")
    log(f"Savforward: {name} disimpan.")

@client.on(events.NewMessage(pattern=r"\.\.sendforward (.+)"))
async def handler_sendforward(event):
    name = event.pattern_match.group(1).strip()
    if name not in saved_forwards:
        await event.reply("⚠️ Nama tidak ditemukan.")
        return
    chat_id, msg_id = saved_forwards[name]
    await event.reply(f"📢 Menyebarkan pesan `{name}` ke semua grup...")
    success, failed = 0, 0
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await client.forward_messages(dialog.id, msg_id, chat_id)
                success += 1
                await asyncio.sleep(1)
            except:
                failed += 1
    await event.reply(f"✅ Berhasil: {success} grup | ❌ Gagal: {failed}")
    log(f"Sendforward selesai: {success} sukses, {failed} gagal")

# ===== MAIN USERBOT =====
async def main():
    await manual_login()
    print("✅ Userbot berjalan! Ketik ..help di Telegram untuk melihat semua perintah")
    await client.run_until_disconnected()

asyncio.run(main())
