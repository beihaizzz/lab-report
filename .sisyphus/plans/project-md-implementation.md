# project.md 实施方案

## TL;DR

> **改动**: init_project.py 增加 project.md 自动创建/更新逻辑 + SKILL.md 增加会话启动协议 + 文档更新
> **新增文件**: 无（project.md 由 init 时动态生成，不是静态模板）
> **净增代码**: ~70 行 + 文档

---

## 实现任务

- [x] ### T1. init_project.py 新增 project.md 检测/创建/更新

**文件**: `lab-report/scripts/init_project.py`

**新增函数** `_create_or_update_project_md(directory, experiment_name, course_info, student_info)`:

```python
PROJECT_MD_TEMPLATE = """# 课程信息

课程名称: {{课程名称}}
课程代码: {{课程代码}}
任课教师: {{任课教师}}

# 实验进度

- [x] {{实验名称}}
- [x] ...

# 通用配置

默认风格: normal
Git: 未启用

---

> 由 lab-report skill 自动维护。AI 每次会话启动时先读此文件了解项目状态。
"""

def _create_or_update_project_md(directory, experiment_name=None, 
                                  course_info=None, student_info=None):
    """在课程根目录创建或更新 project.md"""
    project_md = directory / "project.md"
    
    existing = {}
    if project_md.exists():
        for line in project_md.read_text(encoding='utf-8').split('\n'):
            if ':' in line and not line.startswith(('#', '-', '>')):
                k, v = line.split(':', 1)
                existing[k.strip()] = v.strip()
    
    if course_info:
        existing.update(course_info)
    
    # 构建内容 — 课程信息
    lines = ["# 课程信息\n"]
    for key in ["课程名称", "课程代码", "任课教师"]:
        lines.append(f"{key}: {existing.get(key, '{{%s}}' % key)}")
    
    # 实验进度（保留已有记录，追加新的）
    lines.append("\n# 实验进度\n")
    found = False
    for old_line in (project_md.read_text(encoding='utf-8').split('\n') 
                     if project_md.exists() else []):
        if old_line.startswith('- [') and '实验' in old_line:
            lines.append(old_line)
            found = True
    if experiment_name and experiment_name not in '\n'.join(lines):
        lines.append(f"- &#x20; {experiment_name}")
    elif not found:
        lines.append("- &#x20; ...")
    
    # 通用配置 + 脚注
    lines.append("\n# 通用配置\n")
    lines.append("默认风格: normal")
    lines.append("Git: 未启用")
    lines.append("\n---\n> 由 lab-report skill 自动维护。")
    
    project_md.write_text('\n'.join(lines), encoding='utf-8')
    return project_md
```

**在 init_project() 中调用**（放在 discover_files 之后）：

```python
# 3. 检测/创建 project.md
result["project_md"] = _create_or_update_project_md(
    directory,
    experiment_name=experiment_name
)
```

- [x] ### T2. SKILL.md 添加会话启动协议

**文件**: `lab-report/SKILL.md`

在 "Quick Start" 之后新增一节：

```markdown
## Session Startup Protocol

每次会话开始时（无论 Guide Mode 还是 Work Mode）：

1. **Read `project.md`** — 了解课程信息、实验进度、通用配置
2. **Read `学生信息.md`** — 获取个人信息
3. **Verify key paths** — `ls` 检查 project.md 引用的文件是否还存在
4. If paths stale → 告知用户并更新 project.md

project.md 是 session 的"快速上下文"——读它即可了解整个项目状态，无需重新扫描整个目录。
```

- [x] ### T3. 更新 workflow 文档

- [x] `references/guide-mode-workflow.md` — Step 0 改为 "Read project.md + 学生信息.md"
- [x] `references/work-mode-workflow.md` — Step 1.5 之前增加 "Read project.md for context"

- [x] ### T4. project.md 安全规则

在 AGENTS.md 和 workflow 文档中添加：

```
> ⚠️ project.md 不可包含：
> - 任何敏感信息（密码、token、API key）
> - 学生真实姓名（通过学生信息.md 引用，不复制）
> 仅存课程元信息和实验进度。
```

---

## commit 计划

所有改动一个 commit：
`新增：init 自动创建 project.md + 会话启动协议，减少重复上下文分析`
