import asyncio
import random
import os
from datetime import datetime
import pytz
from pyrogram import Client, enums, errors

# --- CONFIGURATION (AMBIL DARI VARIABLES RAILWAY) ---
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
LOG_CHANNEL = "@farinmodssv2"

# Setting Zona Waktu Indonesia (WIB)
WIB = pytz.timezone('Asia/Jakarta')

# --- KONTEN PROMOSI FARIN SHOP ---
PROMO_TEXT = (
"📱 **NOKOS MURAH & INSTAN** 📱\n\n"
"• Harga mulai Rp900\n"
"• Banyak pilihan aplikasi\n"
"• Auto refund saldo jika OTP tidak masuk\n"
"• Deposit QRIS otomatis\n"
"• Proses cepat & stabil\n\n"
"🕘 Admin online 24/7\n"
"⚡ Fast respon\n\n"
"🤖 Bot order: @farinshop_bot\n"
"🚀 **Langsung gas order sekarang!**"
)

# Variabel global untuk menyimpan ID pesan agar bisa di-edit
status_msg_id = None 

app = Client(
    "farin_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

async def update_dashboard(stats_content):
    """Fungsi untuk mengupdate satu pesan log (Dashboard Mode)"""
    global status_msg_id
    now = datetime.now(WIB).strftime("%d/%m/%Y %H:%M:%S")
    
    header = f"🛡️ **FARIN SHOP MONITORING**\n{'─'*25}\n"
    footer = f"\n{'─'*25}\n🕒 *Last Update: {now} WIB*"
    full_text = header + stats_content + footer
    
    try:
        if status_msg_id:
            await app.edit_message_text(LOG_CHANNEL, status_msg_id, full_text)
        else:
            msg = await app.send_message(LOG_CHANNEL, full_text)
            status_msg_id = msg.id
    except Exception:
        # Jika pesan lama dihapus atau terjadi error, kirim pesan baru
        try:
            msg = await app.send_message(LOG_CHANNEL, full_text)
            status_msg_id = msg.id
        except Exception as e:
            print(f"Gagal update log: {e}")

async def auto_promo():
    # Pastikan client aktif
    if not app.is_connected:
        await app.start()
        
    await update_dashboard("🚀 **Status:** Userbot Online\n📡 **System:** Menyiapkan putaran promosi...")
    
    while True:
        await update_dashboard("🔍 **Status:** Sedang memindai daftar grup...")
        
        groups = []
        try:
            # Ambil semua dialog grup & supergroup
            async for dialog in app.get_dialogs():
                if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    groups.append(dialog.chat.id)
        except Exception as e:
            await update_dashboard(f"❌ **Error Scan:** {e}\n🔄 Mencoba lagi dalam 1 menit...")
            await asyncio.sleep(60)
            continue

        total_grup = len(groups)
        if total_grup == 0:
            await update_dashboard("⚠️ **Status:** Tidak ada grup ditemukan!\nPastikan akun sudah join grup.")
            await asyncio.sleep(300)
            continue

        # Acak urutan grup agar terlihat natural bagi sistem Telegram
        random.shuffle(groups)
        
        success_count = 0
        failed_count = 0
        left_count = 0

        for index, chat_id in enumerate(groups):
            try:
                # Kirim promosi
                await app.send_message(chat_id, PROMO_TEXT)
                success_count += 1
                
            except (errors.ChatWriteForbidden, errors.UserBannedInChannel, errors.ChatAdminRequired):
                # Auto-leave jika diblokir/tidak boleh kirim pesan
                try:
                    await app.leave_chat(chat_id)
                    left_count += 1
                except:
                    pass
                    
            except errors.FloodWait as e:
                # Jika terkena limit (FloodWait), istirahat sesuai durasi dari Telegram
                await update_dashboard(f"⚠️ **FloodWait!** Limit terdeteksi.\n⏳ Istirahat paksa `{e.value}` detik.")
                await asyncio.sleep(e.value)
                # Coba kirim ulang setelah masa tunggu
                try:
                    await app.send_message(chat_id, PROMO_TEXT)
                    success_count += 1
                except:
                    failed_count += 1
                    
            except Exception:
                failed_count += 1

            # Edit dashboard setiap 5 grup agar aman dari limit edit pesan
            if index % 5 == 0 or index + 1 == total_grup:
                progress_pct = ((index + 1) / total_grup) * 100
                stats = (
                    f"📤 **Status:** Promosi Berjalan\n\n"
                    f"📊 **Progres:** {index + 1}/{total_grup} ({progress_pct:.1f}%)\n"
                    f"✅ **Berhasil:** {success_count}\n"
                    f"❌ **Gagal:** {failed_count}\n"
                    f"🚪 **Auto-Leave:** {left_count}"
                )
                await update_dashboard(stats)

            # Jeda antar pesan (Sangat Penting! 30-60 detik agar akun aman)
            await asyncio.sleep(random.randint(1, 6))

        # Ringkasan Akhir Putaran
        await update_dashboard(
            f"🏁 **Status:** Putaran Selesai!\n\n"
            f"✅ **Total Terkirim:** {success_count}\n"
            f"❌ **Total Gagal:** {failed_count}\n"
            f"🚪 **Total Keluar:** {left_count}\n\n"
            f"💤 **Mode:** Istirahat (1 Jam)"
        )
        
        # Jeda antar putaran (1 Jam / 3600 detik)
        await asyncio.sleep(900)

if __name__ == "__main__":
    app.run(auto_promo())