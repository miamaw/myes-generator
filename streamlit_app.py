"""
Universal PowerPoint Generator - Web App
=========================================
Fully customizable presentation generator for educators
"""

import streamlit as st
import os
import io
import re
from pathlib import Path

# Import the universal generator
try:
    from generate_presentation_universal import (
        merge_config, parse_content_file, build_presentation,
        validate_slide, DEFAULT_CONFIG
    )
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    st.error("⚠️ Generator module not found.")

# Page configuration
st.set_page_config(
    page_title="Universal PowerPoint Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-weight: bold;
    }
    .stButton>button {
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


def rgb_to_hex(rgb):
    """Convert RGB list to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def hex_to_rgb(hex_color):
    """Convert hex color to RGB list"""
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]


def get_quick_reference():
    """Return quick reference text"""
    return """QUICK REFERENCE
===============

Slide Structure:
  Slide #
  Title: ...
  Content: ...
  ---

Layouts:
  • Content: single column
  • Left:/Right: two columns  
  • LeftTop/RightTop/
    LeftBottom/RightBottom: 4-box

Special Tags:
  [step] - animations
  [vocabulary] - custom style
  [question] - custom style
  [answer] - custom style
  [emphasis] - custom style
"""


def get_sample_template():
    """Return sample lesson template"""
    return """# Sample Lesson Template

Slide 1
Title: Lesson Title Here
Content: [emphasis] Main Topic
Content: 
Content: Today's Focus:
Content: [step] Learning objective 1
Content: [step] Learning objective 2
Content: [step] Learning objective 3
Notes: Introduction and warm-up. 5 minutes.

---

Slide 2
Title: Discussion Question
Content: [question] What is your experience with this topic?
Content: 
Content: Think about:
Content: • Point to consider 1
Content: • Point to consider 2
Content: • Point to consider 3
Notes: Pair discussion 3 minutes.

---

Slide 3
Title: Key Vocabulary
Left: [vocabulary] term one
Right: Definition of first term
Left: [vocabulary] term two
Right: Definition of second term
Notes: Drill pronunciation.

---
"""


# ============================================================================
# PREVIEW FUNCTIONS
# ============================================================================

def parse_slides_for_preview(content):
    """Parse content and return structured slide data for preview"""
    slides = []
    current_slide = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if line.startswith('#') or not line:
            continue
        
        # New slide
        if line.lower().startswith('slide '):
            if current_slide:
                slides.append(current_slide)
            current_slide = {
                'number': line,
                'title': '',
                'content': [],
                'left': [],
                'right': [],
                'lefttop': [],
                'righttop': [],
                'leftbottom': [],
                'rightbottom': [],
                'notes': []
            }
        
        # Separator
        elif line == '---':
            if current_slide:
                slides.append(current_slide)
                current_slide = None
        
        # Slide properties
        elif current_slide:
            if line.lower().startswith('title:'):
                current_slide['title'] = line[6:].strip()
            elif line.lower().startswith('content:'):
                current_slide['content'].append(line[8:].strip())
            elif line.lower().startswith('left:'):
                current_slide['left'].append(line[5:].strip())
            elif line.lower().startswith('right:'):
                current_slide['right'].append(line[6:].strip())
            elif line.lower().startswith('lefttop:'):
                current_slide['lefttop'].append(line[8:].strip())
            elif line.lower().startswith('righttop:'):
                current_slide['righttop'].append(line[9:].strip())
            elif line.lower().startswith('leftbottom:'):
                current_slide['leftbottom'].append(line[11:].strip())
            elif line.lower().startswith('rightbottom:'):
                current_slide['rightbottom'].append(line[12:].strip())
            elif line.lower().startswith('notes:'):
                current_slide['notes'].append(line[6:].strip())
    
    # Add last slide
    if current_slide:
        slides.append(current_slide)
    
    return slides


def format_text_with_tags(text):
    """Format text with style tags for preview"""
    # Remove [step] tags for preview
    text = re.sub(r'\[step\]\s*', '', text)
    
    # Apply styling
    if '[vocabulary]' in text:
        text = text.replace('[vocabulary]', '')
        return f'<span style="color: #2E7D32; font-weight: bold;">🔹 {text}</span>'
    elif '[question]' in text:
        text = text.replace('[question]', '')
        return f'<span style="color: #7B1FA2; font-weight: 500;">❓ {text}</span>'
    elif '[answer]' in text:
        text = text.replace('[answer]', '')
        return f'<span style="color: #757575; font-style: italic;">💡 {text}</span>'
    elif '[emphasis]' in text:
        text = text.replace('[emphasis]', '')
        return f'<span style="color: #C62828; font-weight: bold;">⭐ {text}</span>'
    
    return text


def show_slide_preview(slide, slide_num):
    """Display a single slide preview"""
    
    # Determine layout
    has_content = len(slide['content']) > 0
    has_two_col = len(slide['left']) > 0 or len(slide['right']) > 0
    has_four_box = any([
        len(slide['lefttop']) > 0,
        len(slide['righttop']) > 0,
        len(slide['leftbottom']) > 0,
        len(slide['rightbottom']) > 0
    ])
    
    # Preview container with slide-like appearance
    st.markdown(f"""
        <div style="
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 300px;
        ">
            <div style="
                background: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h3 style="color: #1976D2; margin-bottom: 20px; border-bottom: 2px solid #1976D2; padding-bottom: 10px;">
                    {slide['title'] if slide['title'] else 'Untitled Slide'}
                </h3>
    """, unsafe_allow_html=True)
    
    # Single column content
    if has_content:
        st.markdown('<div style="margin: 15px 0;">', unsafe_allow_html=True)
        for item in slide['content']:
            if item:
                formatted = format_text_with_tags(item)
                st.markdown(f'<p style="margin: 8px 0; line-height: 1.6;">{formatted}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Two column layout
    elif has_two_col:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div style="padding-right: 10px;">', unsafe_allow_html=True)
            for item in slide['left']:
                if item:
                    formatted = format_text_with_tags(item)
                    st.markdown(f'<p style="margin: 8px 0;">{formatted}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="padding-left: 10px; border-left: 2px solid #eee;">', unsafe_allow_html=True)
            for item in slide['right']:
                if item:
                    formatted = format_text_with_tags(item)
                    st.markdown(f'<p style="margin: 8px 0;">{formatted}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Four box layout
    elif has_four_box:
        col1, col2 = st.columns(2)
        
        with col1:
            if slide['lefttop']:
                st.markdown('<div style="border: 1px solid #ddd; padding: 10px; margin: 5px; border-radius: 5px; background: #f9f9f9;">', unsafe_allow_html=True)
                for item in slide['lefttop']:
                    if item:
                        formatted = format_text_with_tags(item)
                        st.markdown(f'<p style="margin: 5px 0; font-size: 0.9em;">{formatted}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if slide['leftbottom']:
                st.markdown('<div style="border: 1px solid #ddd; padding: 10px; margin: 5px; border-radius: 5px; background: #f9f9f9;">', unsafe_allow_html=True)
                for item in slide['leftbottom']:
                    if item:
                        formatted = format_text_with_tags(item)
                        st.markdown(f'<p style="margin: 5px 0; font-size: 0.9em;">{formatted}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if slide['righttop']:
                st.markdown('<div style="border: 1px solid #ddd; padding: 10px; margin: 5px; border-radius: 5px; background: #f9f9f9;">', unsafe_allow_html=True)
                for item in slide['righttop']:
                    if item:
                        formatted = format_text_with_tags(item)
                        st.markdown(f'<p style="margin: 5px 0; font-size: 0.9em;">{formatted}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            if slide['rightbottom']:
                st.markdown('<div style="border: 1px solid #ddd; padding: 10px; margin: 5px; border-radius: 5px; background: #f9f9f9;">', unsafe_allow_html=True)
                for item in slide['rightbottom']:
                    if item:
                        formatted = format_text_with_tags(item)
                        st.markdown(f'<p style="margin: 5px 0; font-size: 0.9em;">{formatted}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Show notes if present
    if slide['notes']:
        st.markdown('''
            <div style="
                margin-top: 15px; 
                padding: 10px; 
                background: #FFF9C4; 
                border-left: 4px solid #FBC02D;
                border-radius: 3px;
            ">
                <strong style="color: #F57F17;">📝 Teacher Notes:</strong>
        ''', unsafe_allow_html=True)
        for note in slide['notes']:
            if note:
                st.markdown(f'<p style="margin: 5px 0; color: #666; font-size: 0.9em;">{note}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close containers
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Slide number badge
    st.markdown(f'''
        <div style="text-align: right; margin-top: 5px;">
            <span style="
                background: #1976D2;
                color: white;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: bold;
            ">
                Slide {slide_num}
            </span>
        </div>
    ''', unsafe_allow_html=True)


# ============================================================================
# VALIDATION AND GENERATION FUNCTIONS
# ============================================================================

def validate_content():
    """Validate the content"""
    if not st.session_state.content.strip():
        st.warning("⚠️ Please enter some content first")
        return
    
    if not GENERATOR_AVAILABLE:
        st.error("⚠️ Generator module not available")
        return
    
    try:
        temp_file = "temp_validation.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(st.session_state.content)
        
        slides = parse_content_file(temp_file)
        
        all_issues = []
        for i, slide in enumerate(slides, 1):
            issues = validate_slide(slide, i, st.session_state.custom_config)
            all_issues.extend(issues)
        
        st.session_state.validation_results = {
            'success': True,
            'slide_count': len(slides),
            'issues': all_issues
        }
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    except Exception as e:
        st.session_state.validation_results = {
            'success': False,
            'error': str(e)
        }


def generate_presentation():
    """Generate PowerPoint presentation"""
    if not st.session_state.content.strip():
        st.warning("⚠️ Please enter some content first")
        return
    
    if not GENERATOR_AVAILABLE:
        st.error("⚠️ Generator module not available")
        return
    
    try:
        with st.spinner("🎨 Generating presentation..."):
            temp_input = "temp_content.txt"
            with open(temp_input, 'w', encoding='utf-8') as f:
                f.write(st.session_state.content)
            
            temp_output = "temp_presentation.pptx"
            slides = parse_content_file(temp_input)
            build_presentation(slides, temp_output, st.session_state.custom_config)
            
            with open(temp_output, 'rb') as f:
                pptx_data = f.read()
            
            st.success("✅ Presentation generated successfully!")
            st.download_button(
                label="📥 Download PowerPoint",
                data=pptx_data,
                file_name="presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            
            if os.path.exists(temp_input):
                os.remove(temp_input)
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
    except Exception as e:
        st.error(f"❌ Error generating presentation: {str(e)}")
        st.exception(e)


# ============================================================================
# EDITOR WITH PREVIEW
# ============================================================================

def show_editor():
    """Enhanced editor with live preview panel"""
    st.header("Content Editor")
    
    # File operations
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        uploaded_file = st.file_uploader("📂 Upload .txt file", type=['txt'])
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            st.session_state.content = content
            st.success(f"Loaded: {uploaded_file.name}")
    
    with col2:
        if st.session_state.content:
            st.download_button(
                label="💾 Download .txt",
                data=st.session_state.content,
                file_name="lesson_content.txt",
                mime="text/plain"
            )
    
    # Two column layout: Editor + Preview
    editor_col, preview_col = st.columns([1, 1])
    
    with editor_col:
        st.markdown("### ✏️ Edit Content")
        content = st.text_area(
            "Content Editor",
            value=st.session_state.content,
            height=500,
            help="Write your lesson content here",
            label_visibility="collapsed"
        )
        st.session_state.content = content
    
    with preview_col:
        st.markdown("### 👁️ Live Preview")
        
        if st.session_state.content.strip():
            try:
                slides = parse_slides_for_preview(st.session_state.content)
                
                if slides:
                    # Slide selector
                    slide_options = [f"Slide {i+1}: {s['title'][:30] if s['title'] else 'Untitled'}" 
                                   for i, s in enumerate(slides)]
                    
                    selected = st.selectbox(
                        "Select slide to preview:",
                        range(len(slides)),
                        format_func=lambda x: slide_options[x]
                    )
                    
                    # Show preview
                    show_slide_preview(slides[selected], selected + 1)
                    
                    # Navigation
                    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
                    with nav_col1:
                        if selected > 0:
                            if st.button("⬅️ Previous"):
                                st.rerun()
                    with nav_col3:
                        if selected < len(slides) - 1:
                            if st.button("Next ➡️"):
                                st.rerun()
                    
                    st.info(f"📊 Total slides: {len(slides)}")
                else:
                    st.warning("No slides found. Start with:\n```\nSlide 1\nTitle: Your Title\nContent: Your content\n```")
            except Exception as e:
                st.error(f"Preview error: {str(e)}")
                st.info("Check your syntax and try again")
        else:
            st.info("👈 Start typing to see preview")
            st.markdown("""
            **Quick Start:**
            ```
            Slide 1
            Title: My First Slide
            Content: Hello World!
            ---
            ```
            """)
    
    # Action buttons below
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        validate_button = st.button("✅ Validate Content", use_container_width=True)
    
    with col2:
        generate_button = st.button("🎨 Generate PowerPoint", 
                                    type="primary", 
                                    use_container_width=True,
                                    disabled=not GENERATOR_AVAILABLE)
    
    with col3:
        clear_button = st.button("🗑️ Clear All", use_container_width=True)
    
    # Handle button actions
    if validate_button:
        validate_content()
    
    if generate_button:
        generate_presentation()
    
    if clear_button:
        st.session_state.content = ""
        st.session_state.validation_results = None
        st.rerun()
    
    # Show validation results
    if st.session_state.validation_results:
        st.markdown("---")
        st.markdown("### 🔍 Validation Results")
        
        results = st.session_state.validation_results
        
        if results['success']:
            st.success(f"✅ Found {results['slide_count']} slides")
            
            if results['issues']:
                st.warning(f"⚠️ {len(results['issues'])} issues found:")
                for issue in results['issues']:
                    st.write(f"  • {issue}")
            else:
                st.success("✅ No issues found! Ready to generate.")
        else:
            st.error("❌ Validation failed:")
            st.write(results['error'])


# ============================================================================
# QUICK REFERENCE
# ============================================================================

def show_reference():
    """Show quick reference guide"""
    st.header("📖 Quick Reference Guide")
    
    st.markdown(get_quick_reference())
    
    st.markdown("### Layout Types")
    
    st.markdown("**Single Column:**")
    st.code("Content: Main point", language="text")
    
    st.markdown("**Two Columns:**")
    st.code("Left: Left content\nRight: Right content", language="text")
    
    st.markdown("**Four Boxes:**")
    st.code("LeftTop: Content\nRightTop: Content\nLeftBottom: Content\nRightBottom: Content", language="text")
    
    st.markdown("### Style Tags")
    st.markdown("""
- `[vocabulary]` - Custom color (set in sidebar)
- `[question]` - Custom color (set in sidebar)
- `[answer]` - Custom color (set in sidebar)
- `[emphasis]` - Custom color (set in sidebar)
- `[step]` - Creates animation steps
""")


# ============================================================================
# HELP SECTION (CONTINUED IN NEXT PART DUE TO LENGTH)
# ============================================================================

def get_ai_instructions():
    """Return complete AI instruction file content"""
    return """================================================================================
AI INSTRUCTIONS: PowerPoint Generator Content Format
================================================================================

PURPOSE: You are creating lesson content for the PowerPoint Generator.
This file explains the EXACT format required for the content to work properly.
"""
Shared Help Functions for PowerPoint Generator Web Apps
========================================================
Copy these functions into both MyES and Universal versions
Replace the existing show_help() function with this code
"""

import streamlit as st


def get_ai_instructions():
    """Return complete AI instruction file content - SHARED ACROSS BOTH VERSIONS"""
    return """================================================================================
AI INSTRUCTIONS: PowerPoint Generator Content Format
================================================================================

PURPOSE: You are creating lesson content for the PowerPoint Generator.
This file explains the EXACT format required for the content to work properly.

================================================================================
CRITICAL FORMATTING RULES
================================================================================

1. EVERY slide must start with "Slide X" (where X is any number)
2. EVERY slide must have "Title: [text]"
3. Content is organized in sections: Content:, Left:, Right:, etc.
4. Use "---" to separate slides (optional but recommended)
5. Multiple lines under the same section are allowed
6. Lines starting with "#" are comments (ignored)

================================================================================
CONTENT SECTIONS
================================================================================

Content:        Single column content (default layout)
Left:           Left column in two-column layout
Right:          Right column in two-column layout
LeftTop:        Top-left box in four-box layout
RightTop:       Top-right box in four-box layout
LeftBottom:     Bottom-left box in four-box layout
RightBottom:    Bottom-right box in four-box layout
Notes:          Teacher notes (not visible on slides)
Template:       Apply predefined template (vocabulary, reading, comparison)

================================================================================
LAYOUT SELECTION LOGIC
================================================================================

USE Content: FOR:
- Simple slides with one main message
- Title slides with objectives
- Instructions
- Single-topic explanations

USE Left: and Right: FOR:
- Vocabulary (word | definition)
- Comparisons (before | after)
- Advantages vs Disadvantages
- Theory vs Practice

USE LeftTop:, RightTop:, LeftBottom:, RightBottom: FOR:
- Four related concepts (4 project phases, 4 skills)
- Grammar explanations with examples and practice
- Pros/cons with solutions/alternatives

USE LeftTop: (passage) and LeftBottom: (questions) FOR:
- Reading comprehension
- Case studies with questions
- Longer texts with follow-up questions

================================================================================
STYLE TAGS - USE THESE FOR FORMATTING
================================================================================

[vocabulary]    Bold text - Use for NEW vocabulary terms
[question]      Styled text - Use for discussion questions
[answer]        Italic text - Use for model answers
[emphasis]      Bold text - Use for key takeaways
[step]          Creates animations - Use for sequential reveals

EXAMPLES:
Content: [vocabulary] resilience - the ability to recover from failures
Content: [question] What challenges do you face in your role?
Content: [answer] Common challenges include time management and priorities
Content: [emphasis] Remember: Always validate before submitting!
Content: [step] First, identify the problem
Content: [step] Then, analyze possible solutions
Content: [step] Finally, implement and monitor

NOTE: Colors are customizable in the web app settings.

================================================================================
CONTENT LENGTH GUIDELINES
================================================================================

Slide Titles:       Max 60 characters
Single Column:      Up to 500 characters per slide
Two Columns:        Up to 300 characters per column
Four Boxes:         Up to 150 characters per box
Reading Passages:   800-1000 characters (150-250 words)
Questions:          3-5 questions per slide maximum
Vocabulary Items:   4-6 terms per slide

IMPORTANT: Long text automatically reduces font size, but there are limits!

================================================================================
ANIMATIONS & IMAGES - HANDLE IN POWERPOINT
================================================================================

DO NOT INCLUDE IMAGE REFERENCES OR COMPLEX ANIMATIONS IN YOUR CONTENT FILE.

Instead:
✓ Generate clean text-based slides
✓ Add images later in PowerPoint using Insert > Pictures
✓ Recommended: Use stock photo sites like Unsplash, Pexels, Pixabay
✓ Add animations in PowerPoint using the Animations tab
✓ Use [step] tag only for basic text reveals (handled automatically)

Why this approach is better:
- Easier to find and place images in PowerPoint
- More control over image sizing and positioning
- Access to PowerPoint's full animation suite
- Can use built-in stock images (Insert > Stock Images)
- Easier to update and modify later

================================================================================
LESSON STRUCTURE TEMPLATE
================================================================================

A well-structured lesson should follow this pattern:

Slide 1: Title + Objectives
- Use [emphasis] for lesson number/name
- Use [step] for each learning objective (3-4 max)
- Add Notes: with timing and warm-up question

Slide 2: Lead-in / Discussion
- Use [question] for discussion prompts
- Add bullet points with "Think about:"
- Add Notes: with interaction instructions

Slide 3: Reading / Case Study
- Use LeftTop: for passage (150-250 words)
- Use LeftBottom: for comprehension questions (3-4)
- Add Notes: with reading strategy

Slide 4: Vocabulary
- Option A: Use Template: vocabulary
- Option B: Use Left: (term) and Right: (definition)
- Use [vocabulary] tag on terms
- Add Notes: with pronunciation tips

Slide 5: Grammar / Language Focus
- Use four-box layout for rules, examples, practice, notes
- LeftTop: [emphasis] Rule/Form with explanation
- RightTop: [emphasis] Practice with exercises
- LeftBottom: [emphasis] Common Errors
- RightBottom: [emphasis] Usage Notes

Slide 6: Practice Activity
- Use Content: with [emphasis] for task title
- Use [step] for sequential instructions
- Add Notes: with timing and monitoring tips

Slide 7: Speaking / Production
- Use [question] for prompts
- Provide structure/scaffolding
- Add Notes: with grouping suggestions

Slide 8: Recap + Reflection
- Use [emphasis] for "Today we covered:"
- Use checkmarks (✓) for completed items
- Use [question] for reflection questions
- Add Notes: with homework assignment

================================================================================
EXAMPLE COMPLETE SLIDE
================================================================================

Slide 1
Title: Professional Email Writing
Content: [emphasis] Lesson 1
Content: Business Communication Skills
Content: 
Content: Today's Focus:
Content: [step] Email structure and conventions
Content: [step] Professional language and tone
Content: [step] Common business phrases
Notes: Warm-up about email challenges. 5 minutes. Add company logo image in PowerPoint.

---

Slide 2
Title: Lead-in Discussion
Content: [question] How many emails do you write per week?
Content: [question] What makes a professional email effective?
Content: 
Content: Think about:
Content: • Clarity and conciseness
Content: • Appropriate tone
Content: • Professional formatting
Notes: Pair discussion 3 minutes. Elicit responses. Add relevant stock photo in PowerPoint.

---

================================================================================
TEACHER NOTES - ALWAYS INCLUDE
================================================================================

Every slide should have Notes: with:
- Timing estimate (e.g., "5 minutes")
- Interaction type (pair work, whole class, individual)
- Key instructions for teacher
- Common errors to watch for
- Extension activities if time permits
- Suggestions for images to add later (optional)

EXAMPLE:
Notes: Elicit answers first. Drill pronunciation. CCQ: "Can something resilient break easily?" (No). Give 2 min for pair discussion. Monitor for past tense errors. 8-10 minutes total. Suggestion: Add icon/image of person overcoming obstacle.

================================================================================
COMMON MISTAKES TO AVOID
================================================================================

❌ Forgetting "Slide X" at the start
❌ Missing "Title:" on any slide
❌ Using wrong section names (e.g., "LeftSide:" instead of "Left:")
❌ Too much text in four-box layouts (>150 chars per box)
❌ Not using style tags ([vocabulary], [question], etc.)
❌ Forgetting teacher notes
❌ Mixing layouts incorrectly
❌ Including image file references (handle in PowerPoint instead)
❌ Trying to specify complex animations (use PowerPoint instead)

================================================================================
CONTENT GENERATION CHECKLIST
================================================================================

Before submitting content, verify:
□ Every slide starts with "Slide X"
□ Every slide has "Title: [text]"
□ Appropriate layout chosen for content type
□ [vocabulary] tags used for new terms
□ [question] tags used for discussion prompts
□ [emphasis] tags used for key points
□ [step] tags used for sequential content (basic reveals only)
□ Teacher notes included on every slide
□ Content length appropriate (not too long)
□ Slides separated with "---"
□ 8-10 slides total per lesson
□ NO image references (add those in PowerPoint later)
□ NO complex animation specs (handle in PowerPoint)

================================================================================
LEVEL-SPECIFIC GUIDELINES
================================================================================

A1-A2 (Beginner):
- Simple vocabulary and short sentences
- Note in teacher notes: "Add supportive images in PowerPoint"
- 6-8 slides per lesson

B1-B2 (Intermediate):
- Moderate complexity vocabulary
- Longer reading passages (150-200 words)
- 8-10 slides per lesson

C1-C2 (Advanced):
- Advanced vocabulary and idioms
- Complex texts (200-250 words)
- 10-12 slides per lesson

================================================================================
OUTPUT FORMAT
================================================================================

Your output should be plain text starting with:

# Lesson Name
# Level: XX | Duration: XX minutes

Then proceed with slides as shown in examples above.

================================================================================
END OF INSTRUCTIONS
================================================================================
"""


def show_help():
    """Show help and documentation - SHARED ACROSS BOTH VERSIONS"""
    st.header("ℹ️ Help & Documentation")
    
    # AI Instructions Download
    st.markdown("### 🤖 Use AI to Create Lesson Content")
    
    st.info("💡 **Tip:** Let AI do the work! Download the instruction file, give it to any AI (ChatGPT, Claude, etc.) with your lesson requirements, and it will generate properly formatted content.")
    
    st.download_button(
        label="📥 Download AI Instruction File",
        data=get_ai_instructions(),
        file_name="AI_Instructions_PowerPoint_Generator.txt",
        mime="text/plain",
        help="Download this file to give to AI (ChatGPT, Claude, etc.)"
    )
    
    st.markdown("### 📝 Sample AI Prompts")
    
    with st.expander("🗣️ Conversation Practice Lesson"):
        st.code("""I need to create an English lesson using the PowerPoint Generator format.

[Attach or paste the AI_Instructions_PowerPoint_Generator.txt file]

Please create a lesson with these specifications:
- Topic: Conversation practice - Making small talk at networking events
- Level: B1 (Intermediate)
- Duration: 60 minutes
- Focus: Ice breakers, follow-up questions, showing interest
- Include: Vocabulary, example dialogues, practice activities
- 8-10 slides following the structure in the instructions

Generate the complete content file in the exact format specified.""", language="text")
    
    with st.expander("💼 Business English Lesson"):
        st.code("""I need to create an English lesson using the PowerPoint Generator format.

[Attach or paste the AI_Instructions_PowerPoint_Generator.txt file]

Please create a lesson with these specifications:
- Topic: Writing professional emails - Making requests
- Level: B2 (Upper Intermediate)
- Duration: 60 minutes
- Focus: Formal language, polite requests, appropriate tone
- Include: Email structure, key phrases, practice writing activity
- 8-10 slides following the structure in the instructions

Generate the complete content file in the exact format specified.""", language="text")
    
    with st.expander("🔬 Technical/Specialist Language"):
        st.code("""I need to create an English lesson using the PowerPoint Generator format.

[Attach or paste the AI_Instructions_PowerPoint_Generator.txt file]

Please create a lesson with these specifications:
- Topic: IT Architecture - Describing cloud infrastructure
- Level: B2-C1 (Business English for Technical Architects)
- Duration: 60 minutes
- Focus: Technical vocabulary, explaining systems, comparing solutions
- Include: Case study, technical terms, practice describing projects
- 8-10 slides following the structure in the instructions

Generate the complete content file in the exact format specified.""", language="text")
    
    with st.expander("📰 News Article Lesson"):
        st.code("""I need to create an English lesson using the PowerPoint Generator format.

[Attach or paste the AI_Instructions_PowerPoint_Generator.txt file]

Please create a lesson based on this news article:
[Paste the article text or URL]

Specifications:
- Level: B1 (Intermediate)
- Duration: 60 minutes
- Include: Simplified reading passage (200 words), comprehension questions, vocabulary, discussion
- 8-10 slides following the structure in the instructions

Generate the complete content file in the exact format specified.""", language="text")
    
    with st.expander("📚 Grammar Focus Lesson"):
        st.code("""I need to create an English lesson using the PowerPoint Generator format.

[Attach or paste the AI_Instructions_PowerPoint_Generator.txt file]

Please create a lesson with these specifications:
- Topic: Past Simple vs Present Perfect
- Level: B1 (Intermediate)
- Duration: 60 minutes
- Focus: Form, usage differences, time expressions, practice
- Include: Rule explanation, examples, controlled practice, freer practice
- 8-10 slides following the structure in the instructions

Generate the complete content file in the exact format specified.""", language="text")
    
    st.markdown("---")
    
    st.markdown("### 🎨 Adding Images & Animations")
    
    st.info("""
    **Best Practice:** Add images and animations AFTER generating your presentation.
    
    This gives you more control and makes it easier to find the perfect visuals.
    """)
    
    # Platform selection tabs
    img_tab1, img_tab2 = st.tabs(["📊 Google Slides", "📊 PowerPoint"])
    
    with img_tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📷 Adding Images in Google Slides")
            st.write("""
            **Method 1: Upload from Computer**
            1. Click **Insert** > **Image** > **Upload from computer**
            2. Select your image file
            3. Drag to resize and position
            
            **Method 2: Search the Web**
            1. Click **Insert** > **Image** > **Search the web**
            2. Search for your image (uses Google Images)
            3. Click to insert
            
            **Method 3: Insert by URL**
            1. Click **Insert** > **Image** > **By URL**
            2. Paste image link from Unsplash, Pexels, etc.
            3. Click **Insert**
            
            **Method 4: Google Drive**
            - **Insert** > **Image** > **Drive** to use saved images
            
            **Tip:** Right-click image > **Image options** for advanced formatting
            """)
        
        with col2:
            st.markdown("#### ✨ Adding Animations in Google Slides")
            st.write("""
            **Basic Animations:**
            1. **Select** the text box or object
            2. Click **Insert** > **Animation** (or **Slide** menu)
            3. Click **+ Add animation** in the panel
            4. Choose animation type:
               - **Fade in** - subtle reveal
               - **Fly in from left/right** - dynamic entry
               - **Zoom** - emphasis effect
            5. Set **speed** (Slow/Medium/Fast)
            6. Choose **Start condition**:
               - On click (default)
               - After previous
               - With previous
            
            **Animation Panel:**
            - Shows all animations on slide
            - Drag to reorder
            - Click play ▶️ to preview
            
            **Note:** The `[step]` tag creates separate text boxes that you can animate individually.
            """)
        
        st.markdown("**🔍 Recommended Stock Image Sites:**")
        st.markdown("""
        - 🔸 [Unsplash](https://unsplash.com) - High quality, free (right-click > Copy image address)
        - 🔸 [Pexels](https://pexels.com) - Diverse photos & videos (use "Copy link" button)
        - 🔸 [Pixabay](https://pixabay.com) - Photos, vectors, illustrations
        - 🔸 Google Images - Built into Slides (**Insert** > **Image** > **Search the web**)
        """)
    
    with img_tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📷 Adding Images in PowerPoint")
            st.write("""
            1. **Open** your generated presentation
            2. **Go to** Insert > Pictures
            3. **Choose from:**
               - This Device (your files)
               - Stock Images (built-in)
               - Online Pictures (Bing search)
            4. **Resize & position** as needed
            
            **Recommended Stock Image Sites:**
            - 🔸 [Unsplash](https://unsplash.com) - High quality, free
            - 🔸 [Pexels](https://pexels.com) - Diverse photos & videos
            - 🔸 [Pixabay](https://pixabay.com) - Photos, vectors, illustrations
            - 🔸 PowerPoint's built-in stock images
            """)
        
        with col2:
            st.markdown("#### ✨ Adding Animations in PowerPoint")
            st.write("""
            1. **Select** the text or object
            2. **Go to** Animations tab
            3. **Choose** an animation effect
            4. **Set** timing and order
            
            **Popular Choices:**
            - 🔸 Fade/Appear - subtle reveals
            - 🔸 Fly In - dynamic entry
            - 🔸 Wipe - directional reveal
            - 🔸 Animation Pane - manage all animations
            
            **Note:** The `[step]` tag in your content creates basic text reveals automatically.
            """)
    
    st.markdown("---")
    
    st.markdown("### Getting Started")
    st.write("""
    **Option 1: Use AI to Generate Content** ⭐ Recommended
    1. **Download** the AI instruction file above
    2. **Give it to AI** (ChatGPT, Claude, Gemini, etc.) with your lesson specifications
    3. **Copy** the generated content
    4. **Paste** into the editor or upload as .txt file
    5. **Validate** and **Generate**
    6. **Add images & animations** in PowerPoint
    
    **Option 2: Write Content Manually**
    1. **Write or upload** your lesson content using the generator syntax
    2. **Validate** to check for errors
    3. **Generate** to create your PowerPoint presentation
    4. **Add images & animations** in PowerPoint
    5. **Download** and use in your lesson!
    """)
    
    st.markdown("### Common Questions")
    
    with st.expander("❓ How do I create a slide?"):
        st.write("""
        Every slide must start with:
        ```
        Slide 1
        Title: Your Title
        ```
        Then add content using Content:, Left:, Right:, etc.
        Separate slides with `---`
        """)
    
    with st.expander("❓ Should I include image references in my content?"):
        st.write("""
        **No!** It's much easier to add images directly in PowerPoint after generating.
        
        This way you can:
        - Browse and preview images easily
        - Resize and position them perfectly
        - Use PowerPoint's built-in stock images
        - Make changes without regenerating
        """)
    
    with st.expander("❓ How do animations work?"):
        st.write("""
        **Basic animations:** Use the `[step]` tag in your content for automatic text reveals.
        
        **Advanced animations:** Add these in PowerPoint after generating for full control.
        
        Example in content:
        ```
        Content: [step] First point
        Content: [step] Second point
        Content: [step] Third point
        ```
        """)
    
    with st.expander("❓ What if my text is too long?"):
        st.write("""
        The generator automatically reduces font size for long text:
        - 300+ characters → 18pt
        - 500+ characters → 16pt
        - 700+ characters → 14pt
        
        You'll see overflow warnings during validation.
        """)
    
    with st.expander("❓ Can I use this for any subject?"):
        st.write("""
        **Yes!** While designed for language teaching, the generator works for:
        - Any educational subject
        - Training presentations
        - Workshop materials
        - Corporate training
        - Academic lectures
        
        Just focus on clear text content and add subject-specific images in PowerPoint.
        """)
    
    st.markdown("### Example Lesson Structure")
    
    st.code("""
Slide 1 - Title & Objectives (with [step] animations)
Slide 2 - Lead-in Discussion (with [question] tags)
Slide 3 - Reading Passage + Questions (LeftTop/LeftBottom)
Slide 4 - Vocabulary (Two-column or four-box layout)
Slide 5 - Main Content/Explanation (Choose appropriate layout)
Slide 6 - Practice Exercise
Slide 7 - Speaking/Production Activity
Slide 8 - Recap & Homework

Then add relevant images and extra animations in PowerPoint!
    """, language="text")


def show_help():
    """Show help and documentation"""
    st.header("ℹ️ Help & Documentation")
    
    st.markdown("### 🤖 Use AI to Create Lesson Content")
    
    st.info("💡 **Tip:** Let AI do the work! Download the instruction file, give it to any AI (ChatGPT, Claude, etc.) with your lesson requirements, and it will generate properly formatted content.")
    
    # Add rest of help section here from previous artifact
    

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎨 Universal PowerPoint Generator</h1>', unsafe_allow_html=True)
    st.markdown("**Create customized educational presentations**")
    
    # Initialize session state
    if 'content' not in st.session_state:
        st.session_state.content = ""
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'custom_config' not in st.session_state:
        st.session_state.custom_config = DEFAULT_CONFIG.copy()
    if 'background_file' not in st.session_state:
        st.session_state.background_file = None
    
    # Sidebar with customization
    with st.sidebar:
        st.header("🎨 Customization")
        
        with st.expander("📐 Slide Design", expanded=True):
            # Background options
            bg_option = st.radio(
                "Background Type:",
                ["Solid Color", "Upload Image"]
            )
            
            if bg_option == "Solid Color":
                bg_color = st.color_picker(
                    "Background Color",
                    value=rgb_to_hex(st.session_state.custom_config["background_color"])
                )
                st.session_state.custom_config["background_color"] = hex_to_rgb(bg_color)
                st.session_state.custom_config["background_image"] = None
            
            else:  # Upload Image
                uploaded_bg = st.file_uploader(
                    "Upload Background Image",
                    type=['jpg', 'jpeg', 'png'],
                    help="Recommended: 1920x1080 or 1280x720"
                )
                
                if uploaded_bg:
                    bg_path = f"temp_background_{uploaded_bg.name}"
                    with open(bg_path, 'wb') as f:
                        f.write(uploaded_bg.read())
                    st.session_state.custom_config["background_image"] = bg_path
                    st.session_state.background_file = bg_path
                    st.success("✅ Background uploaded")
        
        with st.expander("🔤 Fonts & Colors", expanded=True):
            # Title
            st.subheader("Title")
            title_font = st.selectbox(
                "Title Font:",
                ["Arial", "Calibri", "Times New Roman", "Georgia", "Verdana", 
                 "Tahoma", "Trebuchet MS", "Comic Sans MS", "Impact", "Montserrat"],
                index=0
            )
            st.session_state.custom_config["title_font_name"] = title_font
            
            title_color = st.color_picker(
                "Title Color",
                value=rgb_to_hex(st.session_state.custom_config["title_color"])
            )
            st.session_state.custom_config["title_color"] = hex_to_rgb(title_color)
            
            # Body
            st.subheader("Body Text")
            body_font = st.selectbox(
                "Body Font:",
                ["Arial", "Calibri", "Times New Roman", "Georgia", "Verdana", 
                 "Tahoma", "Trebuchet MS", "Comic Sans MS", "Montserrat"],
                index=0
            )
            st.session_state.custom_config["font_name"] = body_font
            
            text_color = st.color_picker(
                "Text Color",
                value=rgb_to_hex(st.session_state.custom_config["text_color"])
            )
            st.session_state.custom_config["text_color"] = hex_to_rgb(text_color)
        
        with st.expander("🎯 Style Tags", expanded=False):
            st.info("Customize colors for [vocabulary], [question], [answer], [emphasis] tags")
            
            vocab_color = st.color_picker(
                "[vocabulary] Color",
                value=rgb_to_hex(st.session_state.custom_config["styles"]["vocabulary"]["color"])
            )
            st.session_state.custom_config["styles"]["vocabulary"]["color"] = hex_to_rgb(vocab_color)
            
            question_color = st.color_picker(
                "[question] Color",
                value=rgb_to_hex(st.session_state.custom_config["styles"]["question"]["color"])
            )
            st.session_state.custom_config["styles"]["question"]["color"] = hex_to_rgb(question_color)
            
            answer_color = st.color_picker(
                "[answer] Color",
                value=rgb_to_hex(st.session_state.custom_config["styles"]["answer"]["color"])
            )
            st.session_state.custom_config["styles"]["answer"]["color"] = hex_to_rgb(answer_color)
            
            emphasis_color = st.color_picker(
                "[emphasis] Color",
                value=rgb_to_hex(st.session_state.custom_config["styles"]["emphasis"]["color"])
            )
            st.session_state.custom_config["styles"]["emphasis"]["color"] = hex_to_rgb(emphasis_color)
        
        with st.expander("⚙️ Options", expanded=False):
            enable_numbers = st.checkbox(
                "Show slide numbers",
                value=st.session_state.custom_config.get("enable_slide_numbers", True)
            )
            st.session_state.custom_config["enable_slide_numbers"] = enable_numbers
            
            enable_warnings = st.checkbox(
                "Show overflow warnings",
                value=st.session_state.custom_config.get("enable_overflow_warnings", True)
            )
            st.session_state.custom_config["enable_overflow_warnings"] = enable_warnings
        
        st.markdown("---")
        
        if st.button("🔄 Reset to Defaults"):
            st.session_state.custom_config = DEFAULT_CONFIG.copy()
            st.rerun()
        
        if st.button("📄 Load Sample"):
            st.session_state.content = get_sample_template()
            st.success("Sample loaded!")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["✏️ Editor", "📖 Quick Reference", "❓ Help"])
    
    with tab1:
        show_editor()  # Now calls the preview-enabled editor
    
    with tab2:
        show_reference()
    
    with tab3:
        show_help()


if __name__ == "__main__":
    main()

