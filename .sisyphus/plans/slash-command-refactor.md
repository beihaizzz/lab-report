# /lab 命令系统重构

## TL;DR
> **改动**: SKILL.md YAML frontmatter + 新增 Commands 章节
> **影响**: 用户使用 `/lab init` 替代 `/lab-report init`，`/lab -work` 强制 Work Mode
> **不涉及脚本改动** — 纯文档层

---

## 实现任务

### T1. YAML frontmatter 更新

文件: `lab-report/SKILL.md`

旧 description:
```yaml
description: |
  Lab Report skill for university students. Helps complete lab experiments with two modes: 
  Guide Mode ... Triggers on: lab report, 实验报告, experiment report, /lab-report, ...
```

新 description:
```yaml
description: |
  Lab Report skill for university students. Helps complete lab experiments with two modes.
  Trigger: `/lab` command. Subcommands: `-init`, `-work`, `-guide`, `-update`, `-help`.
  Keywords: lab report, 实验报告, experiment report, /lab-report, /lab,
  实验指导, .docx template, .pdf guide, experiment writeup.
```

### T2. 新增 Commands 章节

在 "## Quick Start" 之后、"## Session Startup Protocol" 之前插入：

```markdown
## Commands

所有命令以 `/lab` 触发：

| 命令 | 作用 |
|------|------|
| `/lab -init` | 初始化项目。自动发现资料、创建 project.md、配置环境。`/lab -init --git` 启用版本管理 |
| `/lab -work` | 强制进入 Work Mode。直接生成实验报告 |
| `/lab -guide` | 强制进入 Guide Mode。开始指导实验 |
| `/lab -update` | 重新扫描项目目录。用于新增实验或大量文件变更后，刷新 project.md 和 .lab-report/config.json |
| `/lab -help` | 显示所有命令和简要说明 |
```

### T3. 更新现有引用

- `## /lab-report init` 改为 `## /lab -init`
- 全文搜索 `/lab-report` 替换为 `/lab`（如有）
- Quick Start 中 `Run /lab-report init` 改为 `Run /lab -init`

### T4. 更新 installed skill

同步到 `~/.claude/skills/lab-report/SKILL.md`

### commit 信息
```
重构：/lab 命令系统取代 /lab-report，新增 -init/-work/-guide/-update/-help 子命令
```
