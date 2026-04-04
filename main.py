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

# Global variable untuk ID pesan Dashboard
status_msg_id = None

app = Client(
    "farin_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    sleep_threshold=120  # Otomatis handle FloodWait yang lama
)

async def update_dashboard(stats_content):
    """Mengedit satu pesan log agar channel tetap bersih (Dashboard Mode)"""
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
        try:
            # Jika pesan lama dihapus, kirim pesan baru
            msg = await app.send_message(LOG_CHANNEL, full_text)
            status_msg_id = msg.id
        except:
            pass

async def auto_promo():
    # Menangani Error 409 (Conflict) saat startup
    try:
        if not app.is_connected:
            await app.start()
    except errors.AuthKeyDuplicated:
        print("Error 409: Session bentrok! Menunggu restart...")
        await asyncio.sleep(15)
        return

    await update_dashboard("🚀 **Status:** Userbot Online\n📡 **System:** Overpower Mode Aktif (600+ Grup)")
    
    while True:
        await update_dashboard("🔍 **Status:** Memindai & Membersihkan Grup Sampah...")
        
        groups = []
        try:
            # Bypass error 406 saat scan dialog
            async for dialog in app.get_dialogs():
                try:
                    if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                        groups.append(dialog.chat.id)
                except (errors.ChannelPrivate, errors.ChatAdminRequired, errors.UserBannedInChannel):
                    # AUTO LEAVE jika grup sudah tidak bisa diakses
                    try:
                        await app.leave_chat(dialog.chat.id)
                    except: pass
                except Exception:
                    continue
        except Exception as e:
            await update_dashboard(f"⚠️ **Scan Terhambat:** {e}\nLanjut dengan grup yang terbaca.")

        total_grup = len(groups)
        if total_grup == 0:
            await update_dashboard("⚠️ **Status:** Tidak ada grup ditemukan!")
            await asyncio.sleep(300)
            continue

        # Acak urutan kirim agar terlihat natural
        random.shuffle(groups)
        
        success, failed, left = 0, 0, 0

        for index, chat_id in enumerate(groups):
            try:
                await app.send_message(chat_id, PROMO_TEXT)
                success += 1
                
            # --- LOGIKA AUTO-LEAVE (GRUP MATI/BAN/PRIVATE) ---
            except (errors.ChatWriteForbidden, 
                    errors.UserBannedInChannel, 
                    errors.ChatAdminRequired, 
                    errors.ChannelPrivate,
                    errors.ChatInvalid,
                    errors.PeerIdInvalid):
                try:
                    await app.leave_chat(chat_id)
                    left += 1
                except: pass
                
            except errors.FloodWait as e:
                # Jika kena limit massal dari Telegram
                await update_dashboard(f"⚠️ **FloodWait!** Limit `{e.value}` detik.")
                await asyncio.sleep(e.value)
                try:
                    await app.send_message(chat_id, PROMO_TEXT)
                    success += 1
                except: failed += 1
                
            except Exception:
                failed += 1

            # Update Dashboard setiap 10 grup agar hemat request API
            if (index + 1) % 10 == 0 or (index + 1) == total_grup:
                pct = ((index + 1) / total_grup) * 100
                stats = (
                    f"📤 **Status:** Promosi Massal Aktif\n\n"
                    f"📊 **Progres:** {index + 1}/{total_grup} ({pct:.1f}%)\n"
                    f"✅ **Terkirim:** {success}\n"
                    f"❌ **Gagal:** {failed}\n"
                    f"🚪 **Auto-Leave (Mati/Ban):** {left}\n\n"
                    f"ℹ️ *Grup bermasalah otomatis ditinggalkan.*"
                )
                await update_dashboard(stats)

            # JEDA AMAN (Sangat penting agar akun tidak di-ban)
            # Menggunakan jeda 35-65 detik per pesan
            await asyncio.sleep(random.randint(1, 6))

        # Ringkasan Akhir Putaran
        await update_dashboard(
            f"🏁 **Status:** Putaran Selesai!\n\n"
            f"✅ **Total Berhasil:** {success}\n"
            f"❌ **Total Gagal:** {failed}\n"
            f"🚪 **Total Grup Dihapus:** {left}\n\n"
            f"💤 **Mode:** Istirahat (2 Jam)"
        )
        
        # Jeda 2 jam antar putaran massal
        await asyncio.sleep(1200)

if __name__ == "__main__":
    # Loop utama untuk menangani restart otomatis jika terjadi Conflict (409)
    while True:
        try:
            app.run(auto_promo())
        except errors.AuthKeyDuplicated:
            print("Koneksi bentrok (409). Mematikan proses lama...")
            asyncio.run(asyncio.sleep(15))
        except Exception as e:
            print(f"Sistem Restart: {e}")
            asyncio.run(asyncio.sleep(10))