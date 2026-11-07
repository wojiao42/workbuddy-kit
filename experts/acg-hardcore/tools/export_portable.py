#!/usr/bin/env python3
"""
把 WorkBuddy 专家包导出为平台无关格式。

输入：本仓库根目录（含 .codebuddy-plugin/plugin.json 与 agents/*.md）
输出：portable/
    agents/<id>.system.md   纯系统提示词（已剥离 YAML frontmatter）
    agents/<id>.json        {"model":null,"messages":[{"role":"system","content":...}]}
    team.json               编排定义（谁调度谁、成员清单）
    index.json              索引

用法：
    python3 tools/export_portable.py
    python3 tools/export_portable.py <package-root> <output-dir>
"""

import json
import re
import sys
from pathlib import Path


def split_frontmatter(text):
    """返回 (meta_dict, body)。支持一层嵌套的 YAML，够用。"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw_fm, body = parts[1], parts[2].lstrip("\n")

    meta = {}
    current = None
    for line in raw_fm.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        # 顶层空值键 -> 进入嵌套
        if re.match(r"^[A-Za-z0-9_-]+:\s*$", line):
            current = line.split(":")[0].strip()
            meta[current] = {}
            continue
        # 顶层 key: value
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.+)$", line)
        if m and not line.startswith((" ", "\t")):
            key, val = m.group(1), m.group(2).strip()
            meta[key] = val.strip('"').strip("'")
            current = key
            continue
        # 嵌套 key: value
        m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.+)$", line)
        if m and isinstance(meta.get(current), dict):
            meta[current][m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return meta, body


def export(root: Path, out: Path):
    plugin_json = root / ".codebuddy-plugin" / "plugin.json"
    if not plugin_json.exists():
        sys.exit(f"找不到 {plugin_json}")

    cfg = json.loads(plugin_json.read_text(encoding="utf-8"))
    agents_dir = root / "agents"
    out_agents = out / "agents"
    out_agents.mkdir(parents=True, exist_ok=True)

    index = []
    for md in sorted(agents_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        meta, body = split_frontmatter(text)
        agent_id = md.stem

        (out_agents / f"{agent_id}.system.md").write_text(body, encoding="utf-8")

        payload = {
            "id": agent_id,
            "displayName": meta.get("displayName", {}),
            "profession": meta.get("profession", {}),
            "description": meta.get("description", ""),
            "messages": [{"role": "system", "content": body}],
        }
        (out_agents / f"{agent_id}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        index.append(
            {
                "id": agent_id,
                "name": meta.get("displayName", {}),
                "profession": meta.get("profession", {}),
                "system_prompt": f"agents/{agent_id}.system.md",
            }
        )
        print(f"  exported {agent_id}")

    lead_id = cfg.get("agentName") or cfg.get("teamInfo", {}).get("leadAgent")
    team = {
        "schema": "portable-expert-team/v1",
        "type": cfg.get("expertType", "agent"),
        "name": cfg.get("name"),
        "version": cfg.get("version"),
        "displayName": cfg.get("displayName", {}),
        "profession": cfg.get("profession", {}),
        "description": cfg.get("description", ""),
        "category": cfg.get("categoryId"),
        "source": "WorkBuddy expert package",
        "lead": next((a for a in index if a["id"] == lead_id), None),
        "members": [a for a in index if a["id"] != lead_id],
        "orchestration": {
            "note": "以下约定源自主理人的系统提示词，非 WorkBuddy 平台也可按此手动或程序化实现。",
            "rules": [
                "主理人负责分诊、编排、边界仲裁与汇编，不代写成员产出",
                "按阶段串行/并行调度成员，跨成员信息流一律经主理人中转",
                "成员产出原文回传，不做摘要转交",
                "任何专业结论必须由对应成员输出后才可采信",
            ],
        },
    }
    (out / "team.json").write_text(
        json.dumps(team, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "index.json").write_text(
        json.dumps({"agents": index}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n✅ 导出完成：{out}")
    print(f"   成员 {len(index)} 人，主理人 {lead_id}")


if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else root / "portable"
    export(root, out)
