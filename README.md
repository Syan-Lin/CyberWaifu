# CyberWaifu

### 项目介绍

CyberWaifu 是一个使用 ChatGPT 和 Vits 语音合成的实时聊天系统，实现与 AI 老婆语音聊天的项目。

该项目基于：
1. [chatgpt-vits-waifu](https://github.com/Li-kaige/chatgpt-vits-waifu)
2. [vits-models](https://huggingface.co/spaces/zomehwh/vits-models)

有多音色选择和双语支持（日语和汉语），具有长对话自动总结和保存功能，让 AI 老婆具有长期记忆力，同时 AI 老婆可以感知时间的流逝，例如一天之后交流。

支持自定义人设，默认自带了几个精心调教的预设人设。

### 功能

- [x] 双语语音回复
- [x] 中文语音包（12 种声线）
- [x] 日文语音包（14 种声线）
- [x] 精心预设人设（对现实时间有感知，不同的时间有不同的反应）
- [x] 自定义人设
- [ ] 图形化界面
- [ ] QQ/微信 部署
- [ ] 服务器架设

### 安装

Python 版本：3.10.10

使用 conda:
```powershell
git clone https://github.com/Syan-Lin/CyberWaifu
cd CyberWaifu
conda create --name CyberWaifu python=3.10.10
conda activate CyberWaifu
pip install -r requirements.txt
```

### 运行

填写 `api.json` 中的相关信息，需要梯子

```powershell
python CyberWaifu.py
```

语言和语音包：
- 日语需要配置百度翻译 API
- 中文微软语言包需要配置 Azure 语音服务的 API
