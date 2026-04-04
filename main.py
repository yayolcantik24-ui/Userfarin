import asyncio
import random
import os
from datetime import datetime
from pyrogram import Client, enums, errors

# --- AMBIL DARI VARIABLES RAILWAY ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
LOG_CHANNEL = "@farinmodssv2"

# --- KONTEN PROMOSI ---
PROMO_TEXT = (
"📱 **NOKOS MURAH & INSTAN** 📱\n\n• Harga mulai Rp900\n• Banyak pilihan aplikasi\n• Auto refund saldo jika OTP tidak masuk\n• Deposit QRIS otomatis\n• Proses cepat & stabil\n\n🕘 Admin online 24/7\n⚡ Fast respon\n\n🤖 Bot order: @farinshop_bot\n🚀 **Langsung gas order sekarang!**"
)

app = Client(
    "farin_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def send_log(text):
    """Kirim laporan ke @farinmodssv2"""
    try:
        now = datetime.now().strftime("%H:%M")
        await app.send_message(LOG_CHANNEL, f"📝 **LOG USERBOT** [{now}]\n{text}")
    except Exception as e:
        print(f"Gagal kirim log: {e}")

async def auto_promo():
    async with app:
        await send_log("✅ **Userbot Farin Shop Aktif!**\nSistem siap memproses 300+ grup.")
        
        while True:
            # 1. FITUR AUTO SCAN GRUB
            groups = []
            async for dialog in app.get_dialogs():
                if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    groups.append(dialog.chat.id)
            
            total_grup = len(groups)
            await send_log(f"🔍 Scan Selesai. Ditemukan **{total_grup} grup**.\nMemulai putaran promosi...")
            
            random.shuffle(groups) # Acak urutan grup agar natural
            success_count = 0

            for chat_id in groups:
                try:
                    await app.send_message(chat_id, PROMO_TEXT)
                    success_count += 1
                    
                    # 2. JEDA PER CHAT (Sangat Penting untuk 300+ Grup)
                    # Jeda acak antara 3 sampai 6 menit
                    await asyncio.sleep(random.randint(1, 8)) 

                except (errors.ChatWriteForbidden, errors.UserBannedInChannel):
                    # 3. FITUR AUTO LEAVE JIKA KENA BANNED/MUTE
                    await send_log(f"🚫 Keluar dari grup `{chat_id}` karena tidak diizinkan kirim pesan.")
                    await app.leave_chat(chat_id)
                
                except errors.FloodWait as e:
                    # Notif jika kena limit Telegram
                    await send_log(f"⚠️ **FloodWait!** Akun limit, istirahat paksa `{e.value}` detik.")
                    await asyncio.sleep(e.value)

                except Exception:
                    continue
            
            # 4. FITUR ISTIRAHAT 2 JAM
            await send_log(
                f"🏁 **Putaran Selesai!**\n"
                f"✅ Berhasil kirim ke: **{success_count} grup**\n"
                f"💤 Bot istirahat selama **10 menit**."
            )
            
            await asyncio.sleep(1000) # Jeda 2 jam
            await send_log("⏰ **Waktu istirahat habis!** Memulai scan grup untuk putaran baru...")

if __name__ == "__main__":
    app.run(auto_promo())
