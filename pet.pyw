# WhalePet 桌宠 启动器（Qt WebEngine：透明无边框置顶窗口）
import ctypes
import json
import math
import os
import random
import sys
import threading
from ctypes import wintypes

# 必须在导入 Qt 之前设置：否则 Chromium 沙箱起不来，页面加载会失败
os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--no-sandbox --disable-dev-shm-usage --disable-features=ElasticOverscroll",
)

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "whale.html")
POS_FILE = os.path.join(HERE, ".pet_pos.json")
CFG_FILE = os.path.join(HERE, ".pet_cfg.json")

W, H = 260, 400          # 基准尺寸（scale=1.0）
MIN_SCALE, MAX_SCALE = 0.55, 1.45
FOCUS_MINUTES = 30
POLL_MS = 50

IS_WIN = (sys.platform == "win32")

STARTUP_DIR = os.path.join(
    os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
STARTUP_FILE = os.path.join(STARTUP_DIR, "WhalePet.bat")
# 历史遗留的自启文件名（旧版曾用中文名）。留着只为升级时能清理掉旧条目，不再新建
STARTUP_FILE_LEGACY = os.path.join(STARTUP_DIR, "WhalePet-legacy.bat")
PYTHONW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(PYTHONW):
    PYTHONW = sys.executable

BASE_FLAGS = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool


def load_pos():
    try:
        with open(POS_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            return int(d["x"]), int(d["y"])
    except Exception:
        return None


def save_pos(x, y):
    try:
        with open(POS_FILE, "w", encoding="utf-8") as f:
            json.dump({"x": int(x), "y": int(y)}, f)
    except Exception:
        pass


class PetPage(QWebEnginePage):
    """宿主侧：轮询取走页面命令队列，控制真实窗口。"""

    def __init__(self, view, app, parent=None):
        super().__init__(parent)
        self.view = view
        self.app = app
        self.busy = False
        self.focus_on = False
        self.focus_timer = None

        self.voice_on = False
        self.tts_voice = None
        self._tts_ready = False
        self._tts_busy = False
        self.cfg = {"sound": True, "wander": True, "voice": True,
                    "skin": "whale", "scale": 0.78, "voice_style": ""}
        self._load_cfg()
        self._init_tts()

        self.drag_offset = None
        self.drag_timer = QTimer(self)
        self.drag_timer.setInterval(16)
        self.drag_timer.timeout.connect(self._follow_cursor)

        self.wander_timer = QTimer(self)
        self.wander_timer.setInterval(30)
        self.wander_timer.timeout.connect(self._wander_step)
        self.wander_plan = None

        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(POLL_MS)
        self.poll_timer.timeout.connect(self._poll)
        self.poll_timer.start()

    # ---------- 命令通道 ----------
    def _poll(self):
        if self.busy:
            return
        self.busy = True
        # 逗号表达式：顺手告诉页面宿主在线，再取走队列
        self.runJavaScript(
            "(window.__hostReady=true,(window.__drain?window.__drain():'[]'))",
            self._on_drain)

    def _on_drain(self, text):
        self.busy = False
        if not text:
            return
        try:
            items = json.loads(text)
        except Exception:
            return
        for it in items:
            if isinstance(it, dict):
                self.dispatch(it.get("c", ""), it.get("a", ""), it.get("i"))

    def dispatch(self, cmd, arg, rid):
        if cmd == "wander":
            self.start_wander()
        elif cmd == "drag_start":
            c = QCursor.pos()
            self.drag_offset = (c.x() - self.view.x(), c.y() - self.view.y())
            self.drag_timer.start()
        elif cmd == "drag_end":
            self.drag_timer.stop()
            self.drag_offset = None
            save_pos(self.view.x(), self.view.y())
        elif cmd == "to_corner":
            g = self.screen_geom()
            w, h = self.cur_wh()
            x = g.x() + g.width() - w - 20
            y = g.y() + g.height() - h - 60
            self.view.move(x, y)
            save_pos(x, y)
        elif cmd == "focus_mode":
            self.reply(rid, self.set_focus(True))
        elif cmd == "toggle_autostart":
            self.reply(rid, self.toggle_autostart())
        elif cmd == "autostart_state":
            self.reply(rid, IS_WIN and
                       (os.path.exists(STARTUP_FILE) or os.path.exists(STARTUP_FILE_LEGACY)))
        elif cmd == "speak":
            self.speak(arg)
        elif cmd == "get_cfg":
            self.reply(rid, self._cfg_dict())
        elif cmd == "set_cfg":
            self._apply_cfg(arg)
        elif cmd == "quit":
            QTimer.singleShot(0, self.app.quit)

    def reply(self, rid, value):
        if rid is None:
            return
        self.runJavaScript("window.__apiResult(%d, %s)" % (int(rid), json.dumps(value)))

    def js(self, code):
        self.runJavaScript(code)

    # ---------- 屏幕 / 窗口 ----------
    def screen_geom(self):
        scr = self.view.screen() or self.app.primaryScreen()
        return scr.availableGeometry()

    def _follow_cursor(self):
        if self.drag_offset is None:
            return
        # 安全网：若鼠标左键已松开（如松手在窗口外、mouseup 没收到），立即停跟，
        # 避免桌宠永远黏在鼠标上
        if not (QApplication.mouseButtons() & Qt.LeftButton):
            self.dispatch("drag_end", "", None)
            return
        c = QCursor.pos()
        self.view.move(c.x() - self.drag_offset[0], c.y() - self.drag_offset[1])

    # ---------- 自动游荡 ----------
    def start_wander(self):
        g = self.screen_geom()
        w, h = self.cur_wh()
        step = random.uniform(90, 240)
        ang = random.uniform(0, math.tau)
        tx = self.view.x() + math.cos(ang) * step
        ty = self.view.y() + math.sin(ang) * step * 0.55
        tx = max(g.x(), min(tx, g.x() + g.width() - w))
        ty = max(g.y(), min(ty, g.y() + g.height() - h))
        if abs(tx - self.view.x()) > 8:
            self.js("window.__face(%d)" % (-1 if tx < self.view.x() else 1))
        n = max(1, random.randint(1800, 3400) // 30)
        self.wander_plan = [self.view.x(), self.view.y(), tx, ty, 0, n]
        self.wander_timer.start()

    def _wander_step(self):
        p = self.wander_plan
        if not p:
            self.wander_timer.stop()
            return
        x0, y0, tx, ty, i, n = p
        i += 1
        if i >= n:
            self.view.move(int(tx), int(ty))
            self.wander_plan = None
            self.wander_timer.stop()
            return
        p[4] = i
        self.view.move(int(x0 + (tx - x0) * i / n), int(y0 + (ty - y0) * i / n))

    # ---------- 专注模式：鼠标穿透（Ctrl+Alt+W 全局快捷键可随时开关）----------
    def set_focus(self, on):
        x, y = self.view.x(), self.view.y()
        if on:
            self.focus_on = True
            self.view.setWindowFlags(BASE_FLAGS | Qt.WindowTransparentForInput)
            self.view.show()
            self.view.move(x, y)
            if self.focus_timer is None:
                self.focus_timer = QTimer(self)
                self.focus_timer.setSingleShot(True)
                self.focus_timer.timeout.connect(self._end_focus)
            self.focus_timer.start(FOCUS_MINUTES * 60 * 1000)
            self.js("if(window.__setFocus)window.__setFocus(true);")
            return True
        # 退出专注模式
        self.focus_on = False
        if self.focus_timer is not None:
            self.focus_timer.stop()
        self.view.setWindowFlags(BASE_FLAGS)
        self.view.show()
        self.view.move(x, y)
        self.js("(function(){if(window.__setFocus)window.__setFocus(false);"
                "var b=document.getElementById('bubble');"
                "if(b){b.textContent='专注模式结束，我回来啦～';b.classList.add('show');"
                "setTimeout(function(){b.classList.remove('show')},3200);}})()")
        return False

    def _end_focus(self):
        self.set_focus(False)

    def toggle_focus(self):
        self.set_focus(not self.focus_on)

    # ---------- 设置持久化（静音/游荡/语音）----------
    def _load_cfg(self):
        try:
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            for k in self.cfg:
                if k in d:
                    if k in ("sound", "wander", "voice"):
                        self.cfg[k] = bool(d[k])
                    elif k == "scale":
                        try:
                            v = float(d[k])
                            self.cfg[k] = max(MIN_SCALE, min(MAX_SCALE, v))
                        except (TypeError, ValueError):
                            pass
                    else:
                        self.cfg[k] = d[k]
        except Exception:
            pass
        self.voice_on = self.cfg["voice"]
        self.skin = self.cfg.get("skin") or "whale"
        vs = self.cfg.get("voice_style") or ""
        self.voice_style = vs if vs in self.VOICE_PRESETS else ""

    def _save_cfg(self):
        try:
            with open(CFG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cfg, f)
        except Exception:
            pass

    def _cfg_dict(self):
        return dict(self.cfg)

    def _apply_cfg(self, arg):
        try:
            d = json.loads(arg)
            for k in self.cfg:
                if k in d:
                    if k in ("sound", "wander", "voice"):
                        self.cfg[k] = bool(d[k])
                    elif k == "scale":
                        try:
                            v = float(d[k])
                            self.cfg[k] = max(MIN_SCALE, min(MAX_SCALE, v))
                        except (TypeError, ValueError):
                            pass
                    else:
                        self.cfg[k] = d[k]
            self.voice_on = self.cfg["voice"]
            # 音色配方：用户手动挑过 voice_style 就用它，否则跟随角色
            vs = self.cfg.get("voice_style") or ""
            if vs not in self.VOICE_PRESETS:
                vs = self.skin if self.skin in self.VOICE_PRESETS else ""
            self.voice_style = vs
            self._apply_voice_preset()
            self._save_cfg()
            if "scale" in d:
                self.resize_pet(self.cfg["scale"])
        except Exception:
            pass

    # ---------- 尺寸缩放（窗口与页面一起缩放，位置按比例保持）----------
    def cur_wh(self):
        s = float(self.cfg.get("scale", 1.0))
        return max(120, int(W * s)), max(180, int(H * s))

    def resize_pet(self, scale):
        try:
            s = max(MIN_SCALE, min(MAX_SCALE, float(scale)))
        except (TypeError, ValueError):
            return
        self.cfg["scale"] = s
        w, h = self.cur_wh()
        x, y = self.view.x(), self.view.y()
        self.view.resize(w, h)
        # 贴着屏幕右下角时，缩放后仍然贴着右下角，避免缩小时悬空
        g = self.screen_geom()
        if x + w > g.x() + g.width():
            x = g.x() + g.width() - w
        if y + h > g.y() + g.height():
            y = g.y() + g.height() - h
        self.view.move(max(g.x(), x), max(g.y(), y))
        save_pos(self.view.x(), self.view.y())
        self._save_cfg()
        # 通知页面重算菜单定位（页面用 transform 缩放，尺寸已变）
        self.js("if(window.__onResize)window.__onResize();")

    # ---------- 语音（优先 Edge TTS 在线神经语音，质量远好于本地 SAPI；离线退回 SAPI）----------
    # 每个角色一套音色配方：不同基础嗓音 + 语速 + 音调，听感差异明显但**全部是女声**。
    # pitch 实测生效（同文案不同 pitch 出音频 md5 不同），是拉开音色差异的关键旋钮。
    #
    # ⚠️ 可迁移性约定（换机器 / 换网络都能用）：
    #   1. 只有 edge_tts 一个在线依赖，且它是纯 WebSocket 调用，**不需要 API key、不需要登录**；
    #      官方在中国大陆也提供服务，正常联网即可用。
    #   2. 这里只列**官方长期存在的 zh-CN 女声**，绝不写死某个可能下架的小众音色。
    #   3. 万一某个音色在别的机器上不可用，会自动按 voices 列表往下试，
    #      再不行才退 SAPI —— 见 _speak_edge 的逐音色回退。
    VOICE_PRESETS = {
        # ── 按角色性格配声 ─────────────────────────────────────────────
        # 鲸鱼娘：干饭萌系小鲸鱼。音调抬高 + 慢语速，念起来糯糯的
        "whale":  {"voices": ["zh-CN-XiaoyiNeural", "zh-CN-XiaoxiaoNeural"],
                   "rate": "-2%",  "pitch": "+38Hz", "volume": "+0%"},
        # 白龙娘：冷淡不悦、倨傲。音调压低、语速略慢、音量轻 —— 一股「懒得理你」的敷衍感
        "gpt":    {"voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-XiaoyiNeural"],
                   "rate": "-6%",  "pitch": "-18Hz", "volume": "-8%"},
        # 书卷娘：半垂眼厌世学姐，沉静疏离。语速平缓、音调偏低，不带起伏
        "claude": {"voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-XiaoyiNeural"],
                   "rate": "-2%",  "pitch": "-6Hz",  "volume": "-4%"},
        # 猫耳娘：温柔带点调皮的猫耳娘。语速稍快、音调上扬，活泼里透着狡黠
        "glm":    {"voices": ["zh-CN-XiaoyiNeural", "zh-CN-XiaoxiaoNeural"],
                   "rate": "+4%",  "pitch": "+12Hz", "volume": "+0%"},
    }
    DEFAULT_VOICE = {"voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-XiaoyiNeural"],
                     "rate": "+5%", "pitch": "+25Hz", "volume": "+0%"}

    def _init_tts(self):
        self.tts_engine = None
        self.tts_voice = None   # SAPI 嗓音 id（兜底用）
        self.skin = "whale"
        self.edge_voices = ["zh-CN-XiaoxiaoNeural"]
        self.edge_rate = "+5%"
        self.edge_pitch = "+25Hz"
        try:
            import edge_tts  # noqa: F401
            self.tts_engine = "edge"
        except Exception:
            self.tts_engine = None
        try:
            import pyttsx3
            e = pyttsx3.init()
            vs = e.getProperty("voices") or []
            zh = [v for v in vs if any((la or "").lower().startswith("zh")
                                       for la in (v.languages or []))]
            if zh:
                self.tts_voice = zh[0].id
            if self.tts_engine is None:
                self.tts_engine = "sapi"
        except Exception:
            pass
        self._tts_ready = bool(self.tts_engine)
        self._apply_voice_preset()

    def _apply_voice_preset(self):
        """按「音色配方」切换嗓音（全部女声）。

        配方来源优先级：用户手动选的 voice_style > 当前角色 > 默认。
        """
        key = getattr(self, "voice_style", "") or self.skin
        if key not in self.VOICE_PRESETS:
            key = self.skin if self.skin in self.VOICE_PRESETS else ""
        p = self.VOICE_PRESETS.get(key, self.DEFAULT_VOICE)
        self.edge_voices = list(p.get("voices") or self.DEFAULT_VOICE["voices"])
        self.edge_rate = p.get("rate", "+5%")
        self.edge_pitch = p.get("pitch", "+25Hz")
        self.edge_volume = p.get("volume", "+0%")
        # SAPI 兜底也按配方调语速：pitch 无效，只能靠语速体现差异
        self.sapi_rate = {"whale": 178, "gpt": 160, "claude": 168, "glm": 196}.get(key, 188)

    def speak(self, text):
        if not self.voice_on or not self.tts_engine:
            return
        # 防止并发重叠：正在念就跳过新的，避免多句叠在一起听不清
        if self._tts_busy:
            return
        self._tts_busy = True
        threading.Thread(target=self._speak_worker,
                         args=(str(text)[:60], self._tts_done),
                         daemon=True).start()

    def _tts_done(self):
        self._tts_busy = False

    def _speak_worker(self, text, done):
        try:
            if self.tts_engine == "edge":
                self._speak_edge(text)
            else:
                self._speak_sapi(text)
        except Exception:
            # edge 失败（如无网络）时退回 SAPI
            try:
                self._speak_sapi(text)
            except Exception:
                pass
        finally:
            if done:
                done()

    def _speak_sapi(self, text):
        import pyttsx3
        e = pyttsx3.init()
        if self.tts_voice:
            e.setProperty("voice", self.tts_voice)
        # SAPI 不支持 pitch/volume 参数，只能靠语速体现角色差异
        e.setProperty("rate", getattr(self, "sapi_rate", 188))
        e.say(text)
        e.runAndWait()

    def _speak_edge(self, text):
        """在线神经语音。逐音色回退，任一音色成功即返回。

        换机器 / 换网络时某个音色可能不可用（下架、区域限制），
        所以不能只试一个就放弃 —— 依次试完 voices 列表，全挂才抛异常退 SAPI。
        """
        import asyncio
        import tempfile
        voices = list(self.edge_voices) or ["zh-CN-XiaoxiaoNeural"]
        # 打乱顺序让同一角色的多音色轮流上场，听着不单调
        random.shuffle(voices)
        last_err = None
        for voice in voices:
            fd, mp3 = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            try:
                asyncio.run(self._edge_save(text, voice, mp3))
                if os.path.getsize(mp3) > 0:
                    self._play_mp3(mp3)
                    return
                last_err = RuntimeError("空音频: %s" % voice)
            except Exception as e:
                last_err = e
            finally:
                try:
                    os.remove(mp3)
                except Exception:
                    pass
        if last_err:
            raise last_err

    async def _edge_save(self, text, voice, path):
        import edge_tts
        comm = edge_tts.Communicate(text, voice,
                                    rate=self.edge_rate,
                                    pitch=self.edge_pitch,
                                    volume=getattr(self, "edge_volume", "+0%"))
        await comm.save(path)

    def _play_mp3(self, path):
        """播放 mp3。Windows 用自带 winmm（零依赖）；其他平台找常见播放器，都没有就静默跳过。"""
        if IS_WIN:
            w32 = ctypes.windll.winmm
            buf = ctypes.create_unicode_buffer(256)

            def cmd(s):
                return w32.mciSendStringW(s, buf, 256, None)

            if cmd('open "%s" type mpegvideo alias petvoice' % path) != 0:
                return
            try:
                if cmd("play petvoice wait") != 0:
                    cmd("play petvoice")
            finally:
                cmd("close petvoice")
            return
        # macOS / Linux：退而求其次，调系统播放器（有就用，没有就算了，不影响主流程）
        import shutil
        import subprocess
        for player, args in (("afplay", []), ("mpg123", ["-q"]), ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet"])):
            exe = shutil.which(player)
            if not exe:
                continue
            try:
                subprocess.run([exe] + args + [path], timeout=30,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except Exception:
                continue

    # ---------- 开机自启（仅 Windows 有"启动文件夹"这一说，其他平台直接不支持）----------
    def toggle_autostart(self):
        if not IS_WIN:
            return False
        was_on = os.path.exists(STARTUP_FILE) or os.path.exists(STARTUP_FILE_LEGACY)
        # 清理英文名与可能残留的旧中文名，避免重复自启项
        for f in (STARTUP_FILE, STARTUP_FILE_LEGACY):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        if was_on:
            return False
        try:
            with open(STARTUP_FILE, "w", encoding="utf-8") as f:
                f.write("@echo off\nchcp 65001 >nul\n")
                f.write('cd /d "%s"\n' % HERE)
                f.write('start "" "%s" "pet.pyw"\n' % PYTHONW)
            return True
        except Exception:
            return False


class PetView(QWebEngineView):
    """承载桌宠窗口；拦截 WM_HOTKEY 实现全局快捷键（Ctrl+Alt+W 切换专注模式）。"""
    def nativeEvent(self, eventType, message):
        if IS_WIN and eventType == b"windows_generic_MSG":
            try:
                msg = wintypes.MSG.from_address(int(message))
                if msg.message == 0x0312:  # WM_HOTKEY
                    p = self.page()
                    if isinstance(p, PetPage):
                        p.toggle_focus()
            except Exception:
                pass
        return super().nativeEvent(eventType, message)


def main():
    app = QApplication(sys.argv)

    view = PetView()
    view.setWindowFlags(BASE_FLAGS)
    view.setAttribute(Qt.WA_TranslucentBackground, True)
    view.setAttribute(Qt.WA_NoSystemBackground, True)
    view.resize(W, H)
    view.setWindowTitle("WhalePet 桌宠")

    page = PetPage(view, app, view)
    page.setBackgroundColor(QColor(0, 0, 0, 0))
    view.setPage(page)

    g = app.primaryScreen().availableGeometry()
    x, y = load_pos() or (g.x() + g.width() - W - 20, g.y() + g.height() - H - 60)
    view.move(x, y)

    view.load(QUrl.fromLocalFile(HTML))
    view.show()

    # 按上次保存的尺寸缩放（页面拿到 cfg 后会把缩放套到 #stage 上）
    sw, sh = page.cur_wh()
    view.resize(sw, sh)

    # 全局快捷键 Ctrl+Alt+W：切换专注模式（即便鼠标穿透也能触发）
    if IS_WIN:
        try:
            if ctypes.windll.user32.RegisterHotKey(int(view.winId()), 1, 0x0002 | 0x0001, 0x57):
                import atexit
                atexit.register(lambda: ctypes.windll.user32.UnregisterHotKey(int(view.winId()), 1))
            else:
                print("[warn] 注册全局快捷键 Ctrl+Alt+W 失败（专注模式将只能用 30 分钟定时退出）")
        except Exception as e:
            print("[warn] 全局快捷键不可用:", e)
    else:
        print("[info] 非 Windows 平台：全局快捷键与开机自启不可用，专注模式仍可从右键菜单进入（30 分钟自动退出）")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
