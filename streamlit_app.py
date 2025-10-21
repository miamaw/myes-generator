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


def show_help():
    """Show help and documentation"""
    st.header("ℹ️ Help & Documentation")
    
    st.markdown("### Getting Started")
    st.write("""
    1. **Write or upload** your lesson content using MyES syntax
    2. **Validate** to check for errors
    3. **Generate** to create your PowerPoint presentation
    4. **Download** and use in your lesson!
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
    
    with st.expander("❓ What if my text is too long?"):
        st.write("""
        The generator automatically reduces font size for long text:
        - 300+ characters → 18pt
        - 500+ characters → 16pt
        - 700+ characters → 14pt
        
        You'll see overflow warnings during validation.
        """)
    
    with st.expander("❓ How do I add animations?"):
        st.write("""
        Use `[step]` before each line you want to animate:
        ```
        Content: [step] First point
        Content: [step] Second point
        Content: [step] Third point
        ```
        Each step creates a separate shape for easy animation.
        """)
    
    with st.expander("❓ Can I use images?"):
        st.write("""
        Yes! Upload images to the same folder and reference them:
        ```
        Image: diagram.png | width=5 | align=center
        ```
        Supported parameters: width, left, top, align
        """)
    
    with st.expander("❓ Where's my background template?"):
        st.write("""
        Make sure `Copy of MyES Slides Template 2025.jpg` is in the same 
        folder as this app. The generator uses it for the slide background.
        """)
    
    st.markdown("### Example Lesson Structure")
    
    st.code("""
Slide 1 - Title & Objectives (with [step] animations)
Slide 2 - Lead-in Discussion (with [question] tags)
Slide 3 - Reading Passage + Questions (LeftTop/LeftBottom)
Slide 4 - Vocabulary (Template: vocabulary)
Slide 5 - Grammar Explanation (4-box layout)
Slide 6 - Practice Exercise
Slide 7 - Speaking Activity
Slide 8 - Recap & Homework
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
    
    template_exists = os.path.exists("Copy of MyES Slides Template 2025.jpg")
    
    if template_exists:
        st.success("✅ Background template found")
    else:
        st.error("❌ Background template not found")
        st.write("Please add `Copy of MyES Slides Template 2025.jpg` to the app directory")
    
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