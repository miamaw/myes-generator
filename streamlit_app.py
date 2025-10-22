"""
MyES PowerPoint Generator - Web App Version
===========================================
Streamlit web interface for creating MyES presentations
Can be run locally or deployed to the cloud
"""

import streamlit as st
import os
import io
from pathlib import Path

# Import the generator functions
try:
    from generate_myes_presentation_enhanced import (
        load_config, parse_content_file, build_presentation,
        validate_slide, DEFAULT_CONFIG
    )
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    st.error("⚠️ Generator module not found. Please ensure generate_myes_presentation_enhanced.py is in the same directory.")

# Page configuration
st.set_page_config(
    page_title="MyES PowerPoint Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for MyES branding
st.markdown("""
    <style>
    .main-header {
        color: #C00000;
        font-family: 'Montserrat', sans-serif;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #000066;
        color: white;
        font-weight: bold;
    }
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
    }
    </style>
""", unsafe_allow_html=True)


def get_quick_reference():
    """Return quick reference text"""
    return """
QUICK REFERENCE
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
  [vocabulary] - green style
  [question] - purple style
  [answer] - gray italic
  [emphasis] - red bold

Images:
  Image: file.jpg | width=5

Math:
  x^2, H_2O, >=, pi

Comments:
  # comment line
"""


def get_sample_template():
    """Return sample lesson template"""
    return """# MyES Lesson Template

Slide 1
Title: Lesson Title Here
Content: [emphasis] Lesson 1
Content: Business English Course
Content: 
Content: Today's Focus:
Content: [step] Learning objective 1
Content: [step] Learning objective 2
Content: [step] Learning objective 3
Notes: Introduce lesson topic. 5 minutes.

---

Slide 2
Title: Discussion Question
Content: [question] What is your experience with [topic]?
Content: 
Content: Think about:
Content: • Point to consider 1
Content: • Point to consider 2
Content: • Point to consider 3
Notes: Give thinking time. Elicit responses.

---

Slide 3
Title: Key Vocabulary
Template: vocabulary
Left: [vocabulary] term one
Right: Definition of first term
Left: [vocabulary] term two
Right: Definition of second term
Notes: Drill pronunciation. Check understanding.

---

Slide 4
Title: Practice Activity
Content: [emphasis] Task Instructions
Content: 
Content: Steps:
Content: [step] Step 1 description
Content: [step] Step 2 description
Content: [step] Step 3 description
Notes: Demonstrate first. Monitor and give feedback.

---
"""


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎨 MyES PowerPoint Generator</h1>', unsafe_allow_html=True)
    st.markdown("**Create professional educational presentations with ease**")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Navigation")
        
        tab_choice = st.radio(
            "Choose a section:",
            ["✏️ Editor", "📖 Quick Reference", "ℹ️ Help", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 🔧 Quick Actions")
        
        if st.button("📄 Load Sample Template"):
            st.session_state.content = get_sample_template()
            st.success("Template loaded!")
        
        st.markdown("---")
        st.markdown("**Version 2.0**")
        st.markdown("*MyES - My English School*")
    
    # Initialize session state
    if 'content' not in st.session_state:
        st.session_state.content = ""
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    
    # Main content based on tab
    if tab_choice == "✏️ Editor":
        show_editor()
    elif tab_choice == "📖 Quick Reference":
        show_reference()
    elif tab_choice == "ℹ️ Help":
        show_help()
    elif tab_choice == "⚙️ Settings":
        show_settings()


def show_editor():
    """Show the main editor interface"""
    
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
    
    # Text editor
    st.markdown("### Edit Your Content")
    content = st.text_area(
        "Content Editor",
        value=st.session_state.content,
        height=400,
        help="Write your lesson content here using the MyES syntax",
        label_visibility="collapsed"
    )
    st.session_state.content = content
    
    # Action buttons
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


def validate_content():
    """Validate the content"""
    if not st.session_state.content.strip():
        st.warning("⚠️ Please enter some content first")
        return
    
    if not GENERATOR_AVAILABLE:
        st.error("⚠️ Generator module not available")
        return
    
    try:
        # Save to temp file
        temp_file = "temp_validation.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(st.session_state.content)
        
        # Parse and validate
        config = load_config() if os.path.exists("myes_config.json") else DEFAULT_CONFIG
        slides = parse_content_file(temp_file)
        
        all_issues = []
        for i, slide in enumerate(slides, 1):
            issues = validate_slide(slide, i, config)
            all_issues.extend(issues)
        
        # Store results
        st.session_state.validation_results = {
            'success': True,
            'slide_count': len(slides),
            'issues': all_issues
        }
        
        # Clean up
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
            # Save content to temp file
            temp_input = "temp_content.txt"
            with open(temp_input, 'w', encoding='utf-8') as f:
                f.write(st.session_state.content)
            
            # Generate presentation
            temp_output = "temp_presentation.pptx"
            config = load_config() if os.path.exists("myes_config.json") else DEFAULT_CONFIG
            slides = parse_content_file(temp_input)
            build_presentation(slides, temp_output, config)
            
            # Read the generated file
            with open(temp_output, 'rb') as f:
                pptx_data = f.read()
            
            # Offer download
            st.success("✅ Presentation generated successfully!")
            st.download_button(
                label="📥 Download PowerPoint",
                data=pptx_data,
                file_name="lesson_slides.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            
            # Clean up
            if os.path.exists(temp_input):
                os.remove(temp_input)
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
    except Exception as e:
        st.error(f"❌ Error generating presentation: {str(e)}")
        st.exception(e)


def show_reference():
    """Show quick reference guide"""
    st.header("📖 Quick Reference Guide")
    
    st.markdown("### Basic Syntax")
    st.code("""
Slide 1
Title: Your Slide Title
Content: Your content here
Content: [step] Animated point
Notes: Teacher notes
---
    """, language="text")
    
    st.markdown("### Layout Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Single Column:**")
        st.code("""
Content: Main point
Content: Another point
        """, language="text")
        
        st.markdown("**Two Columns:**")
        st.code("""
Left: Left content
Right: Right content
        """, language="text")
    
    with col2:
        st.markdown("**Four Boxes:**")
        st.code("""
LeftTop: Content
RightTop: Content
LeftBottom: Content
RightBottom: Content
        """, language="text")
        
        st.markdown("**Reading Layout:**")
        st.code("""
LeftTop: Reading passage...
LeftBottom: 1. Question?
LeftBottom: 2. Question?
        """, language="text")
    
    st.markdown("### Style Tags")
    
    tags = {
        "[vocabulary]": "Green, bold - for new terms",
        "[question]": "Purple - for discussion questions",
        "[answer]": "Gray, italic - for model answers",
        "[emphasis]": "Red, bold - for key points",
        "[step]": "Creates animation steps"
    }
    
    for tag, description in tags.items():
        st.markdown(f"**{tag}** - {description}")
    
    st.markdown("### Special Features")
    st.code("""
# Comments (ignored)
Image: photo.jpg | width=5 | align=center
Template: vocabulary
Math: x^2, H_2O, >=, pi
    """, language="text")



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
ANIMATIONS & IMAGES - HANDLE IN GOOGLE SLIDES OR POWERPOINT
================================================================================

DO NOT INCLUDE IMAGE REFERENCES OR COMPLEX ANIMATIONS IN YOUR CONTENT FILE.

Instead:
✓ Generate clean text-based slides
✓ Add images later using Insert > Image (Google Slides) or Insert > Pictures (PowerPoint)
✓ Recommended: Use stock photo sites like Unsplash, Pexels, Pixabay
✓ Google Slides: Use Insert > Image > Search the web for instant access
✓ Add animations using Insert > Animation (Google Slides) or Animations tab (PowerPoint)
✓ Use [step] tag only for basic text reveals (handled automatically)

Why this approach is better:
- Easier to find and place images in your presentation app
- More control over image sizing and positioning
- Access to full animation suite in Google Slides or PowerPoint
- Can use built-in stock images and web search
- Easier to update and modify later
- Works with both Google Slides and PowerPoint

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
Notes: Warm-up about email challenges. 5 minutes. Add company logo image in Google Slides or PowerPoint.

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
Notes: Pair discussion 3 minutes. Elicit responses. Add relevant stock photo in Google Slides or PowerPoint.

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
Notes: Elicit answers first. Drill pronunciation. CCQ: "Can something resilient break easily?" (No). Give 2 min for pair discussion. Monitor for past tense errors. 8-10 minutes total. Suggestion: Add icon/image of person overcoming obstacle in Google Slides or PowerPoint.

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
❌ Trying to specify complex animations (use Google Slides or PowerPoint instead)

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
□ NO image references (add those in Google Slides or PowerPoint later)
□ NO complex animation specs (handle in Google Slides or PowerPoint)

================================================================================
LEVEL-SPECIFIC GUIDELINES
================================================================================

A1-A2 (Beginner):
- Simple vocabulary and short sentences
- Note in teacher notes: "Add supportive images in Google Slides or PowerPoint"
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
    6. **Download** the .pptx file
    7. **Open in Google Slides** (File > Open > Upload) or PowerPoint
    8. **Add images & animations**
    
    **Option 2: Write Content Manually**
    1. **Write or upload** your lesson content using the generator syntax
    2. **Validate** to check for errors
    3. **Generate** to create your presentation
    4. **Download** the .pptx file
    5. **Open in Google Slides or PowerPoint**
    6. **Add images & animations**
    7. **Use and share** your lesson!
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
        **No!** It's much easier to add images directly in Google Slides or PowerPoint after generating.
        
        This way you can:
        - Browse and preview images easily
        - Resize and position them perfectly
        - Use built-in stock image search in Google Slides
        - Use PowerPoint's built-in stock images
        - Make changes without regenerating
        
        **For Google Slides:** Use **Insert** > **Image** > **Search the web** for instant access to Google Images.
        """)
    
    with st.expander("❓ How do animations work?"):
        st.write("""
        **Basic animations:** Use the `[step]` tag in your content for automatic text reveals.
        
        **Advanced animations:** Add these after generating for full control.
        
        **In Google Slides:**
        1. Select text box
        2. Click **Insert** > **Animation**
        3. Click **+ Add animation**
        4. Choose effect and timing
        
        **In PowerPoint:**
        1. Select text box
        2. Go to **Animations** tab
        3. Choose effect
        
        Example in content:
        ```
        Content: [step] First point
        Content: [step] Second point
        Content: [step] Third point
        ```
        
        Each `[step]` creates a separate text box you can animate individually.
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

def show_settings():
    """Show settings and configuration"""
    st.header("⚙️ Settings")
    
    st.markdown("### Generator Configuration")
    
    # Check if config exists
    config_exists = os.path.exists("myes_config.json")
    
    if config_exists:
        st.success("✅ Configuration file found: myes_config.json")
        
        try:
            config = load_config()
            
            st.markdown("**Current Settings:**")
            st.json({
                "Font": config.get("font_name", "Montserrat"),
                "Title Color": config.get("title_color", [192, 0, 0]),
                "Text Color": config.get("text_color", [0, 0, 102]),
                "Slide Numbers": config.get("enable_slide_numbers", True),
                "Overflow Warnings": config.get("enable_overflow_warnings", True)
            })
            
        except Exception as e:
            st.error(f"Error loading config: {e}")
    else:
        st.info("ℹ️ Using default configuration")
        st.write("To customize, create a `myes_config.json` file with your settings.")
    
    st.markdown("### Template Status")
    
    # Get template name from config
    config = load_config() if os.path.exists("myes_config.json") else DEFAULT_CONFIG
    template_name = config.get("background_image", "MyES Slides Template 2025.jpg")
    template_exists = os.path.exists(template_name)
    
    if template_exists:
        st.success(f"✅ Background template found: {template_name}")
    else:
        st.error(f"❌ Background template not found: {template_name}")
        st.write(f"Please add `{template_name}` to the app directory")
    
    st.markdown("### System Information")
    
    st.write(f"**Generator Available:** {'✅ Yes' if GENERATOR_AVAILABLE else '❌ No'}")
    st.write(f"**Working Directory:** {os.getcwd()}")
    
    # Show files in directory
    with st.expander("📁 Files in current directory"):
        files = os.listdir(".")
        for f in sorted(files):
            st.write(f"  • {f}")


if __name__ == "__main__":
    main()

