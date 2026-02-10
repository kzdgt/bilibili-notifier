import random
import requests, qrcode, time, re, json, os, tempfile, filecmp, shutil, schedule
from pathlib import Path
import requests.utils as ru
from datetime import datetime

# 加载配置文件
def load_config():
    config_file = Path('./config.json')
    default_config = {
        "followed_dynamic_types": ["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"],
        "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx",
        "check_interval_minutes": 1
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ 配置文件加载成功")
            return config
        except Exception as e:
            print(f"⚠️ 配置文件读取失败，使用默认配置: {e}")
            return default_config
    else:
        print("⚠️ 配置文件不存在，创建默认配置文件")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print("✅ 默认配置文件已创建")
        except Exception as e:
            print(f"❌ 配置文件创建失败: {e}")
        return default_config

HEADERS = {
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*',
    'Host': 'passport.bilibili.com',
    'Connection': 'keep-alive'
}

# 加载配置
CONFIG = load_config()

# -----------运行地址-----------
OLD_BVID_FILE = Path('./bili/old_bvid.json')
COOKIE_FILE = Path('./bili/cookie.txt')
JSON_FILE = Path("./bili/jsonAll.json")
SAVE_FILE = Path('./www/wwwroot/qr.png')
#↑↑服务器公网链接展示图片

# -----------动态类型配置-----------
# 支持的动态类型: DYNAMIC_TYPE_AV(视频), DYNAMIC_TYPE_DRAW(文字/图文)
FOLLOWED_DYNAMIC_TYPES = CONFIG.get("followed_dynamic_types", ["DYNAMIC_TYPE_AV", "DYNAMIC_TYPE_DRAW"])

session = requests.Session()

def saveNprint_qr_image(text: str, path: str) -> None:
    # 确保目录存在
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = qrcode.make(text)
    img.save(path)
    print("二维码已保存到", path)
    qr = qrcode.QRCode(border=1)
    qr.add_data(text)
    qr.print_ascii(invert=True)

def send_feishu_card_error(error_str: str):
    elements = []
    # 添加错误信息
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": (
                f"**系统提示：** {error_str}  \n"
                f"**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
            )
        }
    })
    elements.append({
        "tag": "action",
        "actions": [{
            "tag": "button",
            "text": {"tag": "plain_text", "content": "👉 扫码登录"},
            "type": "primary",
            "url": ""  # 替换为实际的链接地址
        }]
    })
    elements.append({"tag": "hr"})

    # 飞书 Webhook 地址
    FEISHU_WEBHOOK = CONFIG.get("feishu_webhook")

    # 构造卡片消息
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "⚠️ 系统错误通知"},
                "template": "red"
            },
            "elements": elements
        }
    }

    # 发送请求
    resp = requests.post(FEISHU_WEBHOOK, json=card, timeout=10)
    print("飞书推送结果：", resp.json())


def send_feishu_card(dynamics: list[dict]):
    if not dynamics:
        return

    elements = []
    for dynamic in dynamics:
        # 纯文本段落 + 超链接按钮
        if dynamic['type'] == 'video':
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"**UP：**{dynamic['name']}  \n"
                        f"**时间：**{dynamic['pub_ts']}  \n"
                        f"**视频：**{dynamic['title']}"
                    )
                }
            })
            elements.append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "👉 打开视频"},
                    "type": "primary",
                    "url": f"https://www.bilibili.com/video/{dynamic['bvid']}"
                }]
            })
        elif dynamic['type'] == 'text':
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": (
                        f"**UP：**{dynamic['name']}  \n"
                        f"**时间：**{dynamic['pub_ts']}  \n"
                        f"**动态：**{dynamic['title']}"
                    )
                }
            })
            elements.append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "👉 查看完整动态"},
                    "type": "primary",
                    "url": f"https://t.bilibili.com/{dynamic['dynamic_id']}"
                }]
            })
        elements.append({"tag": "hr"})

    FEISHU_WEBHOOK = CONFIG.get("feishu_webhook")
    # 根据动态类型设置标题
    has_video = any(d['type'] == 'video' for d in dynamics)
    has_text = any(d['type'] == 'text' for d in dynamics)
    
    if has_video and has_text:
        title = "🎞 关注的 UP 更新啦！"
    elif has_video:
        title = "🎞 关注的 UP 更新视频啦！"
    elif has_text:
        title = "📝 关注的 UP 发动态啦！"
    else:
        title = "📢 关注的 UP 有更新啦！"

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue"
            },
            "elements": elements
        }
    }

    resp = requests.post(FEISHU_WEBHOOK, json=card, timeout=10)
    print("飞书推送结果：", resp.text)

