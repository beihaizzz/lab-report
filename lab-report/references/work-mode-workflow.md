# Work Mode Workflow

Work Mode generates a completed lab report DOCX from a template and experiment data. It pulls student info, experiment progress, and student descriptions together, fills a template, and verifies the output.

---

## Overview

Work Mode is the second mode, activated after Guide Mode completes (or directly if the student already has experiment data). It produces a finished lab report by:

1. Collecting all available data sources
2. Parsing the template DOCX to discover placeholders
3. Building a complete data JSON
4. Rendering the template
5. Verifying no placeholders remain

---

## Step 1: Detect Existing Progress

Check for `.lab-report/progress.json`:

```bash
python scripts/progress_manager.py
```

### If progress exists

Extract experiment data from the progress file:

- `experiment_name` maps to `实验名称`
- `notes` contains step-by-step observations the student recorded
- `screenshots_required` lists captured screenshot paths
- `status` tells you if the experiment is complete

Combine this with student info (Step 2) and any additional description the student provides.

### If no progress exists

Ask the student to describe the experiment in natural language:

```
没有找到实验进度记录。请描述你的实验：
- 实验名称是什么？
- 实验目的和原理是什么？
- 你做了哪些步骤？
- 观察到了什么数据？
```

Collect the student's response and use it as the primary data source. You can still initialize progress retroactively if the student wants to track things.

---

## Step 2: Collect Student Info

Run the student info discovery script:

```bash
python scripts/student_info.py --json
```

This searches for `学生信息.md` in the current directory and up to 3 parent directories.

### If found

The script returns a JSON object with `姓名`, `学号`, `学院`, `专业`, `班级`. Use these values directly in the template data.

### If not found

Create the template file:

```bash
python scripts/student_info.py --create
```

Then ask the student to fill in their information in the created `学生信息.md` file. The file format is:

```markdown
# 学生信息

姓名: 张三
学号: 2024001
学院: 物理学院
专业: 应用物理
班级: 物理2401
```

---

## Step 3: Parse the Template DOCX

Identify the template file (usually a `.docx` in the project directory or provided by the student), then parse it:

```bash
python scripts/parse_docx.py --input path/to/template.docx
```

This returns a JSON structure containing:

- `paragraphs`: All text paragraphs with their styles
- `tables`: All table data as nested arrays
- `placeholders`: List of all `{{placeholder}}` patterns found in the document
- `structure`: Counts of paragraphs, tables, and headings

### Placeholder Discovery

The parser uses the regex `\{\{([^}]+)\}\}` to find Jinja2-style placeholders in both paragraphs and table cells. The returned `placeholders` list is your data contract: every item in this list must have a corresponding value in the template data JSON.

---

## Step 4: Map Placeholders to Data Sources

Each placeholder maps to one of three data sources:

| Source | Fields | How to obtain |
|--------|--------|---------------|
| Student info | 姓名, 学号, 学院, 专业, 班级 | `scripts/student_info.py` |
| Experiment progress | 实验名称, 实验步骤, 实验数据 | `.lab-report/progress.json` |
| Student description | 实验目的, 实验原理, 实验器材, 实验结果, 实验结论 | Ask the student or infer from guide content |

### Mapping Table

| Placeholder | Primary source | Fallback |
|-------------|---------------|----------|
| `{{姓名}}` | student_info | Ask student |
| `{{学号}}` | student_info | Ask student |
| `{{学院}}` | student_info | Ask student |
| `{{专业}}` | student_info | Ask student |
| `{{班级}}` | student_info | Ask student |
| `{{课程名}}` | Ask student | From guide title |
| `{{实验名称}}` | progress.experiment_name | Ask student |
| `{{实验日期}}` | Ask student | Today's date |
| `{{实验地点}}` | Ask student | From guide |
| `{{实验目的}}` | Parsed guide content | Ask student |
| `{{实验原理}}` | Parsed guide content | Ask student |
| `{{实验器材}}` | Parsed guide content | Ask student |
| `{{实验步骤}}` | progress.notes + completed steps | Ask student |
| `{{实验数据}}` | progress.notes + screenshots | Ask student |
| `{{实验结果}}` | Ask student | Infer from data |
| `{{实验结论}}` | Ask student | Infer from results |

### Missing Data Handling

If a placeholder has no data source and the student cannot provide it:

- Use `"暂无"` as the value (not an empty string, which would break table layouts)
- Flag the placeholder as incomplete in the output summary

---

## Step 5: Build Template Data JSON

Create a JSON file (e.g., `.lab-report/template-data.json`) with all required fields:

