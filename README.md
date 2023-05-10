![cover](assets/cover.jpg)

<p align="center">
  <a href="https://github.com/Syan-Lin/CyberWaifu/stargazers"><img src="https://img.shields.io/github/stars/Syan-Lin/CyberWaifu?color=cd7373&amp;logo=github&amp;style=for-the-badge" alt="Github stars"></a>
  <img src="https://img.shields.io/badge/Python-3.10.10-blue?style=for-the-badge&logo=Python&logoColor=white&color=cd7373" alt="Python">
  <a href="./LICENSE"><img src="https://img.shields.io/github/license/Syan-Lin/CyberWaifu?&amp;color=cd7373&amp;style=for-the-badge" alt="License"></a>
</p>


---

### 介绍🔎

CyberWaifu 是一个使用 LLM 和 TTS 实现的聊天机器人，探索真实的聊天体验。

该项目使用 [LangChain](https://github.com/hwchase17/langchain) 作为 LLM 主体框架，使用 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 进行 QQ 机器人部署，TTS 支持 vits、[edge-tts](https://github.com/rany2/edge-tts)。

### 功能

✅ 预定义的思考链：使 AI 可以进行一定的逻辑思考，进行决策。例如在文本中添加 Emoji、发送表情包等等。

✅ 记忆数据库：自动总结对话内容并导入记忆数据库，根据用户的提问引入上下文，从而实现长时记忆。同时支持批量导入记忆，使人设更丰富、真实和可控。

✅ 现实感知：AI 可以感知现实的时间并模拟自己的状态和行为，例如晚上会在睡觉、用户隔很久回复会有相应反馈（这部分表现暂时不稳定）。

✅ 联网搜索：根据用户的信息，自主构造搜索决策，并引入上下文。

✅ QQ 机器人部署

✅ QQ 表情支持

✅ 人设模板、自定义人设

✅ edge-tts, azure 语音服务支持

⬜ vits, emotion-vits 支持

⬜ bark 支持

⬜ AI 绘图支持，将绘图引入思考链，使 AI 可以生成图片，例如 AI 自拍

### 安装💻

Python 版本：3.10.10

使用 conda:
```powershell
git clone https://github.com/Syan-Lin/CyberWaifu
cd CyberWaifu
conda create --name CyberWaifu python=3.10.10
conda activate CyberWaifu
pip install -r requirements.txt
```

#### QQ 机器人部署
根据 [go-cqhttp 下载文档](https://docs.go-cqhttp.org/guide/quick_start.html#%E4%B8%8B%E8%BD%BD)，下载相应平台的可执行程序，并放入 `qqbot` 目录中

#### ffmpeg 安装
为了支持任意格式的语音发送，按照 go-cqhttp 要求，需要 [下载ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z) 解压到 `qqbot/ffmpeg` 文件夹中（如果不存在请自行创建）

Windows 在 cmd 中执行：X 部分替换为你的项目所在目录，设置完成后需要重启电脑
```cmd
setx /M PATH "X:\XXX\CyberWaifu\qqbot\ffmpeg\bin;%PATH%"
```

### 配置✏️

按照 `template.ini` 进行配置，配置完成后改名为 `config.ini`

#### QQ 机器人配置：
运行 `main.py` 提示：

```
PyCqBot: go-cqhttp 警告 账号密码未配置, 将使用二维码登录.
PyCqBot: go-cqhttp 警告 虚拟设备信息不存在, 将自动生成随机设备.
PyCqBot: go-cqhttp 警告 当前协议不支持二维码登录, 请配置账号密码登录.
```

在 `qqbot/device.json` 文件中，找到字段 `protocol`，将值修改为 2 即可扫码登录

权限设置：`qqbot/bot.json` 文件

```json5
{
    // 需处理的 QQ 群信息 为空处理所有，目前的 AI 思考链针对私聊设计，群聊效果并不好
    "group_id_list": [
        123456,
        654321
    ],
    // 需要处理的 QQ 私聊信息，为空处理所有
    "user_id_list": [
        1234567,
        7654321
    ]
}
```

#### 人设 Prompt 配置
根据 `presets/charactor/模板.txt` 进行编写，将编写好的人设 Prompt 丢到 `presets/charactor` 目录下即可，随后在 `config.ini` 配置文件中的 `charactor` 字段填写文件名（不包含后缀名）

记忆设定同样是丢到 `presets/charactor` 目录下，多段记忆用空行分开，并在配置文件中填写 `memory` 字段