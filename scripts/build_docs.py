#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
DOCS = ROOT / "docs"
CATEGORIES = DOCS / "categories"


CATEGORY_RULES = [
    ("编程语言与工程基础", ["java", "python", "rust", "c++", "cpp", "go", "php", "coding", "developer", "clean-code", "code-mentor", "code-executor", "全栈", "前端开发", "程序", "开发"]),
    ("前端、移动端与交互体验", ["frontend", "react", "vue", "android", "ios", "flutter", "swiftui", "ui", "ux", "design", "canvas", "web-artifacts", "小程序", "移动", "前端", "设计"]),
    ("后端、云平台与 API", ["api", "cloud", "cloudbase", "server", "backend", "docker", "mcp", "gateway", "腾讯云", "cloudflare", "数据库", "云", "后端"]),
    ("AI、Agent 与模型应用", ["ai", "agent", "llm", "gpt", "claude", "gemini", "model", "prompt", "openai", "image", "video", "voice", "模型", "智能体", "绘图", "语音", "视频"]),
    ("数据、算法与科研", ["data", "algorithm", "research", "academic", "arxiv", "paper", "stock", "finance", "excel", "spreadsheet", "算法", "数据", "论文", "科研", "金融"]),
    ("浏览器、搜索与自动化", ["browser", "scrape", "crawler", "search", "playwright", "firecrawl", "exa", "baidu", "web", "爬虫", "搜索", "浏览器", "自动化"]),
    ("安全、审计与质量保障", ["security", "audit", "review", "test", "safe", "vet", "scanner", "antivirus", "安全", "审计", "扫描", "测试"]),
    ("文档、办公与内容生产", ["doc", "pdf", "word", "ppt", "xlsx", "markdown", "notion", "joplin", "email", "content", "writing", "文档", "写作", "邮件", "飞书", "腾讯文档", "办公"]),
    ("效率工具、个人工作流与其他", ["task", "calendar", "reminder", "habit", "todo", "workflow", "things", "apple", "weather", "map", "效率", "日历", "提醒", "天气"]),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def extract_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not match:
        return {}, text
    raw = match.group(1)
    rest = text[match.end() :]
    meta: dict[str, str] = {}
    for key in ("name", "description", "homepage"):
        m = re.search(rf"^{key}\s*:\s*(.+?)\s*$", raw, re.M)
        if m:
            value = m.group(1).strip().strip('"').strip("'")
            meta[key] = value
    return meta, rest


def first_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def compact(text: str, limit: int = 130) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    text = text.replace("|", "\\|")
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def category_for(name: str, description: str, rel: str) -> str:
    haystack = f"{name} {description} {rel}".lower()
    for category, keywords in CATEGORY_RULES:
        if any(k.lower() in haystack for k in keywords):
            return category
    return "效率工具、个人工作流与其他"


def skill_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    skill_paths = [p for p in SKILLS.rglob("*") if p.is_file() and p.name.lower() == "skill.md"]
    for skill_path in sorted(skill_paths, key=lambda p: str(p).lower()):
        rel = skill_path.relative_to(ROOT).as_posix()
        skill_dir = skill_path.parent
        text = read_text(skill_path)
        meta, body = extract_frontmatter(text)
        directory_name = skill_dir.name
        name = meta.get("name") or first_heading(body) or directory_name
        description = meta.get("description") or ""
        homepage = meta.get("homepage") or ""
        file_count = sum(1 for p in skill_dir.rglob("*") if p.is_file())
        category = category_for(name, description, rel)
        records.append(
            {
                "name": name,
                "directory": skill_dir.relative_to(SKILLS).as_posix(),
                "path": rel,
                "description": compact(description, 180),
                "homepage": homepage,
                "category": category,
                "file_count": str(file_count),
            }
        )
    return records


def md_table(records: list[dict[str, str]], include_category: bool = True) -> str:
    headers = ["Skill", "说明", "文件"]
    if include_category:
        headers.insert(2, "分类")
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for item in records:
        link = f"[`{item['directory']}`](../{item['path']})" if not include_category else f"[`{item['directory']}`]({item['path']})"
        row = [link, item["description"] or "暂无简述，保留原始 Skill 内容。"]
        if include_category:
            row.append(item["category"])
        row.append(item["file_count"])
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def category_file_name(category: str) -> str:
    mapping = {
        "编程语言与工程基础": "programming.md",
        "前端、移动端与交互体验": "frontend-mobile-ui.md",
        "后端、云平台与 API": "backend-cloud-api.md",
        "AI、Agent 与模型应用": "ai-agent-models.md",
        "数据、算法与科研": "data-algorithms-research.md",
        "浏览器、搜索与自动化": "browser-search-automation.md",
        "安全、审计与质量保障": "security-quality.md",
        "文档、办公与内容生产": "docs-office-content.md",
        "效率工具、个人工作流与其他": "workflow-others.md",
    }
    return mapping[category]


def write_readme(records: list[dict[str, str]]) -> None:
    total = len(records)
    total_files = sum(1 for _ in SKILLS.rglob("*") if _.is_file())
    total_size = sum(p.stat().st_size for p in SKILLS.rglob("*") if p.is_file())
    mb = total_size / 1024 / 1024
    counts = Counter(item["category"] for item in records)
    top = sorted(records, key=lambda x: (x["category"], x["directory"].lower()))[:18]

    category_rows = "\n".join(
        f"| [{cat}](docs/categories/{category_file_name(cat)}) | {counts[cat]} |"
        for cat, _ in CATEGORY_RULES
    )
    highlight_rows = "\n".join(
        f"| [`{item['directory']}`]({item['path']}) | {item['category']} | {item['description'] or '完整说明见 Skill 文件'} |"
        for item in top
    )

    content = f"""# 计算机专业 Skills 大合集

<p align="center">
  <img alt="Skills" src="https://img.shields.io/badge/Skills-{total}-2563eb">
  <img alt="Files" src="https://img.shields.io/badge/Files-{total_files}-16a34a">
  <img alt="Size" src="https://img.shields.io/badge/Package-{mb:.1f}MB-f97316">
  <img alt="For" src="https://img.shields.io/badge/For-Computer%20Science%20Students-7c3aed">
  <a href="https://github.com/bighardperson/computer-science-skills-collection/releases/latest"><img alt="Download" src="https://img.shields.io/badge/Download-Latest%20Release-0f766e"></a>
  <a href="https://github.com/bighardperson/computer-science-skills-collection/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/bighardperson/computer-science-skills-collection?style=social"></a>
</p>

这是一个面向计算机专业学生、开发者和 AI Agent 使用者的 Skills 大合集。它整理了本机 Claude Code / OpenClaw 风格的 skill 库，覆盖编程语言、前后端、移动端、云服务、AI Agent、浏览器自动化、数据分析、科研论文、文档办公、安全审计和效率工作流等方向。

这个仓库的目标不是把资料堆在一起，而是把可复用的能力沉淀成一套可以浏览、复制、二次开发的知识库：你可以把它当成技能提示词库、AI Agent 工作流模板库，也可以把它当成计算机专业实践方向的路线图。

## 一键下载

如果你只是想先把全部 skills 拉到本地，推荐直接下载 Release：

```bash
curl -L -o computer-science-skills-collection.zip \
  https://github.com/bighardperson/computer-science-skills-collection/releases/latest/download/computer-science-skills-collection.zip
```

如果你想持续同步更新，推荐 clone 仓库：

```bash
git clone https://github.com/bighardperson/computer-science-skills-collection.git
cd computer-science-skills-collection
```

想快速装到本机 skills 目录，可以运行：

```bash
bash scripts/install.sh ~/.agents/skills
```

## 为什么值得收藏

- **覆盖面广**：当前收录 {total} 个 skill 入口文件（`SKILL.md` / `skill.md`），从 Java、Android、前端、云开发到科研、爬虫、安全审计都有入口。
- **结构清楚**：所有 skill 保留原始目录，并额外生成总目录、分类索引和学习路线。
- **适合二次开发**：每个 skill 都尽量保持可迁移的 Markdown 结构，方便改造成自己的 Claude Code / Codex / OpenClaw 工作流。
- **面向实战**：很多 skill 不只是概念说明，还包含命令、脚本、检查清单、参考资料和使用场景。
- **适合展示**：仓库按作品集方式整理，方便别人快速看懂你的技术栈、工具链和自动化能力。

## 快速导航

| 入口 | 说明 |
| --- | --- |
| [完整目录 CATALOG](CATALOG.md) | 全部 skills 的索引表，适合检索和浏览 |
| [学习路线](docs/LEARNING_ROADMAP.md) | 按计算机专业成长路径组织的使用路线 |
| [使用指南](docs/USAGE.md) | 如何复制、改造、安装和维护这些 skills |
| [传播文案](docs/SHARE_COPY.md) | 发朋友圈、社群、README 推荐时可直接使用 |
| [贡献指南](CONTRIBUTING.md) | 如何补充、优化和提交新的 skill |
| [公开说明](LICENSE_NOTICE.md) | 关于公开整理、敏感信息排除和来源尊重的说明 |

## 分类地图

| 分类 | 数量 |
| --- | ---: |
{category_rows}

## 能力地图

```mermaid
mindmap
  root((计算机专业 Skills))
    编程语言与工程基础
      Java / Python / Rust / C++
      工程规范与代码审查
      测试与调试
    前端移动端
      Web / React / UI
      Android / iOS / Flutter
      小程序与交互设计
    后端云平台
      API Gateway / MCP
      CloudBase / Cloudflare
      Docker / DevOps
    AI Agent
      Prompt / Agent Team
      多模态生成
      模型接入与评测
    数据科研
      数据分析
      论文阅读
      金融与自动化研究
    自动化与安全
      浏览器自动化
      爬虫搜索
      安全审计
```

## 精选示例

| Skill | 分类 | 看点 |
| --- | --- | --- |
{highlight_rows}

## 推荐使用方式

1. 先看 [学习路线](docs/LEARNING_ROADMAP.md)，按自己的方向选择一条路线。
2. 再打开 [完整目录](CATALOG.md)，用浏览器搜索关键词，例如 `Android`、`Java`、`MCP`、`论文`、`安全`。
3. 找到对应 skill 后，进入 `skills/<skill-name>/SKILL.md` 或 `skill.md` 阅读触发规则、命令和参考资料。
4. 复制到自己的 Agent skill 目录，按项目实际路径、API 环境变量和工具链做最小改造。

## 仓库结构

```text
.
├── README.md                  # 项目首页与总览
├── CATALOG.md                 # 全量 skill 索引
├── docs/
│   ├── LEARNING_ROADMAP.md    # 计算机专业学习路线
│   ├── USAGE.md               # 使用与二次开发指南
│   └── categories/            # 按方向拆分的索引
├── scripts/
│   └── build_docs.py          # 自动生成目录文档
└── skills/                    # 原始 skills 内容
```

## 适合谁

- 想把 AI 编程工具用得更系统的计算机专业学生。
- 正在整理个人技术栈、作品集和自动化工作流的开发者。
- 想学习 Claude Code / Codex / OpenClaw skill 写法的人。
- 想快速搭建 Agent 工具库、提示词库或项目脚手架的人。

## 给 Star 的理由

如果你觉得这个仓库帮你节省了整理资料、写提示词、搭工作流的时间，欢迎点一个 Star。后续可以继续把它扩展成更完整的计算机专业技能地图：每个方向都有路线、示例、模板、工具链和实践项目。

## Star History

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=bighardperson/computer-science-skills-collection&type=Date&theme=dark">
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=bighardperson/computer-science-skills-collection&type=Date">
  </picture>
</p>
"""
    (ROOT / "README.md").write_text(content, encoding="utf-8")


def write_catalog(records: list[dict[str, str]]) -> None:
    content = "# CATALOG - 全量 Skills 索引\n\n"
    content += f"当前收录 `{len(records)}` 个 skill 入口文件（`SKILL.md` / `skill.md`）。表格按目录名排序，点击路径可以直接进入原始 skill 文件。\n\n"
    content += md_table(records, include_category=True) + "\n"
    (ROOT / "CATALOG.md").write_text(content, encoding="utf-8")


def write_categories(records: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in records:
        grouped[item["category"]].append(item)
    for category, _ in CATEGORY_RULES:
        items = sorted(grouped.get(category, []), key=lambda x: x["directory"].lower())
        lines = [f"# {category}", "", f"共 `{len(items)}` 个 skills。", "", md_table(items, include_category=False), ""]
        (CATEGORIES / category_file_name(category)).write_text("\n".join(lines), encoding="utf-8")


def write_roadmap(records: list[dict[str, str]]) -> None:
    content = """# 学习路线

这份路线不是课程表，而是把 skills 当成实践入口来使用。你可以按阶段挑选对应的 skill，边学边做小项目。

## 1. 编程基础与工程习惯

目标：能读懂项目结构、写出可维护代码、会用 Git 管理版本。

建议关注：

- Java / Python / Rust / C++ 等语言类 skills。
- coding、developer、clean-code、code-review、git-workflow 类 skills。
- 测试、调试、代码审计和项目文档类 skills。

## 2. 前端、移动端与用户界面

目标：能做出可运行、可展示、体验不错的界面项目。

建议关注：

- frontend、web-design、canvas-design、ui-ux 相关 skills。
- Android 原生开发、React Native、Flutter、iOS、微信小程序相关 skills。
- 图片、视频、音频、动画、PPT 等可视化表达 skills。

## 3. 后端、云平台与 API 能力

目标：能把项目从本地脚本扩展为可部署、可调用、可维护的服务。

建议关注：

- API Gateway、MCP、Docker、CloudBase、Cloudflare、腾讯云相关 skills。
- 数据库、对象存储、云函数、身份认证、支付和服务端工程相关 skills。
- 自动化部署、环境配置、日志排查和安全配置类 skills。

## 4. AI Agent 与模型应用

目标：不只是会问模型，而是能把模型接入稳定工作流。

建议关注：

- agent、llm、prompt、model、openai、gemini、claude 相关 skills。
- 浏览器自动化、搜索、文档读取、多模态生成、模型评测相关 skills。
- Agent Team、MCP 管理器、skill 创建与审计相关 skills。

## 5. 数据、科研与安全

目标：能完成数据分析、论文阅读、实验复现、安全审计和专业报告。

建议关注：

- academic、arxiv、research、paper、citation 相关 skills。
- data、excel、finance、stock、market 相关 skills。
- security、audit、scanner、review、test 相关 skills。

## 6. 个人工作流与作品集整理

目标：把学习成果沉淀成别人愿意 star、愿意复用的公开资产。

建议关注：

- document、markdown、pdf、word、ppt、content、writing 相关 skills。
- task、calendar、reminder、habit、goal、workflow 相关 skills。
- GitHub、README、项目展示、自动化整理相关 skills。

## 推荐实践项目

| 项目 | 可以组合的 skills |
| --- | --- |
| 个人主页 + 项目作品集 | GitHub、Markdown、frontend-design、document-summary |
| Android 课程项目展示 | android-native-dev、java、code-review、pdf-generator |
| 论文精读与复现仓库 | arxiv-reader、academic-research-hub、python、data-analyst |
| AI Agent 工具箱 | agent-team-orchestration、mcp、browser-use、web-scraper |
| 安全审计实验仓库 | security-auditor、java-audit-skill、clean-code-review |
"""
    (DOCS / "LEARNING_ROADMAP.md").write_text(content, encoding="utf-8")


def write_usage() -> None:
    content = """# 使用指南

## 复制一个 skill

找到你需要的目录后，复制整个 skill 文件夹到自己的 Agent skills 目录中：

```bash
cp -R skills/<skill-name> ~/.agents/skills/
```

不同客户端的目录可能不同。你可以只复制 `SKILL.md`，也可以把 `scripts/`、`references/`、`templates/` 一起复制。

## 改造成自己的版本

建议按这个顺序改：

1. 阅读 `SKILL.md` 的 `name`、`description` 和触发条件。
2. 检查是否依赖外部命令、API Key、浏览器、Node.js、Python 或云平台。
3. 把示例路径改成自己的项目路径。
4. 删除你暂时用不到的 references，保持 skill 轻量。
5. 为常用工作流补充自己的命令和成功案例。

## 公开前检查

如果你要继续公开自己的改版，建议至少检查：

- 不要提交真实 `.env`、Token、私钥、证书、Cookie、数据库文件。
- 不要提交个人聊天记录、会话缓存、浏览器配置、临时日志。
- 如果 skill 来自第三方项目，请保留来源说明并尊重原项目协议。
- 如果 skill 调用在线服务，请在 README 中说明需要哪些环境变量。

## 重新生成目录

修改 `skills/` 之后，可以运行：

```bash
python3 scripts/build_docs.py
```

它会重新生成：

- `README.md`
- `CATALOG.md`
- `docs/categories/*.md`
- `docs/manifest.json`
"""
    (DOCS / "USAGE.md").write_text(content, encoding="utf-8")


def write_notice() -> None:
    content = """# 公开说明

这个仓库是对本机 Claude Code / OpenClaw 风格 skills 的整理合集，主要用于学习、索引、复用和作品集展示。

公开前已做基础排除：

- 排除 `.env`、私钥、证书、数据库、日志等不适合公开的文件类型。
- 排除 `.git`、`node_modules`、`__pycache__`、`.DS_Store` 等缓存或本地生成物。
- 保留 skill 的原始目录结构，方便继续追溯和二次改造。

注意：

- 仓库中的部分 skill 可能来源于公开工具、插件或第三方模板。若某个目录内包含原始 license 或来源说明，请优先遵守原始说明。
- 如果你要商用、再分发或大规模改造，请自行确认对应 skill 的来源和许可边界。
- 本仓库更适合作为学习资料、个人工作流模板和 Agent 能力地图。
"""
    (ROOT / "LICENSE_NOTICE.md").write_text(content, encoding="utf-8")


def write_manifest(records: list[dict[str, str]]) -> None:
    payload = {
        "title": "计算机专业 Skills 大合集",
        "skill_count": len(records),
        "categories": Counter(item["category"] for item in records),
        "skills": records,
    }
    (DOCS / "manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    CATEGORIES.mkdir(parents=True, exist_ok=True)
    records = skill_records()
    write_readme(records)
    write_catalog(records)
    write_categories(records)
    write_roadmap(records)
    write_usage()
    write_notice()
    write_manifest(records)
    print(f"generated docs for {len(records)} skills")


if __name__ == "__main__":
    main()
