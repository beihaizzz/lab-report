# lab-report

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**OpenCode Skill** — 帮助大学生完成实验报告。两种模式：指导你做实验，或者帮你写报告。

## 两种模式

| 模式 | 做什么 | 适合场景 |
|------|--------|----------|
| **Guide Mode（指导模式）** | 读取实验指导书，展示所有步骤和注意事项，同步进度，提醒截图 | 第一次做实验，需要一步步引导 |
| **Work Mode（工作模式）** | 读取报告模板，根据实验过程填入内容，生成 Word 文件 | 已经做完实验，需要生成报告 |

两种模式输出的报告均默认融入**去 AI 味**风格 —— 自然段落、真人语调、无 AI 特征词。

## 快速开始

```bash
# 1. 创建课程实验文件夹
mkdir 大学物理实验一
cd 大学物理实验一

# 2. 放入资料（实验指导书 PDF/Word/PPT、报告模板 Word）
# 3. 打开 OpenCode，运行初始化
/lab-report init
```

初始化后会自动发现课程资料、找到或创建 `学生信息.md`，然后你可以进入指导或工作模式。

## 使用方法

### 初始化
```
/lab-report init
```
自动发现当前目录下的实验指导书（PDF/DOCX/PPTX）、报告模板（DOCX）、参考材料。信息不足会主动询问。

### 复用学生信息
`学生信息.md` 可跨课程复用 —— 写完一次，复制到其他课程文件夹即可：
```markdown
# 学生信息

姓名: 张三
学号: 20240001
学院: 电子信息学院
专业: 电子信息工程
班级: 电子2101班
```

### 可选：Git 版本管理
```
/lab-report init --git
```
每次 AI 修改文件后自动 git commit，记录所有改动历史。

## 报告模板

你的 Word 模板中需要填写的字段用 `{{字段名}}` 标记。例如：

```
| 姓名 | {{姓名}} | 学号 | {{学号}} |
| 实验名称 | {{实验名称}} | 日期 | {{实验日期}} |
```

支持的字段：`{{姓名}}` `{{学号}}` `{{学院}}` `{{专业}}` `{{班级}}` `{{课程名}}` `{{实验名称}}` `{{实验日期}}` `{{实验地点}}` `{{实验目的}}` `{{实验原理}}` `{{实验器材}}` `{{实验步骤}}` `{{实验数据}}` `{{实验结果}}` `{{实验结论}}`

没有模板也无妨 —— skill 自带默认模板，初始化时可选择使用。

## 报告风格

| 风格 | 效果 |
|------|------|
| **perfect** | 完整填充，专业表述 |
| **normal** | 标准填充，自然叙述 |

两种风格均默认融入去 AI 味（无"首先其次最后"、自然段落叙述、不分条目）。

## 项目结构

```
lab-report/
├── SKILL.md              # 主 Skill 定义
├── scripts/              # Python 脚本
│   ├── init_project.py    # 项目初始化
│   ├── parse_pdf.py       # PDF 文本提取 + 扫描件检测
│   ├── parse_docx.py      # DOCX 解析 + 占位符检测
│   ├── parse_pptx.py      # PPT 文本提取
│   ├── fill_template.py   # docxtpl 模板填空 + CJK 字体
│   ├── progress_manager.py# JSON 进度管理
│   ├── student_info.py    # 学生信息发现/创建
│   ├── git_manager.py     # Git 自动提交
│   └── check_deps.py      # 依赖预检
├── references/           # 参考文档
│   ├── guide-mode-workflow.md
│   ├── work-mode-workflow.md
│   ├── template-patterns.md
│   ├── de-ai-style-guide.md
│   └── report-structure.md
├── assets/               # 资产文件
│   ├── 学生信息模板.md
│   └── report_template.docx
└── tests/                # 测试套件 (27 tests)
```

## 技术栈

- **运行时**: Python 3.10+, [uv](https://github.com/astral-sh/uv) 包管理
- **文档解析**: pdfplumber, python-docx, python-pptx, pymupdf4llm
- **模板引擎**: [docxtpl](https://github.com/elapouya/python-docx-template) (Jinja2)
- **CJK 字体**: 自动设置 `w:eastAsia` 属性，中文不会显示为方框
- **安全**: 所有操作在模板副本上进行，永远不会修改原始文件

## 安装

这是一个 OpenCode Skill，无需单独安装。将 `lab-report/` 目录放入以下任一位置即可：

- 项目级：`<your-project>/.opencode/skills/lab-report/`
- 用户级：`~/.config/opencode/skills/lab-report/`

## 许可

MIT License

---

如果模板中无占位符或格式特殊，AI 会主动询问你如何映射。原始文件永远不会被修改 —— AI 总是在副本上操作。
