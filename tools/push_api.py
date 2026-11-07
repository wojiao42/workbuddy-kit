#!/usr/bin/env python3
"""
通过 GitHub REST API 推送本地仓库内容（绕过 git 协议）。

适用场景：网络只放行 api.github.com、git push / HTTPS 隧道被代理拦截时。

用法：
    set GH_TOKEN=ghp_xxx && python tools/push_api.py
    GH_TOKEN=ghp_xxx python3 tools/push_api.py wojiao42 workbuddy-kit

原理：
    对每个文件 POST /git/blobs
    → POST /git/trees（整棵树）
    → POST /git/commits
    → POST/PATCH /git/refs/heads/main

不会改动本地 git 状态；远程会得到一个新 commit，内容与工作区一致。
"""

import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://api.github.com"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    sys.exit("缺少 GH_TOKEN 环境变量")

OWNER = sys.argv[1] if len(sys.argv) > 1 else "wojiao42"
REPO = sys.argv[2] if len(sys.argv) > 2 else "workbuddy-kit"
BRANCH = "main"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def call(path, method="GET", data=None):
    url = API + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "workbuddy-push")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode() or "{}")
        except Exception:
            payload = {}
        return e.code, payload


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def make_blob(path):
    with open(os.path.join(ROOT, path), "rb") as f:
        data = f.read()
    status, res = call(f"/repos/{OWNER}/{REPO}/git/blobs", "POST", {
        "content": base64.b64encode(data).decode(),
        "encoding": "base64",
    })
    if status not in (200, 201):
        raise RuntimeError(f"blob 失败 {path}: {status} {res.get('message')}")
    return path, res["sha"], len(data)


def main():
    files = tracked_files()
    print(f"待推送文件：{len(files)} 个")

    status, ref = call(f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}")
    parent = None
    if status == 200:
        parent = ref["object"]["sha"]
        print(f"当前远程 HEAD：{parent[:8]}")
    else:
        print("远程为空仓库，将创建首个提交")

    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i, (path, sha, size) in enumerate(pool.map(make_blob, files), 1):
            results.append({"path": path, "mode": "100644", "type": "blob", "sha": sha})
            print(f"  [{i}/{len(files)}] {path} ({size} B)")

    status, tree = call(f"/repos/{OWNER}/{REPO}/git/trees", "POST", {"tree": results})
    if status not in (200, 201):
        sys.exit(f"创建 tree 失败：{status} {tree.get('message')}")
    print(f"tree 创建成功：{tree['sha'][:8]}")

    commit_body = {
        "message": "feat: WorkBuddy 资产库\n\n- experts/acg-hardcore: 九人 ACG 专家团 v1.1.0\n- 含跨平台导出（纯 system prompt）\n- 48 个文件，10 张头像",
        "tree": tree["sha"],
    }
    if parent:
        commit_body["parents"] = [parent]

    status, commit = call(f"/repos/{OWNER}/{REPO}/git/commits", "POST", commit_body)
    if status not in (200, 201):
        sys.exit(f"创建 commit 失败：{status} {commit.get('message')}")
    print(f"commit 创建成功：{commit['sha'][:8]}")

    if parent:
        status, upd = call(f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}", "PATCH", {
            "sha": commit["sha"], "force": False,
        })
    else:
        status, upd = call(f"/repos/{OWNER}/{REPO}/git/refs", "POST", {
            "ref": f"refs/heads/{BRANCH}", "sha": commit["sha"],
        })
    if status not in (200, 201):
        sys.exit(f"更新 ref 失败：{status} {upd.get('message')}")

    print(f"\n推送完成：https://github.com/{OWNER}/{REPO}")
    print(f"远程 HEAD 现在是 {commit['sha'][:8]}")

    status, ver = call(f"/repos/{OWNER}/{REPO}/git/trees/{tree['sha']}?recursive=1")
    if status == 200:
        print(f"远程文件数校验：{len(ver.get('tree', []))} 个")


if __name__ == "__main__":
    main()
