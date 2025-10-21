# MyES PowerPoint Generator - Web App

**Version 2.0** | English Presentation Generator | © 2025 MyES - My English School

A web-based tool for creating professional educational presentations with ease. Works on **any device** - Windows, Mac, Linux, iPad - just needs a web browser!

---

## 🚀 Quick Start

### Access the App
Visit: **[Your Streamlit URL here]**

### How to Use
1. **Open** the web app in your browser
2. **Write or upload** your lesson content using the syntax below
3. **Validate** to check for errors
4. **Generate PowerPoint** - creates your presentation
5. **Download** the .pptx file and teach!

### No Installation Required
✅ Works on Mac, Windows, Linux, tablets  
✅ No Python needed  
✅ No downloads or setup  
✅ Just open your browser and create!

---

## 📖 Table of Contents

1. [Basic Syntax](#basic-syntax)
2. [Layout Types](#layout-types)
3. [Style Tags & Formatting](#style-tags--formatting)
4. [Advanced Features](#advanced-features)
5. [AI Content Creation Guide](#ai-content-creation-guide)
6. [Tips for Educational Content](#tips-for-educational-content)
7. [Troubleshooting](#troubleshooting)

---

## 📝 Basic Syntax

### Slide Structure
Every slide must have:
- `Slide 1` - Slide number (for reference)
- `Title: [text]` - The slide title (required)
- Content sections (see layouts below)
- `---` - Optional slide separator

### Example

You're right - let me provide it directly here so you can copy it:
Copy this entire text and save as README.md:
markdown# MyES PowerPoint Generator - Web App

**Version 2.0** | Business English for Technical Architects | © 2025 MyES - My English School

A web-based tool for creating professional educational presentations with ease. Works on **any device** - Windows, Mac, Linux, iPad - just needs a web browser!

---

## 🚀 Quick Start

### Access the App
Visit: **[Your Streamlit URL here]**

### How to Use
1. **Open** the web app in your browser
2. **Write or upload** your lesson content using the syntax below
3. **Validate** to check for errors
4. **Generate PowerPoint** - creates your presentation
5. **Download** the .pptx file and teach!

### No Installation Required
✅ Works on Mac, Windows, Linux, tablets  
✅ No Python needed  
✅ No downloads or setup  
✅ Just open your browser and create!

---

## 📖 Table of Contents

1. [Basic Syntax](#basic-syntax)
2. [Layout Types](#layout-types)
3. [Style Tags & Formatting](#style-tags--formatting)
4. [Advanced Features](#advanced-features)
5. [AI Content Creation Guide](#ai-content-creation-guide)
6. [Tips for Educational Content](#tips-for-educational-content)
7. [Troubleshooting](#troubleshooting)

---

## 📝 Basic Syntax

### Slide Structure
Every slide must have:
- `Slide 1` - Slide number (for reference)
- `Title: [text]` - The slide title (required)
- Content sections (see layouts below)
- `---` - Optional slide separator

### Example
```
Slide 1
Title: Welcome to Business English
Content: Today we will learn professional vocabulary
Content: [step] Key terms and definitions
Content: [step] Practice exercises
Notes: Ask students about their experience with formal emails
---
```

### Content Sections
- `Content:` - Single column content (default)
- `Left:` / `Right:` - Two-column layout
- `LeftTop:` / `RightTop:` - Four-box layout (top)
- `LeftBottom:` / `RightBottom:` - Four-box layout (bottom)
- `Notes:` - Presenter notes (not visible on slide)
- `# comment` - Lines starting with # are ignored

---

## 🎨 Layout Types

### 1. Single Column (Default)
```
Slide 1
Title: Introduction
Content: Main point here
Content: Another point
Content: Third point
```
**Result:** One centered content area

### 2. Two Columns
```
Slide 2
Title: Comparison Layout
Left: Point A
Left: Point B
Right: Corresponding point 1
Right: Corresponding point 2
```
**Result:** Side-by-side columns (great for comparisons, vocabulary)

### 3. Four Boxes (2x2 Grid)
```
Slide 3
Title: Project Phases
LeftTop: Planning Phase
LeftTop: • Define scope
RightTop: Execution Phase
RightTop: • Implement solutions
LeftBottom: Testing Phase
LeftBottom: • Validate results
RightBottom: Closure Phase
RightBottom: • Complete docs
```
**Result:** Four equal boxes in a grid

### 4. Reading Comprehension (Stacked)
```
Slide 4
Title: Case Study
LeftTop: Your reading passage goes here (150-250 words)...
LeftBottom: 1. What did the team do first?
LeftBottom: 2. When did they complete the migration?
LeftBottom: 3. What benefits did the project deliver?
```
**Result:** Large text area on top (65%), questions below (35%)  
**Note:** Questions with numbers are automatically separated

---

## 🏷️ Style Tags & Formatting

### Inline Style Tags
Use these to add visual emphasis and color:

- `[vocabulary]` - **Green, bold** (24pt) - for new terms
- `[question]` - **Purple** (20pt) - for discussion questions
- `[answer]` - **Gray, italic** (18pt) - for model answers
- `[emphasis]` - **Red, bold** (22pt) - for important points
- `[step]` - Creates separate shapes for animations

### Usage Examples
```
Content: [vocabulary] resilience - the ability to recover from failures
Content: [question] What is your current role?
Content: [answer] I work as a Technical Architect at IBM
Content: [emphasis] Remember: Always back up before migration!
Content: [step] First, assess the environment
Content: [step] Then, design the solution
```

### Automatic Formatting
✅ Bullet points (•, -, *) are auto-detected  
✅ Numbered lists (1. 2. 3.) are auto-detected  
✅ Long text (>300 chars) automatically reduces font size  
✅ Questions ending with "?" can be auto-split

---

## ⚡ Advanced Features

### Templates
Use predefined layouts for common slide types:
```
Slide 5
Title: New Vocabulary
Template: vocabulary
Left: [vocabulary] milestone
Right: A key stage or goal in a project schedule
```

Available templates:
- `Template: vocabulary` - Auto two-column vocabulary layout
- `Template: reading` - Reading comprehension format
- `Template: comparison` - Before/after comparison

### Images
```
Image: diagram.png | width=5 | align=center
Image: photo.jpg | width=4 | left=2 | top=3
```

**Parameters:**
- `width=X` - Width in inches (default 4)
- `align=center|left|right` - Alignment
- `left=X` - Specific horizontal position
- `top=X` - Specific vertical position

### Math & Special Characters
```
x^2         → x² (superscript)
H_2O        → H₂O (subscript)
>=          → ≥
<=          → ≤
!=          → ≠
~=          → ≈
pi          → π
alpha, beta, theta → α, β, θ
```

---

## 🤖 AI Content Creation Guide

### Essential Rules
1. Every slide MUST start with `Slide X`
2. Every slide MUST have `Title: [text]`
3. Content in sections: `Content:`, `Left:`, `Right:`, etc.
4. Use `---` to separate slides (recommended)
5. Multiple lines under same section are allowed

### Layout Selection Logic
- **Simple slides** → Use `Content:`
- **Comparisons/vocabulary** → Use `Left:` and `Right:`
- **Complex topics (4 aspects)** → Use `LeftTop:`, `RightTop:`, `LeftBottom:`, `RightBottom:`
- **Reading + questions** → Use `LeftTop:` for passage, `LeftBottom:` for questions

### Content Length Guidelines
- **Slide titles:** Max 60 characters
- **Single column:** Up to 500 characters per slide
- **Two columns:** Up to 300 characters per column
- **Four boxes:** Up to 150 characters per box
- **Reading passages:** Up to 1000 characters
- **Questions:** 3-5 questions per slide maximum

### Recommended Lesson Structure
```
Slide 1: Title & Objectives (with [step] animations)
Slide 2: Lead-in Discussion (with [question] tags)
Slide 3: Reading Passage + Questions (LeftTop/LeftBottom layout)
Slide 4: Vocabulary (Template: vocabulary)
Slide 5: Grammar Explanation (4-box layout with examples)
Slide 6: Practice Exercise (with [step] instructions)
Slide 7: Speaking Activity (with prompts)
Slide 8: Recap & Reflection (with [question] tags)
```

---

## 💡 Tips for Educational Content

### Font Sizing (Automatic)
- **Default:** 22pt (good for most content)
- **300-500 chars:** Auto-reduces to 18pt
- **500-700 chars:** Auto-reduces to 16pt
- **700+ chars:** Auto-reduces to 14pt

### Content Per Slide
- Aim for **5-7 bullet points** maximum per slide
- Each bullet: **1-2 lines** of text
- Reading passages: **150-250 words** ideal
- Questions: **3-4 per slide** maximum
- Vocabulary: **4-6 items** per slide

### Color Coding (Automatic)
- **Titles:** Red (#C00000)
- **Body text:** Blue (#000066)
- **[vocabulary]:** Green - for new terms
- **[question]:** Purple - for questions
- **[answer]:** Gray - for model answers
- **[emphasis]:** Red - for key points

---

## 🐛 Troubleshooting

### Common Issues

**"Missing title" error**  
→ Every slide needs `Title: [text]` line

**Text overlapping or cut off**  
→ Reduce content length, split into multiple slides

**Questions not splitting**  
→ Format as: `1. Question? 2. Question?`

**Can't generate presentation**  
→ Check validation first, ensure all required sections present

### Best Practices
1. ✅ Always **validate** before generating
2. ✅ Keep titles **under 60 characters**
3. ✅ Aim for **300-500 characters** per content section
4. ✅ Use `[step]` **sparingly** (max 7 per slide)
5. ✅ Use **descriptive filenames**

---

## 🛠️ For Developers

### Running Locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Requirements
- Python 3.8+
- streamlit>=1.28.0
- python-pptx>=0.6.21
- Pillow>=10.0.0

---

## 📜 License

MIT License - Free to use and adapt for educational purposes.

---

**Version 2.0** | Last Updated: 2025  
Made with ❤️ for English teachers everywhere# myes-generator
