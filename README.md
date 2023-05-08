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

✅ 现实感知：AI 可以感知现实的时间并模拟自己的状态和行为，例如晚上会在睡觉、用户隔很久回复会有相应反馈（这部分表现暂时不稳定）

✅ 联网搜索：根据用户的信息，自主构造搜索决策，并引入上下文。

- [ ] vits 双语（中、日）多音色支持
- [ ] emotion-vits 支持
- [ ] bark 支持
- [ ] QQ 机器人部署
- [ ] 人设模板、自定义人设

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
