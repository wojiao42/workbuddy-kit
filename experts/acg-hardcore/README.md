# ACG硬核团 · ACG Hardcore Crew

> 九个人的 ACG 专家团，做考据、算数值、拆硬件、写工具、画图、讲梗。
> 一条底线：**说不出来的就是没看懂，拿不出数字的就不算结论。**

一个 WorkBuddy 专家团（Team 型），同时导出为**平台无关**的系统提示词，可以拿到任何支持 system prompt 的模型上用。

---

## 为什么做这个

大多数 ACG 向的 AI 助手都很"泛"：问它一个梗，它会给你一段像模像样的溯源；问它伤害怎么算，它会说"取决于装备和属性"。

这个团的设计目标是反过来的——**每个结论都要能指回它在哪一层**：

- 事实分三层标注：`[官方]` / `[弱表述]` / `[二设]`
- 技术结论必须带版本前提：补丁号、固件版本、接口版本
- 查不到就写「未确认」，**禁止编造** staff 名、集数、任务名、发售日、API 端点
- 拿不出依据的判断，不输出

## 九人编制

按「看的 / 玩的 / 做的 / 说的」四分域，主理人只做编排，不代写。

### 看的

| 角色 | 代号 | 干什么 |
|---|---|---|
| 番剧考据官 | `anime-canon-researcher` | 作品谱系、staff、时间线、改编差异、作画与演出 |
| 游戏设定考据师 | `game-lore-analyst` | 世界观分层、战力边界、版本沿革、叙事结构 |

### 玩的

| 角色 | 代号 | 干什么 |
|---|---|---|
| 硬核技术玩家 | `hardcore-mechanics-player` | 判定帧、伤害公式、最优配装、速通路线、对战复盘 |
| 极客装备官 | `retro-gear-geek` | 老主机改机、模拟器调优、延迟链路诊断、采集串流、存档保存 |

### 做的

| 角色 | 代号 | 干什么 |
|---|---|---|
| ACG程序员 | `acg-tool-developer` | 番剧表/弹幕抓取、同人游戏原型、Mod 工具链、AI 流水线 |
| 实战画师 | `visual-art-director` | 直接出图与改图、画风辨识、四轴作画拆解、prompt 一致性 |

### 说的

| 角色 | 代号 | 干什么 |
|---|---|---|
| 梗源流研究员 | `meme-culture-researcher` | 出处溯源、传播链路、语义漂移、保鲜期、圈层风险 |
| 二创编剧 | `fanwork-writer` | 二创、整活、安利避雷、OOC 控制 |

主理人：**次元内容主编** `acg-hardcore-team-lead` —— 分诊、编排、边界仲裁、汇编。

## 九条预设链路

| 编号 | 链路 | 触发场景 |
|---|---|---|
| A | 梗档案 | 梗哪来的、什么意思、能不能用 |
| B | 作品全解 | 值不值得看/玩、该看哪一版 |
| C | 二创生产 | 要文案 + 配图，图文双出 |
| D | 设定深挖 | 前后矛盾吗、战力崩了吗、吃书了吗 |
| E | 圈层速查 | 黑话术语、弹幕看不懂 |
| F | 变强拆解 | 伤害公式、配装、速通、连不上招 |
| G | 折腾设备 | 画面糊、手感飘、延迟高、老机器怎么救 |
| H | 开发交付 | 写脚本、抓数据、同人游戏、mod |
| I | 直接出图 | 画一张、做表情包、场景图 |

关键铁律：**C 链路没有设定边界包不许动笔，没有成稿不许配图**——否则图和文必然对不上。

## 装在 WorkBuddy 里

```bash
cd ~/.workbuddy/plugins/marketplaces/my-experts/plugins/
git clone <this-repo> acg-hardcore
```

或者把仓库打成 zip，解压到这个目录（文件夹名必须是 `acg-hardcore`）。

然后注册：

```bash
python3 <workbuddy>/skills/expert-manager/scripts/register_expert.py acg-hardcore
```

重启客户端，在「专家 → 我的专家」里就能看到。

## 装在其他平台上（DeepSeek / ChatGPT / Claude / Kimi…）

看 [`portable/README.md`](portable/README.md)。

一句话总结：**角色提示词通用，团队编排和工具能力不通用。**

```bash
python3 tools/export_portable.py
```

会生成 `portable/agents/*.system.md`（纯系统提示词）和 `portable/team.json`（编排定义），可直接贴进任何聊天窗口或 API 调用。

> 在纯文本平台上，**建议只挑 1–2 个角色用**，别硬套九人团队——没有人替你分诊时，主理人的路由表会变成噪音。

## 目录结构

```
acg-hardcore/
├── .codebuddy-plugin/plugin.json   WorkBuddy 包配置
├── agents/                          9 个角色的系统提示词（带 YAML frontmatter）
├── avatars/                         10 张头像，512×512
├── portable/                        跨平台导出（自动生成）
│   ├── agents/*.system.md
│   ├── agents/*.json
│   ├── team.json
│   └── README.md
├── tools/export_portable.py         导出脚本
├── settings.json
└── README.md
```

## 明确不做

- 受版权保护的影音、游戏资源及其获取途径
- 外挂、破解、私服、绕过付费墙与 DRM
- 破坏多人对战公平性的脚本
- 包装成"玩梗"的歧视性内容

这些不是 README 上的装饰，是写进各角色系统提示词的运行时约束。

## 头像

统一漫画插画风，512×512，单张 ≤500KB，AI 生成。可自行替换，文件名保持不变即可。

## License

MIT。角色提示词随便改、随便用；头像为 AI 生成，可自行替换。
