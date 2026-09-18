# WhalePet · 桌面宠物

**四个会漫游、会交谈的 AI 桌面伙伴 —— 每位角色拥有独特的语气与她自己的声音。**

Four AI desktop companions on your desktop — they wander, they talk, and each one has
her own personality and her own voice.

跨平台桌面宠物 / Cross-platform desktop pets · Windows · macOS · Linux · Python 3.9+

> ⚠️ 使用前请阅读文末 [**免责声明**](#免责声明--disclaimer)。本项目为个人非官方作品，按"现状"提供，不附带任何担保。
> Please read the [**Disclaimer**](#免责声明--disclaimer) at the end before use. Personal, unofficial project, provided "AS IS".

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

---

## 免责声明 · Disclaimer

**请在使用本项目之前完整阅读本节。下载、克隆、安装、运行或以任何方式使用本项目（以下统称"使用"），
即视为你已完整阅读、理解并无条件接受本节全部条款。若你不同意其中任何一条，请立即停止使用并删除本项目全部副本。**

### 一、非官方声明 · No Affiliation

1. 本项目为**个人独立开发的业余作品**，出于学习与技术交流目的发布，**不隶属于任何公司、组织或团体**。
2. 本项目**未获得任何第三方公司、品牌、厂商、平台或服务的授权、认可、赞助、合作、背书或技术支持**。
3. 本项目与任何人工智能服务提供商、语音合成服务提供商、即时通讯平台、操作系统厂商或硬件厂商**均无任何形式的关联**。
4. 本项目的角色名（鲸鱼娘 / 白龙娘 / 书卷娘 / 猫耳娘）系**按形象特征自行命名的描述性名称**，为原创设定，
   **不指向、不影射、不代表任何现实主体、企业、组织、品牌、产品或自然人**。如与任何既有名称存在巧合雷同，
   纯属无意，不构成任何形式的指代或关联。
5. 本项目立绘、角色设定、台词文本、代码均为原创或自行撰写，**如权利人认为本项目内容侵犯其合法权益，
   请通过仓库 Issue 联系，作者将在核实后于合理期限内删除或修改相关内容**。

### 二、技术与内容免责 · No Warranty

1. 本项目按 **"现状"（AS IS）** 提供，**不附带任何形式的明示或默示担保**，包括但不限于对**适销性、
   特定用途适用性、不侵权、准确性、完整性、无错误、无中断、无有害成分**的担保。上述担保在法律允许的
   最大范围内**全部予以排除**。
2. 作者**不保证**本项目的功能满足你的任何需求，**不保证**运行不中断、不出错、不含缺陷，
   也**不保证**任何缺陷会被修复。
3. 作者**不保证**本项目与你的操作系统、硬件环境、第三方软件、网络环境兼容。
4. 本项目**不是**生产力工具、**不是**安全工具、**不是**任何形式的专业建议来源（包括但不限于法律、
   医疗、金融、心理、安全建议）。由本项目输出的任何内容**均不应作为决策依据**。

### 三、语音与网络功能免责 · Voice & Network

1. 本项目的在线语音功能调用的是**第三方公开网络接口**，该接口**非本项目所有、非本项目运营、非本项目控制**，
   其可用性、稳定性、音质、响应速度、服务条款与计费政策**随时可能由第三方单方面变更、限制或终止**，
   **作者对此不作任何保证，亦不承担任何责任**。
2. 本项目的在线语音**可能向你所在地区或网络环境不可达**。作者不保证在任何地区、任何网络、任何时间可用。
3. 使用在线语音功能时，**待朗读的文本内容会经由第三方服务处理**。**你应自行判断待合成文本是否包含
   个人隐私、商业秘密、敏感信息或受法律保护的内容，并自行承担由此产生的一切后果。作者不建议将本项目
   用于播报任何敏感或机密信息。**
4. 离线语音依赖操作系统内置引擎，其可用性、音色与效果**因系统版本与语言包而异**，作者不作保证。
5. 本项目**不主动收集、不上传、不存储、不分析**你的任何个人数据。所有配置与位置信息均以明文形式
   保存在你本机目录下（`.pet_cfg.json` / `.pet_pos.json`），**请自行注意该等文件的保密与备份**。

### 四、使用限制 · Usage Restrictions

1. 使用者应**自行确保其使用行为符合其所在国家或地区的全部适用法律法规、政策要求及公序良俗**。
2. **禁止**将本项目用于任何违法违规用途，包括但不限于：制作、传播违法信息；侵犯他人知识产权、
   名誉权、隐私权或其他合法权益；实施骚扰、欺诈、诈骗或其他侵害行为；规避、破坏任何安全机制。
3. **禁止**将本项目或其衍生作品用于**任何商业营销、品牌代言、官方客服、自动化应答**等
   可能使公众误认为其与任何企业、品牌或服务存在关联的场景。
4. **禁止**移除、篡改、隐藏本项目中的版权声明、许可条款与本免责声明。
5. 使用者因违反上述限制而产生的**一切法律责任与后果，由使用者自行独立承担**，与作者无关。

### 五、责任限制 · Limitation of Liability

1. **在适用法律允许的最大范围内，作者及任何贡献者，对因使用或无法使用本项目而导致的任何
   直接、间接、附带、特殊、惩罚性、示范性或后果性损害，概不承担责任。** 该等损害包括但不限于：
   数据丢失或损坏、设备损坏、系统故障、业务中断、利润损失、商誉损失、第三方索赔、
   以及因语音内容引发的任何争议或纠纷。
2. **无论损害因何原因引起、基于何种责任理论（合同、侵权、过失或其他），亦无论作者是否已被告知
   该等损害发生的可能性，上述责任限制均适用。**
3. **若部分司法管辖区不允许排除或限制某些担保或责任，则本节条款在该等管辖区内应在法律允许的
   最大范围内适用；本节任何条款被认定无效或不可执行，不影响其余条款的效力。**
4. 你使用本项目的**全部风险由你自行承担**。因使用本项目产生的**全部后果由你自行负责**。

### 六、第三方组件 · Third-Party Components

1. 本项目依赖于若干第三方开源组件（如 PySide6 / Qt、edge-tts、pyttsx3 等），
   该等组件**各自适用其自身的许可条款**，与本项目许可相互独立。
2. 你应自行查阅并遵守上述第三方组件的许可条款。**因违反第三方许可而产生的任何责任，
   由你自行承担**，与本项目作者无关。
3. 本项目不包含、不分发、不转授任何第三方的专有代码、模型权重、字体或素材。

### 七、许可范围 · Scope of License

1. 本项目代码以 **MIT 协议**发布，具体条款以仓库根目录 `LICENSE` 文件为准。
2. **MIT 协议仅约束代码的使用、复制、修改与分发。本节免责声明是对使用行为的额外风险提示与
   责任界定，不构成对 MIT 协议所授予权利的削减。**
3. 若本节任何内容与 MIT 协议正文存在冲突，**就责任限制与风险分配事项，以本节约定为准**；
   就代码授权范围事项，以 MIT 协议为准。

### 八、条款变更与解释 · Changes & Interpretation

1. 作者**保留随时修改、更新、暂停或终止本项目及本免责声明的权利，且无需事先通知**。
   修改后的条款自仓库更新之日起生效，你继续使用即视为接受修改后的条款。
2. 本节标题仅为阅读便利而设，**不影响任何条款的含义或解释**。
3. 本免责声明以**中文版本为准**，英文译文（如有）仅供参考。

---

## 关于本文件 · About This Document

本 README 文档由 AI 生成，内容经人工审阅与调整。
This README was generated by AI and reviewed and adjusted by a human.

---

**English Summary (for reference only — the Chinese text above prevails) / 英文摘要（仅供参考，以上方中文为准）**

This project is a personal, non-commercial hobby work released for learning purposes.
It is **not affiliated with, authorized by, endorsed by, or sponsored by any company,
brand, platform, or service provider**. All character names are descriptive and original,
and do not refer to or imply any real entity.

The software is provided **"AS IS", without warranty of any kind**, express or implied,
including but not limited to the warranties of merchantability, fitness for a particular
purpose, and non-infringement. **In no event shall the author be liable for any claim,
damages, or other liability, whether in an action of contract, tort, or otherwise,
arising from, out of, or in connection with the software or the use or other dealings
in the software.** You assume all risk and responsibility for your use of this project.

Online voice synthesis relies on a **third-party public network interface** that is not
owned, operated, or controlled by this project; its availability, terms, and policies
may change or be discontinued at any time without notice, and the author assumes no
responsibility for it. Text submitted for synthesis is processed by that third party —
**do not use this feature to speak any sensitive, private, or confidential information.**

You are solely responsible for ensuring that your use complies with all applicable laws
and regulations in your jurisdiction. Commercial use for marketing, brand endorsement,
official customer service, or automated response purposes is prohibited.

**This disclaimer is governed by the Chinese text above.**
