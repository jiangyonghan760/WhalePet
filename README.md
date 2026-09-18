# WhalePet · 桌面宠物

**四个会溜达、会说话的 AI 娘住在你的桌面上 —— 每个人有自己的语气和她自己的声音。**

Four AI girls living on your desktop — they wander, they talk, and each one has
her own personality and her own voice.

跨平台桌面宠物 / Cross-platform desktop pets · Windows · macOS · Linux · Python 3.9+

---

## 她们是谁 · The Cast

| 角色 | 人设 | 声音 | 语气示例 |
|---|---|---|---|
| **鲸鱼娘** | 吃白饭的蓝色大肥鱼，呆萌迟钝，满脑子只有饭 | 软糯：音调抬高、语速放慢 | 「饭……饭好了吗？」 |
| **白龙娘** | 白龙大小姐，眼高于顶、嘴上不饶人 | 倨傲：音调压低、音量偏轻 | 「有事说事。」「重写。」 |
| **书卷娘** | 抱着书的橙发学姐，半垂着眼、话少而沉 | 疏离：语速平缓、无起伏 | 「……嗯，我在。」 |
| **猫耳娘** | 猫耳狼尾的小恶魔，爱逗人但推理毫不含糊 | 俏皮：语速偏快、音调上扬 | 「喵～找我？我可是很贵的哦。」 |

不是换皮：**台词库、音色、语速音调、菜单配色**都是一套一套分开的。

---

## 快速开始 · Quick Start

```bash
git clone https://github.com/jiangyonghan760/WhalePet.git
cd WhalePet
python install_deps.py     # 装依赖
python run.py              # 启动
```

Windows 用户直接双击 **`launch.bat`** 也行。只想先看看立绘长啥样，双击 `open_browser.html`。

> 觉得 pip 慢就换国内源：
> `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

---

## 怎么玩 · Interactions

| 操作 | 效果 |
|---|---|
| **拖动** | 把她挪到任意位置（位置自动记住） |
| **单击** | 戳一戳，看她的反应 |
| **双击** | 摸头，开心时会飘爱心 |
| **右键** | 呼出菜单 |
| **Ctrl+Alt+W** | 专注模式：鼠标穿透，30 分钟后自动退出（仅 Windows） |

右键菜单里能改：**说点什么 / 自动游荡 / 音效 / 语音 / 大小 / 角色 / 音色 / 专注模式 / 开机自启 / 回到右下角 / 隐藏**。

---

## 语音是怎么回事 · How the Voice Works

语音分两层，**在线优先、离线兜底**，换台电脑也能用。

**在线（Edge TTS，默认）**
调微软 Edge 的神经语音，**免费、不用注册、不用 API key**——它是个公开的 WebSocket 接口，不是需要申请额度的 API。音质比本地合成好一大截，而且支持调**语速 / 音调 / 音量**三个参数——角色之间听感拉开主要靠音调。

**离线（SAPI，兜底）**
断网或者在线合成失败时自动接管。用的是系统自带语音（Windows SAPI / macOS NSSpeechSynthesizer）。
⚠️ 系统语音引擎**只认语速，不认音调和音量**，所以离线状态下四个角色主要靠语速快慢区分。

**关于方言音色的取舍**：中文女声里有个陕西话的 `zh-CN-shaanxi-XiaoniNeural`，音色其实很适合书卷娘的沉静感。但它属于小众方言音色，不同版本的服务端覆盖情况不一致，**为了保证换机器一定能出声**，本项目只使用 `zh-CN-XiaoyiNeural` 和 `zh-CN-XiaoxiaoNeural` 这两个覆盖率最高的普通话女声，靠音调参数做出四种差异——这样任何人 clone 下来都能正常听到。

**音色可以单独挑**：菜单里「音色」那一行能直接选软糯 / 倨傲 / 疏离 / 俏皮，不必跟着角色走。手动选过之后就会被记住，换角色也不会被覆盖。

---

## 自定义 · Customization

加一个角色只要三步：

1. 立绘丢进根目录（建议 1024×1536 透明 PNG，七到八头身的正常人体比例）
2. 在 `whale.html` 的 `SKINS` 数组里加一条——填 `id / name / img / accent / soft / line / persona / talks / poke / happy`
3. 在 `pet.pyw` 的 `VOICE_PRESETS` 里加同名一条 —— 填 `voices / rate / pitch / volume`

菜单里的角色项直接复制一行 `<div data-skin="你的id">名字</div>` 就行。**加角色不需要动其他代码**。

### 音调参数怎么调 · Tuning Pitch

`pitch` 是拉开音色差异最有效的旋钮，单位是 Hz：

- 想更软更萌 → `+30Hz` 以上
- 想更冷更低沉 → `-15Hz` 以下
- 同一个基础音色，只改 pitch 就能出两种明显不同的听感

---

## 项目结构 · Layout

```
WhalePet/
├── pet.pyw            # 宿主：透明置顶窗口、语音、窗口移动、配置持久化
├── whale.html         # 页面：立绘、动画、气泡、台词库、右键菜单（单文件，零外部资源）
├── run.py             # 启动器（挑无控制台解释器）
├── install_deps.py    # 一键装依赖
├── requirements.txt
├── launch.bat / .sh   # Windows / macOS·Linux 启动脚本
├── open_browser.html  # 纯浏览器预览
└── *.png              # 四个角色的立绘（char_whale / char_dragon / char_book / char_cat）
```

运行时会在目录下生成两个文件，**已在 `.gitignore` 里排除**：
`.pet_cfg.json`（静音/语音/角色/音色/尺寸）、`.pet_pos.json`（窗口位置）。

---

## 原理 · How It Works

宿主（PySide6）开一个透明无边框置顶窗口，里面塞一个 `QWebEngineView` 加载 `whale.html`。
两边通过一个**轮询式命令队列**通信：页面把 `{c: 命令, a: 参数, i: 请求id}` 推进 `__queue`，
宿主每 50ms 拉一次 `window.__drain()` 取走并执行，需要返回值的用 `window.__apiResult(id, value)` 回传。

这么做的好处是**页面单独用浏览器打开也能跑**（检测不到宿主就自动降级），改 UI 不用起桌面环境。

窗口缩放是**双份**的：宿主 `resize` 真实窗口，页面同时给 `#stage` 套 `transform: scale()` —— 所以右键菜单的定位要用鼠标坐标**除以缩放比**才能对齐。

---

## 已知限制 · Known Limitations

- **全局快捷键和开机自启只有 Windows 有**。macOS / Linux 上这两个菜单项不可用，专注模式仍可从菜单进入（30 分钟自动退出）。
- 语音播放：Windows 用系统自带 `winmm`；macOS / Linux 需要 `afplay` / `mpg123` / `ffplay` 三者之一，都没有的话语音静默跳过（其他功能不受影响）。
- 在线语音需要联网，首次合成有约 1 秒延迟。

---

## 立绘说明 · Artwork

仓库里的立绘和角色均为**原创**，跟着代码一起以 MIT 协议开源。角色名（鲸鱼娘 / 白龙娘 / 书卷娘 / 猫耳娘）是
按形象特征起的描述性名字，不含任何品牌指向。

## 许可 · License

MIT
