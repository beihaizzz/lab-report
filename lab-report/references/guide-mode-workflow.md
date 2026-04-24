# Guide Mode Workflow

Guide Mode walks a student through an experiment step by step, tracking progress and prompting screenshots at the right moments.

---

## Overview

Guide Mode is the first of two modes. It parses an experiment guide (PDF or PPTX), extracts discrete steps, identifies which steps need screenshots, and presents the full workflow to the student. The student works through steps at their own pace, saying "继续" to advance.

---

## Step 1: Parse the Experiment Guide

### Input Sources

The experiment guide can arrive as:

- A **PDF** file, parsed by `scripts/parse_pdf.py`
- A **PPTX** file, parsed by `scripts/parse_pptx.py`

### Parsing PDF

```bash
python scripts/parse_pdf.py --input path/to/guide.pdf --format json
```

Returns a JSON structure with `text_by_page` and `markdown` fields. If `is_scanned` is `true`, warn the student that OCR quality may be low and ask them to describe unclear steps.

### Parsing PPTX

```bash
python scripts/parse_pptx.py --input path/to/guide.pptx --format json
```

Returns a JSON structure with `slides`, each containing `title` and `content` arrays.

### Step Extraction Heuristics

After parsing, extract steps from the raw text using these patterns:

1. **Numbered lists**: Lines starting with `1.`, `2.`, `3.` or `（1）`, `（2）`, `（3）`
2. **Imperative sentences**: Lines containing verbs like 连接, 测量, 观察, 记录, 调节, 设置, 安装, 拍摄
3. **Procedure sections**: Content under headings like 实验步骤, 操作步骤, 实验过程
4. **Sequential instructions**: Sentences joined by 然后, 接着, 之后

Group extracted steps into a numbered list. Each step should be a single actionable instruction, not a paragraph.

---

## Step 2: Identify Screenshot-Worthy Steps

Scan each extracted step for these keywords:

| Keyword | Reason |
|---------|--------|
| 测量 | Measurement readings need visual proof |
| 连接 | Circuit or apparatus setup must be documented |
| 观察 | Observable phenomena should be captured |
| 记录 | Recorded data often comes from instrument displays |
| 拍摄 | Explicit instruction to take a photo |

Mark any step containing these keywords as `screenshot_required: true` in the progress data.

---

## Step 3: Initialize Progress Tracking

Use `scripts/progress_manager.py` to create the progress file:

```bash
python scripts/progress_manager.py --init --experiment "实验名称" --total-steps N
```

This creates `.lab-report/progress.json` with the structure defined in `schemas.md`.

For each screenshot-worthy step, register it:

```bash
python scripts/progress_manager.py --screenshot --step 3 --description "测量电压表读数"
```

---

## Step 4: Present All Steps to the Student

Display the full step list at once in a clear format:

```
📋 实验名称: 电阻的测量
共 6 个步骤:

1. 连接电路（📸 需要截图）
2. 调节电源电压至 3V
3. 测量并记录电压表读数（📸 需要截图）
4. 测量并记录电流表读数（📸 需要截图）
5. 断开电路，更换电阻
6. 观察并记录实验现象（📸 需要截图）

说"继续"开始第一步，或询问任何步骤的详细说明。
```

### Presentation Rules

- Show **all steps at once**, not one at a time
- Mark screenshot steps with 📸
- Tell the student they can ask about any specific step at any time
- Include the total step count so the student knows the scope

---

## Step 5: Progress Sync Protocol

The student drives progress. The AI responds to these triggers:

### Student says "继续"

1. Read current progress: `python scripts/progress_manager.py`
2. Determine the next incomplete step (smallest step number not in `completed_steps`)
3. Mark it as `in_progress`:
   ```bash
   python scripts/progress_manager.py --step N --status in_progress
   ```
4. Present the step with any relevant tips
5. If the step requires a screenshot, remind the student (see Step 6)

### Student says a step is done

1. Mark the step as `completed`:
   ```bash
   python scripts/progress_manager.py --step N --status completed
   ```
2. If the step had a screenshot requirement, ask if they captured it
3. Show remaining steps count

### Student asks about a specific step

1. Look up the step in the parsed guide content
2. Provide detailed explanation, tips, and common mistakes
3. Do **not** advance the progress counter
4. Remind about screenshots if applicable

### Student says "跳过" (skip)

1. Mark the step as `skipped`:
   ```bash
   python scripts/progress_manager.py --step N --status skipped
   ```
2. Note the skip in progress notes:
   ```bash
   python scripts/progress_manager.py --step N --note "学生跳过了此步骤"
   ```

---

## Step 6: Screenshot Reminders

### When to Remind

- **Before** a screenshot-worthy step begins (not after)
- Format: `📸 提醒: 这一步需要拍照记录 [description]`

### After the Step

- If the step was screenshot-worthy and the student marks it complete, ask:
  `这一步的截图拍好了吗？如果拍了，可以告诉我截图的文件名。`

### Recording Screenshots

When the student provides a screenshot path:

```bash
python scripts/progress_manager.py --screenshot --step N --path "screenshots/step_N.jpg"
```

This sets `captured: true` in the progress data.

---

## Step 7: Completion

When all steps are done (`status` becomes `completed`):

1. Summarize what was accomplished
2. List any skipped steps
3. List any missing screenshots
4. Suggest transitioning to **Work Mode** to generate the lab report

```
✅ 实验完成！

完成步骤: 5/6
跳过步骤: 1 (步骤2)
缺失截图: 1 (步骤4)

建议: 现在可以切换到 Work Mode 生成实验报告了。
```

---

## Error Handling

| Situation | Response |
|-----------|----------|
| PDF is scanned | Warn student, ask them to describe unclear parts |
| No steps detected | Ask student to describe the experiment procedure in their own words |
| Progress file corrupted | Re-initialize with `--reset` and ask student to confirm step count |
| Student provides wrong step number | List current steps and ask them to clarify |
| Student asks about a step not in the guide | Use the parsed content to provide context; if unavailable, say so honestly |

---

## Quick Reference: CLI Commands

```bash
# Initialize progress
python scripts/progress_manager.py --init --experiment "名称" --total-steps N

# Check current progress
python scripts/progress_manager.py

# Mark step in progress
python scripts/progress_manager.py --step N --status in_progress

# Mark step completed
python scripts/progress_manager.py --step N --status completed

# Skip a step
python scripts/progress_manager.py --step N --status skipped

# Add screenshot requirement
python scripts/progress_manager.py --screenshot --step N --description "描述"

# Record screenshot path
python scripts/progress_manager.py --screenshot --step N --path "path/to/file.jpg"

# Add a note
python scripts/progress_manager.py --step N --note "备注内容"

# Reset progress
python scripts/progress_manager.py --reset --experiment "名称" --total-steps N
```