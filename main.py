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

status_msg_id = None 

app = Client(
    "farin_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    sleep_threshold=60 
)

async def update_dashboard(stats_content):
    """Update tampilan log dashboard agar tetap rapi dan profesional"""
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
            msg = await app.send_message(LOG_CHANNEL, full_text)
            status_msg_id = msg.id
        except: pass

async def auto_promo():
    if not app.is_connected:
        await app.start()
        
    await update_dashboard("🚀 **Status:** Userbot Online\n📡 **System:** Mendeteksi 600+ grup...")
    
    while True:
        await update_dashboard("🔍 **Status:** Memindai & Membersihkan Grup...")
        
        groups = []
        # Deteksi awal grup yang bermasalah saat scan dialog
        try:
            async for dialog in app.get_dialogs():
                try:
                    # Filter hanya grup dan supergroup
                    if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                        groups.append(dialog.chat.id)
                except (errors.ChannelPrivate, errors.ChatAdminRequired):
                    # Jika grup sudah di-ban atau private saat discan, langsung keluar
                    try:
                        await app.leave_chat(dialog.chat.id)
                    except: pass
                except Exception:
                    continue
        except Exception as e:
            await update_dashboard(f"⚠️ **Scan Terhambat:** {e}\nTetap lanjut dengan grup yang terbaca.")

        total_grup = len(groups)
        if total_grup == 0:
            await update_dashboard("⚠️ **Status:** Tidak ada grup aktif ditemukan.")
            await asyncio.sleep(300)
            continue

        random.shuffle(groups)
        success, failed, left = 0, 0, 0

        for index, chat_id in enumerate(groups):
            try:
                await app.send_message(chat_id, PROMO_TEXT)
                success += 1
            
            # LOGIKA DETEKSI GRUP BLOKIR / BAN / PRIVATE
            except (errors.ChatWriteForbidden, 
                    errors.UserBannedInChannel, 
                    errors.ChatAdminRequired, 
                    errors.ChannelPrivate,
                    errors.ChatInvalid,
                    errors.PeerIdInvalid):
                # Ini adalah grup yang sudah memblokir kamu atau di-ban Telegram
                try:
                    await app.leave_chat(chat_id)
                    left += 1
                except: pass
                
            except errors.FloodWait as e:
                # Jika kena limit massal, lapor dan istirahat
                await update_dashboard(f"⚠️ **FloodWait!** Limit `{e.value}` detik.\nMenunggu giliran aman...")
                await asyncio.sleep(e.value)
                # Coba sekali lagi setelah tunggu
                try:
                    await app.send_message(chat_id, PROMO_TEXT)
                    success += 1
                except: failed += 1
                
            except Exception:
                failed += 1

            # Update log setiap 10 grup agar tidak overload
            if (index + 1) % 5 == 0 or (index + 1) == total_grup:
                pct = ((index + 1) / total_grup) * 100
                stats = (
                    f"📤 **Status:** Promosi Massal Aktif\n\n"
                    f"📊 **Progres:** {index + 1}/{total_grup} ({pct:.1f}%)\n"
                    f"✅ **Terkirim:** {success}\n"
                    f"❌ **Gagal:** {failed}\n"
                    f"🚪 **Grup Diblokir/Ban:** {left}\n"
                    f"ℹ️ *Grup terblokir otomatis ditinggalkan.*"
                )
                await update_dashboard(stats)

            # JEDA AMAN (Sangat Penting untuk 600+ grup)
            await asyncio.sleep(random.randint(1, 5))

        # Selesai Putaran
        await update_dashboard(
            f"🏁 **Status:** Putaran Selesai!\n\n"
            f"✅ **Total Berhasil:** {success}\n"
            f"❌ **Total Gagal:** {failed}\n"
            f"🚪 **Total Grup Dihapus:** {left}\n\n"
            f"💤 **Mode:** Istirahat (2 Jam)\n"
            f"📅 *Putaran berikutnya akan otomatis dimulai.*"
        )
        # Istirahat 2 jam agar akun tidak dianggap spammer agresif
        await asyncio.sleep(1800)

if __name__ == "__main__":
    app.run(auto_promo())