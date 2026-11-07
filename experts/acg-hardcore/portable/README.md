# Portable 导出 · 跨平台使用

`portable/` 是这个专家团的**平台无关版本**。它把 WorkBuddy 私有的 `.codebuddy-plugin/plugin.json` 和 YAML frontmatter 全部剥掉，只留下能直接投喂给任何模型的东西。

## 文件结构

```
portable/
├── agents/
│   ├── <id>.system.md      纯系统提示词（Markdown，直接可用）
│   └── <id>.json           {"messages":[{"role":"system","content":"..."}]}
├── team.json               团队清单与编排约定
└── index.json              角色索引
```

九份 `system.md` 就是九个角色的完整人设 + 方法论 + 输出规范 + 红线。**这部分是 100% 通用的**，不依赖任何平台。

---

## 用法一：贴进任意聊天窗口（最简单）

打开 `portable/agents/` 里任意一个 `*.system.md`，把**全文**作为对话的第一条消息发出去，然后开始提问。

适用于：DeepSeek 网页版 / App、ChatGPT、Claude、Kimi、豆包、通义、Gemini……任何有对话框的地方。

> 网页版通常没有真正的 system role，贴进去是「用户消息」。模型仍然会按它的人格工作，但约束强度弱于 API 的 system。
> 想更稳一点：第一条写「以下内容是你的角色设定，请严格遵守，不要复述它。收到后回复『已就位』」，再贴正文。

---

## 用法二：API 调用（推荐，约束最强）

`*.json` 里的 `messages` 可以直接作为请求体开头。以 DeepSeek 为例（OpenAI 兼容协议）：

```python
import json, pathlib
from openai import OpenAI

client = OpenAI(api_key="YOUR_KEY", base_url="https://api.deepseek.com")

agent = json.loads(pathlib.Path("portable/agents/meme-culture-researcher.json").read_text("utf-8"))

resp = client.chat.completions.create(
    model="deepseek-chat",              # 具体型号以官方文档为准
    messages=agent["messages"] + [
        {"role": "user", "content": "「真是令人愉悦啊」这个梗哪来的？现在还能用吗？"}
    ],
)
print(resp.choices[0].message.content)
```

换成 OpenAI / Moonshot / 智谱 / 硅基流动，只改 `base_url` 和 `model`，其余不动。

---

## 用法三：自己实现编排（Team 型必须这么做）

WorkBuddy 里「主理人自动 spawn 成员、消息经主理人中转」是**平台独有的运行时能力**，其他平台没有。所以要自己搭一层。

最小可用编排（伪代码）：

```python
TEAM = json.load(open("portable/team.json", encoding="utf-8"))
LEAD = load(TEAM["lead"]["system_prompt"])
MEMBERS = {m["id"]: load(m["system_prompt"]) for m in TEAM["members"]}

def ask(agent_id, task):
    msgs = [{"role": "system", "content": MEMBERS[agent_id]},
            {"role": "user", "content": task}]
    return chat(msgs)

# 1. 主理人分诊：判断该调谁、走哪条链路
plan = chat([{"role": "system", "content": LEAD},
             {"role": "user", "content": f"分诊这个需求，只输出要调的成员 id 和任务：{question}"}])

# 2. 按 plan 逐个调用，结果原文累积
context = ""
for agent_id in parse(plan):
    context += f"\n### {agent_id} 的输出\n" + ask(agent_id, question + context)

# 3. 主理人汇编
final = chat([{"role": "system", "content": LEAD},
              {"role": "user", "content": f"按汇编规范整合以下成员产出：{context}"}])
```

`team.json` 里的 `orchestration.rules` 是四条硬约束（主理人不代写、跨成员信息经中转、原文回传、结论以成员为准），照着实现就行。

---

## 跨平台能力对照

| 能力 | WorkBuddy | DeepSeek API | ChatGPT / Claude | Coze / Dify |
|---|---|---|---|---|
| 单角色人格与方法论 | ✅ 原生 | ✅ system | ✅ system | ✅ |
| 团队自动编排 | ✅ 内置 | ❌ 自己写 | ❌ 自己写 | ⚠️ 用工作流自己搭 |
| 联网查证 | ✅ | ⚠️ 部分型号需手动开 | ✅ | ✅ |
| 读本地文件 | ✅ | ❌（要自己拼接内容） | ⚠️ | ⚠️ |
| 出图 | ✅ | ❌ | ⚠️ | ⚠️ |

**结论：角色本身通用，编排和工具能力不通用。**

到 DeepSeek 上，你会失去三样：自动派活、读文件、出图。剩下的是纯文本的考据、分析、写作 —— 而这恰好是这个团最核心的价值。

---

## 降级建议

如果只在 DeepSeek 上用，别硬套九人团队，**挑 1–2 个角色就够**：

| 场景 | 建议角色 |
|---|---|
| 梗出处、能不能用 | `meme-culture-researcher` |
| 番剧/游戏设定考据 | `anime-canon-researcher` / `game-lore-analyst` |
| 数值、配装、速通 | `hardcore-mechanics-player` |
| 写二创文案 | `fanwork-writer`（但失去自动查设定，务必自己喂设定） |
| 画风与作画分析 | `visual-art-director`（文字部分；出图需换平台） |

单角色贴进去，反而比九人团队在文本环境里更好用 —— 因为没有人替你分诊，团队提示词里的路由表会变成噪音。