```json
{
  "姓名": "张三",
  "学号": "2024001",
  "学院": "物理学院",
  "专业": "应用物理",
  "班级": "物理2401",
  "课程名": "大学物理实验",
  "实验名称": "电阻的测量",
  "实验日期": "2025-04-24",
  "实验地点": "物理实验楼301",
  "实验目的": "掌握伏安法测电阻的原理和方法...",
  "实验原理": "根据欧姆定律 R = U/I...",
  "实验器材": "直流稳压电源、电压表、电流表、电阻箱...",
  "实验步骤": "1. 按电路图连接电路\n2. 调节电源电压至3V\n...",
  "实验数据": "电压/V: 3.0, 电流/mA: 15.2...",
  "实验结果": "测得电阻值为 197.4Ω...",
  "实验结论": "伏安法测电阻结果与标称值接近..."
}
```

### Content Quality Guidelines

When generating content for placeholders from student descriptions or guide content:

- Write in **first person plural** (我们) for experiment steps and observations
- Use **past tense** for completed actions (连接了, 测量了)
- Keep data sections factual and numerical
- Conclusions should reference specific data points
- Avoid banned AI phrases (see `fill_template.py` BANNED_WORDS): 首先, 其次, 最后, 总而言之, 值得注意的是, 综上所述, 不可否认

---

## Step 6: Fill the Template

Run the template filling script:

```bash
python scripts/fill_template.py \
  --template path/to/template.docx \
  --data .lab-report/template-data.json \
  --output output/实验报告.docx \
  --style perfect
```

### Style Options

| Style | Behavior |
|-------|----------|
| `normal` | Standard fill. Content may have minor AI patterns. |
| `perfect` | Applies de-AI style checks. Warns on banned words. Use for final submissions. |

Both styles apply CJK font fixes (宋体 for body text, 黑体 for headings) via the `w:eastAsia` attribute.

### What the Script Does

1. Copies the template to the output path (never modifies the original)
2. Renders all `{{placeholder}}` fields using Jinja2 via `docxtpl`
3. Verifies CJK fonts on all runs containing Chinese characters
4. Checks for unreplaced placeholders in the output
5. Returns a JSON result with `success`, `placeholders_filled`, and `placeholders_missing`

---

## Step 7: Verify Output

After filling, check the result JSON for:

### Unreplaced Placeholders

If `placeholders_missing` is non-empty, the template has unfilled fields. For each missing placeholder:

1. Check if the data JSON has the corresponding key
2. If the key exists but is empty, the value was likely blank
3. If the key is missing, add it to the data JSON and re-run

### CJK Font Verification

The script automatically sets CJK fonts, but verify manually if the output looks wrong:

- Body text should use 宋体 (SimSun)
- Headings should use 黑体 (SimHei)
- The `w:eastAsia` attribute on `w:rFonts` ensures CJK characters render correctly

---

## Step 8: Auto-Commit (Optional)

If git tracking is enabled, commit the output:

```bash
python scripts/git_manager.py --message "生成实验报告: 实验名称"
```

Or with a dry run first:

```bash
python scripts/git_manager.py --dry-run
```

The script stages all changes and commits. It silently exits if the directory is not a git repo.

---

## Complete Workflow Diagram

```
[Start Work Mode]
       │
       ▼
  Progress exists? ──No──► Ask student to describe experiment
       │                         │
      Yes                        │
       │                         │
       ▼                         ▼
  Read progress.json        Collect description
       │                         │
       └─────────┬───────────────┘
                 │
                 ▼
        Collect student info
        (student_info.py)
                 │
                 ▼
        Parse template DOCX
        (parse_docx.py)
                 │
                 ▼
        Map placeholders → data sources
                 │
                 ▼
        Build template-data.json
                 │
                 ▼
        Fill template
        (fill_template.py --style perfect)
                 │
                 ▼
        Verify: no unreplaced placeholders?
           │              │
          Yes             No ──► Fix data, re-fill
           │
           ▼
        Auto-commit (optional)
        (git_manager.py)
                 │
                 ▼
           [Done]
```

---

## Error Handling

| Situation | Response |
|-----------|----------|
| No template DOCX found | Ask student to provide one; list available `.docx` files in the directory |
| Template has no placeholders | The template may use a different syntax; ask student to confirm |
| Data JSON missing keys | Prompt student for missing values; use "暂无" as fallback |
| `fill_template.py` fails | Check error message; common causes: missing dependency, corrupted template |
| Unreplaced placeholders remain | Identify which ones, ask student for values, rebuild data JSON |
| CJK characters display as tofu | Re-run fill; the script applies CJK fonts automatically |
| Student info file not found | Create template with `student_info.py --create`, ask student to fill it in |

---

## Quick Reference: CLI Commands

```bash
# Check for existing progress
python scripts/progress_manager.py

# Get student info
python scripts/student_info.py --json

# Create student info template
python scripts/student_info.py --create

# Parse template DOCX
python scripts/parse_docx.py --input template.docx

# Fill template (normal style)
python scripts/fill_template.py -t template.docx -d data.json -o output.docx --style normal

# Fill template (perfect style, de-AI)
python scripts/fill_template.py -t template.docx -d data.json -o output.docx --style perfect

# Auto-commit output
python scripts/git_manager.py --message "生成实验报告"

# Dry-run commit
python scripts/git_manager.py --dry-run
```