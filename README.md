# WorkBuddy 资产库

> 自己做的 WorkBuddy 专家团、技能与配置，集中放一个仓库。
> 每个资产自成目录，互不干扰；改哪个进哪个目录。

## 目录约定

```
workbuddy-kit/
├── experts/            专家 / 专家团
│   └── <name>/         一个完整专家包（可直接落进 plugins 目录）
├── skills/             技能（预留）
├── notes/              配置笔记、踩坑记录（预留）
├── LICENSE
└── .gitignore
```

**命名规则**：目录名 = 专家包的 `name` 字段（kebab-case），全仓库唯一。

## 现有资产

| 目录 | 版本 | 说明 |
|---|---|---|
| [`experts/acg-hardcore`](experts/acg-hardcore/) | 1.1.0 | ACG硬核团。九人专家团：番剧考据、游戏设定、硬核机制、复古硬件、工具开发、实战画师、梗源流、二创编剧、主编。附平台无关导出。 |

## 安装某个专家

```bash
# 1. 复制到 WorkBuddy 的专家目录
cp -r experts/acg-hardcore ~/.workbuddy/plugins/marketplaces/my-experts/plugins/

# 2. 注册（让它出现在专家中心）
python3 <workbuddy>/skills/expert-manager/scripts/register_expert.py \
  ~/.workbuddy/plugins/marketplaces/my-experts/plugins/acg-hardcore
```

Windows 上路径是 `%USERPROFILE%\.workbuddy\plugins\marketplaces\my-experts\plugins\`。

**目录名必须和包内 `name` 字段一致**，否则 `agentName` 会对不上，专家加载失败。

## 新增一个专家

1. 在 `experts/` 下建目录，名称为 kebab-case 的 `name`
2. 放入 `.codebuddy-plugin/plugin.json`、`agents/*.md`、`avatars/`、`settings.json`
3. 跑一次 `validate_expert.py` 确认字段合规
4. 在下面的资产表里加一行

如果这个专家也需要跨平台使用，就在包内加 `tools/export_portable.py` 并生成 `portable/`（照着 `acg-hardcore` 的结构）。

## 关于跨平台

`experts/acg-hardcore/portable/` 里是剥掉平台私有格式的纯系统提示词，可以在 DeepSeek / ChatGPT / Claude 等任意支持 system role 的模型上使用。

**注意**：角色提示词通用，但「主理人自动派活、成员之间经主理人中转」这套编排是 WorkBuddy 独有的运行时能力，换平台必然降级。纯文本平台上建议只挑单个角色用。

详见 [`experts/acg-hardcore/portable/README.md`](experts/acg-hardcore/portable/README.md)。

## 许可

MIT。各目录内的资产可能有各自的 LICENSE，以子目录为准。