class session_cookie:

    # cookie形式转换
    def dict_cookie_to_header(self, dict_cookie_str: str) -> str:
        # 1. 提取字典部分
        m = re.search(r'\{.*?\}', dict_cookie_str, flags=re.S)
        if not m:
            raise ValueError('未找到字典部分')
        cookie_dict = eval(m.group())
        # 2. 第一段里所有“公共字段”的模板（除了下面 5 个会动态替换）
        # 经过测试以上【xxxx】内容需要根据抓包去获得固定值（每个用户不同），
        # 每次提交的5个实际值才是有效字段，
        # 没有固定值却无法正常访问
        template = (
            "buvid3=xxxx; "
            "b_nut=xxxx; "
            "_uuid=xxxx; "
            "header_theme_version=OPEN; "
            "enable_web_push=DISABLE; "
            "home_feed_column=4; "
            "browser_resolution=xxx; "
            "buvid4=xxxxx; "
            "DedeUserID={DedeUserID}; "
            "DedeUserID__ckMd5={DedeUserID__ckMd5}; "
            "theme-tip-show=SHOWED; "
            "rpdid=xxxx; "
            "theme-avatar-tip-show=SHOWED; "
            "CURRENT_QUALITY=80; "
            "CURRENT_FNVAL=4048; "
            "bsource=search_baidu; "
            "fingerprint=xxxx; "
            "buvid_fp_plain=undefined; "
            "buvid_fp=xxxxx; "
            "bili_ticket=xxxxx; "
            "bili_ticket_expires=xxxx; "
            "SESSDATA={SESSDATA}; "
            "bili_jct={bili_jct}; "
            "sid={sid}; "
            "bp_t_offset_140462390=xxxxx; "
            "b_lsid=xxxxx"
        )    
        # 3. 把字典里的值填进去
        header_cookie = template.format(**cookie_dict)
        return f"Cookie: {header_cookie}"

    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers.update(HEADERS)
        self.load_cookies()

    def load_cookies(self):
        if COOKIE_FILE.exists() and COOKIE_FILE.stat().st_size > 0:
            try:
                with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
                    cookie_str = f.read().strip()
                    self.sess.headers['Cookie'] = self.dict_cookie_to_header(cookie_str)
                print("已加载本地 Cookie")
            except Exception as e:
                print("Cookie 文件损坏，已删除，准备重新登录", e)
                COOKIE_FILE.unlink(missing_ok=True)
        else:
            print("本地无 Cookie,准备登录")

    def cookie_valid(self) -> bool:
        try:
            if not COOKIE_FILE.exists():
                self._notify_and_save_qr("Cookie 文件不存在")
                return False

            url = "https://api.bilibili.com/x/space/myinfo"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://space.bilibili.com/',
                'Cookie': self.dict_cookie_to_header(COOKIE_FILE.read_text(encoding='utf-8').strip())
            }
            r = requests.get(url, headers=headers, timeout=10)
            data = r.json()
            if data.get("code") == 0 and data.get("data", {}).get("mid"):
                return True
        except Exception as e:
            print("Cookie 校验异常:", e)

        # 失效 → 提醒 + 保存二维码
        self._notify_and_save_qr("Cookie 已失效，需重新扫码登录")
        return False

    def _notify_and_save_qr(self, msg: str):
        time.sleep(1)
        # 飞书提醒
        send_feishu_card_error(msg)
        gen_url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
        resp = self.sess.get(gen_url).json()
        login_url = re.search(r'(https?://[^\s<]+)', resp['data']['url']).group(0)
        saveNprint_qr_image(login_url, SAVE_FILE)

    def save_cookies(self):
        # 确保目录存在
        os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(ru.dict_from_cookiejar(self.sess.cookies), f, ensure_ascii=False)
        print("Cookie 已保存到", COOKIE_FILE)

    def getQrCode(self):
        gen_url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
        resp = self.sess.get(gen_url).json()
        self.qrcode_key = resp['data']['qrcode_key']  # 保存 qrcode_key
        login_url = re.search(r'(https?://[^\s<]+)', resp['data']['url']).group(0)
        self._notify_and_save_qr(login_url)
        print(login_url)
        saveNprint_qr_image(login_url, SAVE_FILE)
        print(login_url)
        print('请使用哔哩哔哩 App 扫描二维码，qrcode_key =', self.qrcode_key)

    def ensure_login(self):
        if self.cookie_valid():
            print("✅ Cookie 有效，已登录")
            return True  # 返回 True 表示登录成功

        print("❌ Cookie 无效或未登录，开始扫码登录")
        self._notify_and_save_qr("Cookie 已失效，需重新扫码登录")
        return self._wait_for_qr_login()  # 等待扫码成功

    def _wait_for_qr_login(self) -> bool:
        self.getQrCode()  # 显示二维码
        poll_url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'
        while True:
            time.sleep(5)  # 每 5 秒轮询一次
            poll_resp = self.sess.get(poll_url, params={'qrcode_key': self.qrcode_key}).json()
            code = poll_resp['data']['code']
            if code == 0:  # 登录成功
                print("🎉 扫码成功，登录完成")
                self.save_cookies()  # 保存 Cookie
                return True
            elif code == 86101:  # 未扫描
                print("等待扫码中...")
            elif code == 86090:  # 已扫描未确认
                print("已扫描，等待确认...")
            elif code in (86038, 86039):  # 二维码过期 / 失效
                print("二维码已失效，请重新运行脚本")
                return False
            else:
                print("未知状态:", poll_resp)
                return False

    def compare_and_run(self, resp: dict) -> bool:
        """返回 True 表示有更新"""
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp:
            json.dump(resp, tmp, ensure_ascii=False, indent=2, sort_keys=True)
            tmp_path = tmp.name

        try:
            if JSON_FILE.exists() and filecmp.cmp(tmp_path, JSON_FILE, shallow=False):
                return False
            else:
                shutil.move(tmp_path, JSON_FILE)
                return True
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def get_followed_dynamic(self):
        Url_followed_dynamics = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all?type=all&page=1&features=itemOpusStyle'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.bilibili.com/',
            'Host': 'api.bilibili.com'
        }
        resp = self.sess.get(Url_followed_dynamics, headers=headers).json()
        print(json.dumps(resp, ensure_ascii=False, indent=2, sort_keys=True))
        has_update = self.compare_and_run(resp)
        if not JSON_FILE.exists():
            print("首次运行，本地无旧数据，视为更新。")
        # 确保目录存在并写json
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(resp, f, ensure_ascii=False)
        time.sleep(1)

        # 读json
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        items = data.get('data', {}).get('items', [])

        dynamics = []
        for item in items:
            dynamic_type = item.get('type')
            if dynamic_type not in FOLLOWED_DYNAMIC_TYPES:
                continue
                
            # 获取基础信息
            author_name = item['modules']['module_author']['name']
            pub_ts = datetime.fromtimestamp(item['modules']['module_author']['pub_ts']).strftime('%Y-%m-%d %H:%M:%S')
            
            if dynamic_type == 'DYNAMIC_TYPE_AV':
                # 视频动态处理
                archive = item.get('modules', {}).get('module_dynamic', {}).get('major', {}).get('archive', {})
                if not archive.get('bvid'):
                    continue
                dynamics.append({
                    'type': 'video',
                    'name': author_name,
                    'pub_ts': pub_ts,
                    'title': archive['title'],
                    'bvid': archive['bvid']
                })
            elif dynamic_type == 'DYNAMIC_TYPE_DRAW':
                # 文字/图文动态处理
                opus = item.get('modules', {}).get('module_dynamic', {}).get('major', {}).get('opus', {})
                summary = opus.get('summary', {})
                text_content = summary.get('text', '') if summary else ''
                
                if not text_content:
                    continue
                    
                dynamics.append({
                    'type': 'text',
                    'name': author_name,
                    'pub_ts': pub_ts,
                    'title': text_content[:100] + ('...' if len(text_content) > 100 else ''),  # 截取前100字符
                    'content': text_content,
                    'dynamic_id': item.get('id_str', '')
                })

        # 读取旧的动态ID列表，文件不存在或空/损坏都返回空集合
        try:
            with OLD_BVID_FILE.open(encoding='utf-8') as f:
                content = f.read().strip()
                old_data = json.loads(content) if content else []
                
                # 数据迁移：检查是否是旧的bvid格式（只有bvid字符串）
                if old_data and isinstance(old_data[0], str) and not old_data[0].startswith(('video_', 'text_')):
                    # 旧格式迁移：将["BV1xxx", "BV2xxx"]转换为["video_BV1xxx", "video_BV2xxx"]
                    old_dynamic_ids = set(f"video_{bvid}" for bvid in old_data)
                    print(f"🔄 检测到旧的bvid格式，已迁移 {len(old_dynamic_ids)} 个视频动态ID")
                else:
                    # 新格式直接使用
                    old_dynamic_ids = set(old_data)
                    
        except (FileNotFoundError, json.JSONDecodeError):
            old_dynamic_ids = set()
            
        # 根据动态类型生成唯一ID
        new_dynamics = []
        for dynamic in dynamics:
            if dynamic['type'] == 'video':
                dynamic_id = f"video_{dynamic['bvid']}"
            elif dynamic['type'] == 'text':
                dynamic_id = f"text_{dynamic['dynamic_id']}"
            else:
                continue
                
            if dynamic_id not in old_dynamic_ids:
                new_dynamics.append(dynamic)
            else:
                # 调试信息：显示被过滤的重复动态
                print(f"🔄 过滤重复动态：{dynamic['name']} - {dynamic['title'][:30]}...")

        # 显示处理统计
        total_video = sum(1 for d in dynamics if d['type'] == 'video')
        total_text = sum(1 for d in dynamics if d['type'] == 'text')
        new_video = sum(1 for d in new_dynamics if d['type'] == 'video')
        new_text = sum(1 for d in new_dynamics if d['type'] == 'text')
        
        print(f"📊 处理统计：总{total_video}个视频，{total_text}个文字动态 | 新{new_video}个视频，{new_text}个文字动态 | 已过滤{total_video + total_text - new_video - new_text}个重复动态")
        
        if new_dynamics:
            send_feishu_card(new_dynamics)
            # 确保目录存在并保存本轮全部动态ID供下次差分
            os.makedirs(os.path.dirname(OLD_BVID_FILE), exist_ok=True)
            all_dynamic_ids = []
            for dynamic in dynamics:
                if dynamic['type'] == 'video':
                    all_dynamic_ids.append(f"video_{dynamic['bvid']}")
                elif dynamic['type'] == 'text':
                    all_dynamic_ids.append(f"text_{dynamic['dynamic_id']}")
            
            # 调试信息：显示要保存的动态ID
            print(f"💾 保存动态ID列表：{all_dynamic_ids[:5]}{'...' if len(all_dynamic_ids) > 5 else ''} (共{len(all_dynamic_ids)}个)")
            
            with open(OLD_BVID_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_dynamic_ids, f, ensure_ascii=False)
            print(f"✅ 动态ID列表已保存到 {OLD_BVID_FILE}")
        else:
            print("本次无新增动态，不推送")

def job():
    bililogin = session_cookie()
    if bililogin.ensure_login():  # 等待登录成功
        print(f"[{datetime.now():%H:%M:%S}] 开始抓取...")
        bililogin.get_followed_dynamic()
    else:
        print("登录失败，无法继续抓取")

# 使用配置文件中的检查间隔
interval_minutes = CONFIG.get("check_interval_minutes", 1)
print(f"⏰ 设置检查间隔为 {interval_minutes} 分钟")
schedule.every(interval_minutes).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)