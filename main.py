import streamlit as st
import json
import requests
import re
from datetime import datetime
import os

# Import enhanced functions from mock_test_creator
from src.components.mock_test_creator import (
    get_board_specific_guidelines,
    get_subjects_by_board,
    get_available_subjects,
    get_paper_types_by_board_and_grade,
    get_ib_grade_options,
    get_topics_by_board_grade_subject,
    validate_topic_against_curriculum,
    generate_questions,
    test_claude_api,
    verify_api_key,
    create_questions_pdf,
    create_answers_pdf,
    get_comprehensive_curriculum_topics
)

# Configure page
st.set_page_config(
    page_title="II Tuitions Mock Test Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# FIXED CLIPBOARD CSS - STATIC SIZING ONLY
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman:wght@400;700&display=swap');
    
    /* Hide Streamlit elements */
    .stApp > header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* FORCE ROOT FONT SIZE */
    * {
        font-size: 14px !important;
        line-height: 20px !important;
        transform: none !important;
        zoom: 1 !important;
        -webkit-transform: none !important;
        -moz-transform: none !important;
        -ms-transform: none !important;
        -o-transform: none !important;
    }
    
    html, body {
        font-size: 14px !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        font-family: 'Times New Roman', serif !important;
        min-height: 100vh !important;
        font-size: 14px !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    /* FIXED CONTAINER WITH STATIC HEIGHT */
    .main .block-container {
        background: #8B4513 !important;
        border-radius: 20px 20px 10px 10px !important;
        margin: 30px auto !important;
        width: 1200px !important;
        max-width: 1200px !important;
        min-width: 1200px !important;
        /* FIXED HEIGHT - NO DYNAMIC SIZING */
        height: 800px !important;
        min-height: 800px !important;
        max-height: 800px !important;
        padding: 40px 30px 60px 30px !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5) !important;
        position: relative !important;
        transform: perspective(1200px) rotateX(2deg) !important;
        border: 3px solid #654321 !important;
        box-sizing: border-box !important;
        /* PREVENTS CONTENT OVERFLOW */
        overflow: hidden !important;
        /* ULTRA ANTI-SCALING */
        zoom: 1 !important;
        font-size: 14px !important;
    }
    
    /* REALISTIC METAL CLIP */
    .main .block-container::before {
        content: '' !important;
        position: absolute !important;
        top: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 180px !important;
        height: 60px !important;
        background: linear-gradient(145deg, #F5F5F5, #BDBDBD, #909090) !important;
        border-radius: 30px !important;
        box-shadow: 
            0 15px 25px rgba(0, 0, 0, 0.6),
            inset 0 4px 8px rgba(255, 255, 255, 0.6),
            inset 0 -4px 8px rgba(0, 0, 0, 0.3) !important;
        border: 4px solid #777 !important;
        z-index: 20 !important;
    }
    
    /* Add clip center line for realism */
    .main .block-container::after {
        content: '' !important;
        position: absolute !important;
        top: 50px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 160px !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #666, transparent) !important;
        z-index: 21 !important;
    }
    
    /* FIXED PAPER WITH STATIC HEIGHT AND SCROLLING */
    .main .block-container > div {
        background: #FFFEF7 !important;
        border-radius: 12px !important;
        /* FIXED HEIGHT - NO DYNAMIC SIZING */
        height: 100% !important;
        min-height: 100% !important;
        max-height: 100% !important;
        position: relative !important;
        box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.08) !important;
        border: 2px solid #E0E0E0 !important;
        padding: 70px 60px 60px 120px !important;
        margin: 0 !important;
        word-wrap: break-word !important;
        z-index: 5 !important;
        box-sizing: border-box !important;
        /* SCROLLABLE CONTENT WITHIN FIXED CONTAINER */
        overflow-y: auto !important;
        overflow-x: hidden !important;
        /* NUCLEAR ANTI-SCALING LOCKS */
        width: 100% !important;
        max-width: 100% !important;
        font-size: 14px !important;
        line-height: 20px !important;
        zoom: 1 !important;
        transform: none !important;
        -webkit-transform: none !important;
        -moz-transform: none !important;
        -ms-transform: none !important;
        -o-transform: none !important;
        contain: none !important;
    }
    
    /* STREAMLIT SPECIFIC OVERRIDES */
    .main .block-container > div > div,
    .main .block-container > div > div > div,
    .main .block-container > div > div > div > div {
        font-size: 14px !important;
        line-height: 20px !important;
        zoom: 1 !important;
        transform: none !important;
        -webkit-transform: none !important;
        -moz-transform: none !important;
        contain: none !important;
        height: auto !important;
        min-height: auto !important;
    }
    
    /* FIXED Paper lines - STATIC BACKGROUND */
    .main .block-container > div::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        /* STATIC HEIGHT FOR FIXED BACKGROUND */
        height: 100% !important;
        background-image: 
            linear-gradient(90deg, transparent 90px, #FF6B6B 90px, #FF6B6B 93px, transparent 93px),
            repeating-linear-gradient(180deg, transparent 0px, transparent 28px, #B8E6FF 28px, #B8E6FF 31px) !important;
        background-size: 100% 33px !important;
        background-repeat: repeat !important;
        background-attachment: local !important;
        pointer-events: none !important;
        opacity: 0.4 !important;
        z-index: 1 !important;
    }
    
    /* FIXED Paper holes - STATIC BACKGROUND */
    .main .block-container > div::after {
        content: '' !important;
        position: absolute !important;
        left: 35px !important;
        top: 40px !important;
        width: 20px !important;
        /* STATIC HEIGHT FOR FIXED HOLES */
        height: 100% !important;
        background: repeating-linear-gradient(to bottom,
            transparent 0px, transparent 20px,
            #F0F0F0 25px, #F0F0F0 40px,
            transparent 45px, transparent 65px) !important;
        z-index: 2 !important;
        pointer-events: none !important;
        background-attachment: local !important;
    }
    
    /* NUCLEAR FONT LOCKS FOR ALL STREAMLIT ELEMENTS */
    .stMarkdown,
    .stMarkdown *,
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown p,
    .stMarkdown div,
    .stMarkdown span,
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] *,
    .main .block-container *,
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4,
    .main .block-container h5,
    .main .block-container h6,
    .main .block-container p,
    .main .block-container div,
    .main .block-container span {
        /* NUCLEAR SCALING PREVENTION */
        font-size: 14px !important;
        line-height: 20px !important;
        zoom: 1 !important;
        transform: none !important;
        -webkit-transform: none !important;
        -moz-transform: none !important;
        -ms-transform: none !important;
        -o-transform: none !important;
        contain: none !important;
        /* FIXED PROPERTIES */
        position: relative !important;
        z-index: 10 !important;
        color: #2c3e50 !important;
        font-family: 'Times New Roman', serif !important;
        max-width: 100% !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        hyphens: auto !important;
    }
    
    .main .block-container h1 {
        text-align: center !important;
        font-size: 32px !important;
        line-height: 40px !important;
        margin-bottom: 16px !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .main .block-container h2 {
        text-align: center !important;
        font-size: 20px !important;
        line-height: 28px !important;
        font-style: italic !important;
        margin-bottom: 16px !important;
        color: #34495e !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .main .block-container h3 {
        font-size: 18px !important;
        line-height: 26px !important;
        margin-bottom: 12px !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    /* NUCLEAR BUTTON LOCKS */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 3px 6px rgba(102, 126, 234, 0.4) !important;
        font-family: 'Times New Roman', serif !important;
        font-size: 14px !important;
        line-height: 20px !important;
        min-width: 150px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        zoom: 1 !important;
        transform: none !important;
        -webkit-transform: none !important;
        -moz-transform: none !important;
        contain: strict !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        -webkit-transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.5) !important;
        zoom: 1 !important;
    }
    
    /* NUCLEAR FORM LOCKS */
    div[data-testid="stSelectbox"] > div > div {
        background: white !important;
        border: 2px solid #DDD !important;
        border-radius: 6px !important;
        font-family: 'Times New Roman', serif !important;
        font-size: 14px !important;
        line-height: 20px !important;
        zoom: 1 !important;
        transform: none !important;
        contain: strict !important;
    }
    
    div[data-testid="stTextInput"] > div > div > input {
        background: white !important;
        border: 2px solid #DDD !important;
        border-radius: 6px !important;
        font-family: 'Times New Roman', serif !important;
        padding: 8px 10px !important;
        font-size: 14px !important;
        line-height: 20px !important;
        zoom: 1 !important;
        transform: none !important;
        contain: strict !important;
    }
    
    /* NUCLEAR STATS BADGE */
    .stats-badge {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        padding: 12px 24px !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        line-height: 24px !important;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3) !important;
        display: inline-block !important;
        margin: 12px auto !important;
        text-align: center !important;
        min-width: 300px !important;
        position: relative !important;
        z-index: 10 !important;
        zoom: 1 !important;
        transform: none !important;
        contain: strict !important;
    }
    
    /* NUCLEAR COMPONENT LOCKS */
    .instructions-box,
    .step-box,
    .validation-box,
    .question-box,
    .review-section,
    .review-card {
        font-size: 14px !important;
        line-height: 20px !important;
        zoom: 1 !important;
        transform: none !important;
        contain: none !important;
    }
    
    .instructions-box {
        background: rgba(255, 248, 220, 0.9) !important;
        border: 2px solid #f39c12 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 16px 0 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
        z-index: 10 !important;
    }
    
    .instructions-title {
        font-size: 16px !important;
        line-height: 24px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
        margin-bottom: 10px !important;
        text-decoration: underline !important;
        text-align: center !important;
        font-family: 'Times New Roman', serif !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .step-box {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #DDD !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 12px 0 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
        border-left: 3px solid #667eea !important;
        z-index: 10 !important;
    }
    
    .step-number {
        position: absolute !important;
        top: -8px !important;
        left: 10px !important;
        background: #667eea !important;
        color: white !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: bold !important;
        font-size: 12px !important;
        line-height: 16px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .step-title {
        font-size: 14px !important;
        line-height: 20px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
        margin-bottom: 6px !important;
        margin-left: 12px !important;
        font-family: 'Times New Roman', serif !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .validation-box {
        background: rgba(240, 248, 255, 0.95) !important;
        border: 2px dashed #667eea !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 16px 0 !important;
        text-align: center !important;
        position: relative !important;
        z-index: 10 !important;
    }
    
    .validation-title {
        font-size: 14px !important;
        line-height: 20px !important;
        font-weight: bold !important;
        color: #667eea !important;
        margin-bottom: 6px !important;
        font-family: 'Times New Roman', serif !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .question-box {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #DDD !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 12px 0 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
        border-left: 3px solid #667eea !important;
        position: relative !important;
        z-index: 10 !important;
        max-width: 100% !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        hyphens: auto !important;
    }
    
    .question-box h4,
    .question-box p,
    .question-box div {
        font-size: 14px !important;
        line-height: 20px !important;
        margin: 6px 0 !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .review-section {
        background: rgba(255, 255, 255, 0.7) !important;
        color: #2c3e50 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 16px 0 !important;
        text-align: center !important;
        position: relative !important;
        z-index: 10 !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .review-card {
        background: rgba(102, 126, 234, 0.1) !important;
        padding: 14px !important;
        border-radius: 10px !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        text-align: center !important;
        transition: transform 0.3s ease !important;
        margin: 8px 0 !important;
        color: #2c3e50 !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1) !important;
        zoom: 1 !important;
        transform: none !important;
    }
    
    .review-card:hover {
        transform: translateY(-1px) !important;
        -webkit-transform: translateY(-1px) !important;
        zoom: 1 !important;
    }
    
    /* NUCLEAR SUCCESS/ERROR LOCKS */
    .stSuccess, .stError, .stWarning, .stInfo {
        font-family: 'Times New Roman', serif !important;
        position: relative !important;
        z-index: 10 !important;
        font-size: 14px !important;
        line-height: 20px !important;
        zoom: 1 !important;
        transform: none !important;
        contain: none !important;
    }
    
    /* STREAMLIT COMPONENT OVERRIDES */
    .stSelectbox,
    .stTextInput,
    .stRadio,
    .stCheckbox {
        zoom: 1 !important;
        transform: none !important;
        font-size: 14px !important;
        contain: none !important;
    }
    
    /* MOBILE RESPONSIVE FIXES */
    @media (max-width: 768px) {
        * {
            font-size: 12px !important;
            line-height: 18px !important;
            zoom: 1 !important;
            transform: none !important;
        }
        
        .main .block-container {
            margin: 15px 5px !important;
            padding: 25px 15px 40px 15px !important;
            transform: none !important;
            width: 95% !important;
            max-width: none !important;
            /* FIXED MOBILE HEIGHT */
            height: 600px !important;
            min-height: 600px !important;
            max-height: 600px !important;
            font-size: 12px !important;
        }
        
        .main .block-container > div {
            padding: 40px 20px 40px 70px !important;
            /* FIXED MOBILE PAPER HEIGHT */
            height: 100% !important;
            min-height: 100% !important;
            max-height: 100% !important;
            font-size: 12px !important;
        }
        
        /* MOBILE PAPER LINES AND HOLES - STATIC */
        .main .block-container > div::before {
            height: 100% !important;
        }
        
        .main .block-container > div::after {
            height: 100% !important;
        }
        
        .main .block-container h1 {
            font-size: 24px !important;
            line-height: 32px !important;
        }
        
        .main .block-container h2 {
            font-size: 16px !important;
            line-height: 24px !important;
        }
        
        .main .block-container::before {
            width: 140px !important;
            height: 45px !important;
            top: 15px !important;
        }
        
        .main .block-container::after {
            width: 120px !important;
            top: 40px !important;
        }
        
        .stats-badge {
            min-width: 280px !important;
            font-size: 12px !important;
            line-height: 18px !important;
            padding: 10px 18px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
CLAUDE_API_KEY = ""
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# Add these imports for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def display_generated_test(test_data):
    """Display the generated test in a formatted way with enhanced curriculum info"""
    if not test_data:
        st.error("No test data to display")
        return
    
    test_info = test_data.get('test_info', {})
    questions = test_data.get('questions', [])
    show_answers_on_screen = test_info.get('show_answers_on_screen', False)
    
    # Test header
    st.markdown(f"""
    # 🎓 II Tuition Mock Test Generated
    
    ## {test_info.get('subject', 'Subject')} Mock Test
    
    **Board:** {test_info.get('board', 'N/A')} | **Grade:** {test_info.get('grade', 'N/A')} | **Topic:** {test_info.get('topic', 'N/A')}
    
    **Paper Type:** {test_info.get('paper_type', 'N/A')} | **Total Questions:** {test_info.get('total_questions', len(questions))}
    
    **Curriculum Standard:** {test_info.get('curriculum_standard', 'N/A')}
    """)
    
    # Instructions section
    st.markdown("### 📋 Instructions:")
    
    with st.container():
        st.markdown("""
        <div class="instructions-box">
            <div class="instructions-title">📖 Test Guidelines</div>
            <p style="color: #2c3e50; margin-bottom: 0;">This test is designed according to your curriculum standards. Read questions carefully and choose the best answers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    instructions_col1, instructions_col2 = st.columns(2)
    
    with instructions_col1:
        st.markdown("""
        - Read all questions carefully before answering
        - For multiple choice questions, select the best option
        - Take your time to understand each question
        """)
    
    with instructions_col2:
        st.markdown("""
        - Show all working for calculation problems
        - Write clearly for descriptive answers
        - Manage your time effectively
        """)
    
    st.markdown("---")
    
    # Questions display
    for i, question in enumerate(questions, 1):
        with st.container():
            st.markdown(f"""
            <div class="question-box">
                <h4 style="color: #667eea; margin-bottom: 0.5rem;">Question {i}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"**{question.get('question', 'Question text missing')}**")
        
        if question.get('type') == 'mcq' and 'options' in question:
            options = question['options']
            for option_key, option_text in options.items():
                st.write(f"**{option_key})** {option_text}")
            
            # Only show correct answer if "Show Answers on Screen" was checked
            if show_answers_on_screen and 'correct_answer' in question and question['correct_answer']:
                st.success(f"**Correct Answer: {question['correct_answer']}**")
                # Show explanation if available
                if 'explanation' in question and question['explanation']:
                    st.info(f"**Explanation:** {question['explanation']}")
        
        elif question.get('type') == 'short' or question.get('type') == 'short_answer':
            marks = question.get('marks', 3)
            st.write(f"**[Short Answer Question - {marks} marks]**")
            st.write("Write your detailed answer below:")
            # Only show sample answer if "Show Answers on Screen" was checked
            if show_answers_on_screen and 'sample_answer' in question and question['sample_answer']:
                st.info(f"**Sample Answer:** {question['sample_answer']}")
        
        elif question.get('type') == 'long' or question.get('type') == 'long_answer':
            marks = question.get('marks', 6)
            st.write(f"**[Long Answer Question - {marks} marks]**")
            st.write("Write your detailed answer with proper explanations:")
            # Only show sample answer if "Show Answers on Screen" was checked
            if show_answers_on_screen and 'sample_answer' in question and question['sample_answer']:
                st.info(f"**Sample Answer:** {question['sample_answer']}")
        
        st.markdown("---")

# Initialize enhanced session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

if 'generated_test' not in st.session_state:
    st.session_state.generated_test = None

if 'form_data' not in st.session_state:
    st.session_state.form_data = {
        'board': '',
        'grade': 0,
        'subject': '',
        'topic': '',
        'paper_type': '',
        'curriculum_topics': []
    }

# Enhanced session state for curriculum tracking
if 'curriculum_data' not in st.session_state:
    st.session_state.curriculum_data = {}

if 'last_validated_topic' not in st.session_state:
    st.session_state.last_validated_topic = ''

# MAIN APPLICATION CONTENT - ENHANCED WITH CURRICULUM INTEGRATION
if st.session_state.current_page == 'home':
    # Header - CENTERED AND BIGGER
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 15px;">
            <span style="font-size: 2rem; margin-right: 10px;">🎯</span>
            <h1 style="color: #2c3e50; font-size: 2.5rem; margin: 0;">II TUITIONS</h1>
        </div>
        <h2 style="color: #34495e; font-size: 1.5rem; font-style: italic; margin-bottom: 1rem;">ENHANCED CURRICULUM-BASED MOCK TEST GENERATOR</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # ENHANCED STATS BADGE WITH CURRICULUM INFO
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: 30px 0;">
        <div class="stats-badge">📊 5,247 Curriculum-Aligned Tests Generated Across 5 Boards</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Instructions with Curriculum Focus
    with st.container():
        st.markdown("""
        <div class="instructions-box">
            <div class="instructions-title">ENHANCED CURRICULUM INSTRUCTIONS:</div>
            <div style="color: #2c3e50; font-size: 1rem; line-height: 1.6;">
                <strong>1.</strong> Select your education board from CBSE, ICSE, IB, Cambridge IGCSE, or State Board<br>
                <strong>2.</strong> Choose your grade level and subject according to board curriculum<br>
                <strong>3.</strong> View curriculum topics and select a relevant topic for your test<br>
                <strong>4.</strong> Enhanced validation ensures 100% curriculum alignment<br>
                <strong>5.</strong> Generated tests match your exact board and grade standards
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Create Test Button - CENTERED AND BIGGER
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Create Curriculum-Aligned Test", use_container_width=True, key="big_create_test"):
            st.session_state.current_page = 'create_test'
            st.rerun()
    
    # Enhanced Review Section with Curriculum Stats
    with st.container():
        st.markdown("""
        <div class="review-section">
            <h2 style="text-align: center; margin-bottom: 2rem;">⭐ Curriculum Performance Review</h2>
            <p style="text-align: center; margin-bottom: 2rem;">Track your progress across different boards and subjects with curriculum-specific feedback</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Review Cards with Curriculum Focus
    cols = st.columns(4)
    review_data = [
        ("📚 Board-wise Performance", "Track performance across different education boards", "CBSE: 89% | ICSE: 92%"),
        ("🎯 Subject Mastery", "Monitor curriculum coverage and topic understanding", "Mathematics: 85% | Science: 91%"),
        ("👨‍🏫 Teacher Analytics", "Detailed curriculum-based performance insights", "Topic Coverage: 78%"),
        ("📈 Progress Tracking", "Grade-wise improvement and curriculum completion", "Grade 10: 94% Complete")
    ]
    
    for i, (title, desc, count) in enumerate(review_data):
        with cols[i]:
            st.markdown(f"""
            <div class="review-card">
                <h3>{title}</h3>
                <p>{desc}</p>
                <div style="color: #FFD700;">⭐⭐⭐⭐⭐</div>
                <p style="font-size: 12px;">{count}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # View Analytics Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 View Curriculum Analytics", use_container_width=True, key="big_view_analytics"):
            st.info("📊 Enhanced curriculum analytics coming soon! This will include detailed performance tracking across all boards and subjects.")

elif st.session_state.current_page == 'create_test':
    st.markdown('# 🎯 Create Curriculum-Aligned Mock Test')
    
    # API Test Section
    st.markdown("### 🔍 Claude AI Configuration Test")
    
    # Show API key status
    st.write("**Current API Key Status:**")
    if CLAUDE_API_KEY and CLAUDE_API_KEY != "REPLACE_WITH_YOUR_API_KEY":
        key_preview = CLAUDE_API_KEY[:15] + "..." + CLAUDE_API_KEY[-8:]
        st.success(f"✅ API Key configured: {key_preview}")
    else:
        st.error("❌ API Key not configured")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Test Claude API", key="test_api_big", use_container_width=True):
            with st.spinner("Testing API connection..."):
                working, message = test_claude_api()
                if working:
                    st.success(f"✅ {message}")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")
                    if "401" in message:
                        st.info("🔧 **Troubleshooting Tips:**")
                        st.info("1. Check if your API key is correct")
                        st.info("2. Verify you have Claude API credits remaining")
                        st.info("3. Make sure the API key hasn't expired")
    
    with col2:
        if st.button("📋 Detailed API Verification", key="verify_api_big", use_container_width=True):
            verify_api_key()
    
    st.markdown("---")
    
    # Step 1: Board Selection
    with st.container():
        st.markdown("""
        <div class="step-box">
            <div class="step-number">1</div>
            <div class="step-title">SELECT EDUCATION BOARD:</div>
        </div>
        """, unsafe_allow_html=True)
    
    board_options = ["Select Board", "CBSE", "ICSE", "IB", "Cambridge IGCSE", "State Board"]
    selected_board = st.selectbox(
        "Choose from major education boards recognized globally", 
        board_options, 
        index=0,
        key="board_select"
    )
    
    if selected_board != "Select Board":
        board = selected_board
        # Store in session state
        st.session_state.form_data['board'] = board
    else:
        board = ''
    
    # Step 2: Enhanced Grade Selection with IB Support
    with st.container():
        st.markdown("""
        <div class="step-box">
            <div class="step-number">2</div>
            <div class="step-title">SELECT GRADE LEVEL:</div>
        </div>
        """, unsafe_allow_html=True)
    
    if board:
        if board == "IB":
            grade_options = ["Select Grade"] + get_ib_grade_options()
            selected_grade = st.selectbox(
                "Select your current IB programme and grade", 
                grade_options, 
                index=0,
                key=f"grade_select_{board}"
            )
            
            if selected_grade != "Select Grade":
                grade = selected_grade
                # Extract numeric grade for processing
                try:
                    grade_num = int(selected_grade.split()[1])
                    st.session_state.form_data['grade'] = grade_num
                except (IndexError, ValueError):
                    grade_num = 0
            else:
                grade = 0
                grade_num = 0
        else:
            grade_options = ["Select Grade"] + [f"Grade {i}" for i in range(1, 13)]
            selected_grade = st.selectbox(
                "Select your current academic grade (1-12)", 
                grade_options, 
                index=0,
                key=f"grade_select_{board}"
            )
            
            if selected_grade != "Select Grade":
                try:
                    grade_text = str(selected_grade)
                    grade_num = int(grade_text.replace("Grade ", ""))
                    grade = grade_num
                    st.session_state.form_data['grade'] = grade_num
                except (ValueError, AttributeError):
                    grade = 0
                    grade_num = 0
            else:
                grade = 0
                grade_num = 0
    else:
        st.selectbox(
            "Select your current academic grade (1-12)", 
            ["Please select Board first"], 
            disabled=True,
            key="grade_disabled"
        )
        grade = 0
        grade_num = 0
    
    # Step 3: Enhanced Subject Selection
    with st.container():
        st.markdown("""
        <div class="step-box">
            <div class="step-number">3</div>
            <div class="step-title">SELECT SUBJECT:</div>
        </div>
        """, unsafe_allow_html=True)
    
    if board and grade:
        available_subjects = get_available_subjects(board, grade_num if board == "IB" else grade)
        
        if available_subjects:
            subject_options = ["Select Subject"] + available_subjects
            selected_subject = st.selectbox(
                "Choose the subject for which you want to generate the mock test", 
                subject_options, 
                index=0,
                key=f"subject_select_{board}_{grade}"
            )
            
            if selected_subject != "Select Subject":
                subject = selected_subject
                st.session_state.form_data['subject'] = subject
                if board == "IB":
                    st.success(f"✅ Selected: {subject} for {board} {grade}")
                else:
                    st.success(f"✅ Selected: {subject} for {board} Grade {grade}")
            else:
                subject = ''
        else:
            st.error(f"❌ No subjects available for {board} Grade {grade}")
            subject = ''
    else:
        st.selectbox(
            "Choose the subject for which you want to generate the mock test", 
            ["Please select Board and Grade first"], 
            disabled=True,
            key=f"subject_placeholder"
        )
        subject = ''
    
    # Step 4: Enhanced Topic Input with Curriculum Display
    with st.container():
        st.markdown("""
        <div class="step-box">
            <div class="step-number">4</div>
            <div class="step-title">ENTER TOPIC (CURRICULUM-ALIGNED):</div>
        </div>
        """, unsafe_allow_html=True)
    
    if subject and board and grade:
        # Get curriculum topics for the selected combination
        curriculum_topics = get_topics_by_board_grade_subject(board, grade_num if board == "IB" else grade, subject)
        
        if curriculum_topics:
            st.info(f"📚 **{board} Grade {grade} {subject} Curriculum Topics:**")
            
            # Display topics in columns for better organization
            cols = st.columns(3)
            for i, topic in enumerate(curriculum_topics[:15]):  # Show first 15 topics
                with cols[i % 3]:
                    st.write(f"• {topic}")
            
            if len(curriculum_topics) > 15:
                st.info(f"📖 And {len(curriculum_topics) - 15} more topics in the curriculum...")
            
            # Store curriculum topics in session state
            st.session_state.form_data['curriculum_topics'] = curriculum_topics
        
        topic_input = st.text_input(
            "Specify the exact topic or chapter you want to focus on", 
            placeholder=f"e.g., {', '.join(curriculum_topics[:3]) if curriculum_topics else 'Enter topic name'}", 
            key=f"topic_input_{subject}"
        )
        
        if topic_input:
            topic = topic_input.strip()
            st.session_state.form_data['topic'] = topic
        else:
            topic = ''
    else:
        st.text_input(
            "Specify the exact topic or chapter you want to focus on", 
            placeholder="Please select board, grade, and subject first", 
            disabled=True,
            key="topic_disabled"
        )
        topic = ''
    
    # Enhanced Topic validation with comprehensive curriculum database
    topic_valid = True
    
    if topic and subject and board and grade:
        # Use enhanced curriculum validation function
        is_relevant, curriculum_topics = validate_topic_against_curriculum(board, grade_num if board == "IB" else grade, subject, topic)
        
        if not is_relevant:
            topic_valid = False
            st.error(f"⚠️ Topic '{topic}' doesn't match {board} Grade {grade} {subject} curriculum")
            
            # Show curriculum-based suggestions
            if curriculum_topics:
                st.info(f"💡 **Suggested topics from {board} Grade {grade} {subject} curriculum:**")
                
                col1, col2 = st.columns(2)
                topics_count = len(curriculum_topics)
                mid_point = min(topics_count // 2, 8)  # Limit to 8 suggestions per column
                
                with col1:
                    st.write("**Primary Topics:**")
                    for i in range(min(mid_point, len(curriculum_topics))):
                        curriculum_topic = str(curriculum_topics[i])
                        st.write(f"• {curriculum_topic}")
                
                with col2:
                    st.write("**Additional Topics:**")
                    start_idx = mid_point
                    for i in range(start_idx, min(start_idx + 8, len(curriculum_topics))):
                        if i < len(curriculum_topics):
                            curriculum_topic = str(curriculum_topics[i])
                            st.write(f"• {curriculum_topic}")
                            
                # Show that there are more topics available
                if len(curriculum_topics) > 16:
                    st.info(f"📚 And {len(curriculum_topics) - 16} more topics in {board} Grade {grade} {subject} curriculum")
        else:
            st.success(f"✅ Topic '{topic}' is valid for {board} Grade {grade} {subject}")
            # Show matched curriculum topics for confirmation
            matched_topics = [t for t in curriculum_topics if topic.lower() in t.lower() or t.lower() in topic.lower()]
            if matched_topics:
                st.info(f"🎯 **Matched curriculum topics:** {', '.join(matched_topics[:3])}")
        
        # Store validation result
        st.session_state.last_validated_topic = topic if is_relevant else ''
    elif topic and not (subject and board and grade):
        st.warning("⚠️ Please select board, grade, and subject first to validate your topic")
        topic_valid = False
    
    # Enhanced Validation Summary
    with st.container():
        st.markdown("""
        <div class="validation-box">
            <div class="validation-title">📋 CURRICULUM VALIDATION SUMMARY</div>
        </div>
        """, unsafe_allow_html=True)
    
    validation_results = []
    
    if board:
        validation_results.append((f"✅ BOARD: {board} Selected", "success"))
    else:
        validation_results.append(("❌ BOARD: Please select a board", "error"))
    
    if grade:
        if board == "IB":
            validation_results.append((f"✅ GRADE: {grade} Selected", "success"))
        else:
            validation_results.append((f"✅ GRADE: Grade {grade} Selected", "success"))
    else:
        validation_results.append(("❌ GRADE: Please select a grade", "error"))
    
    if subject:
        validation_results.append((f"✅ SUBJECT: {subject} Selected", "success"))
    else:
        validation_results.append(("❌ SUBJECT: Please select a subject", "error"))
    
    if topic and topic_valid:
        validation_results.append((f"✅ TOPIC: '{topic}' is Curriculum-Aligned", "success"))
    elif topic and not topic_valid:
        validation_results.append(("❌ TOPIC: Topic doesn't match curriculum", "error"))
    else:
        validation_results.append(("❌ TOPIC: Please enter a topic", "error"))
    
    # Display validation results
    for message, msg_type in validation_results:
        if msg_type == "success":
            st.success(message)
        else:
            st.error(message)
    
    # Check if all validations pass
    valid_count = sum(1 for result in validation_results if result[0].startswith("✅"))
    all_valid = (valid_count == 4)
    
    if all_valid:
        st.success("🎉 All validations passed! Ready to create curriculum-aligned mock test.")
    
    # Step 5: Enhanced Test Configuration with Board-specific Paper Types
    with st.container():
        st.markdown("""
        <div class="step-box">
            <div class="step-number">5</div>
            <div class="step-title">SELECT PAPER TYPE (BOARD-SPECIFIC):</div>
        </div>
        """, unsafe_allow_html=True)
    
    if board and grade:
        # Get paper types based on board and grade
        paper_options = get_paper_types_by_board_and_grade(board, grade_num if board == "IB" else grade)
        
        if paper_options:
            col1, col2 = st.columns(2)
            
            with col1:
                paper_type = st.radio("Choose paper type:", paper_options, key="paper_type_radio")
                st.session_state.form_data['paper_type'] = paper_type
            
            with col2:
                # Enhanced descriptions based on paper type
                if "40 MCQs" in paper_type:
                    st.info("✅ 40 Multiple Choice Questions")
                elif "30 MCQs" in paper_type:
                    st.info("✅ 30 Multiple Choice Questions")
                elif "25 MCQs" in paper_type or "25 MCQ" in paper_type:
                    st.info("✅ 25 Multiple Choice Questions")
                elif "20 Mixed" in paper_type:
                    st.info("✅ 20 Mixed Questions (MCQ + Short)")
                elif "15 Short + 15 Long" in paper_type:
                    st.info("✅ 15 Short + 15 Long Answer Questions")
                elif "15 Activity" in paper_type or "Skills Practice" in paper_type:
                    st.info("✅ 15 Hands-on Activity Tasks")
                elif "25 Exploration" in paper_type or "Inquiry Tasks" in paper_type:
                    st.info("✅ 25 Inquiry-based Questions")
                elif "Primary Assessment" in paper_type or "Foundation Test" in paper_type:
                    st.info("✅ 20 Age-appropriate Mixed Questions")
                elif "Board Pattern Paper 1" in paper_type:
                    st.info("✅ 25 MCQs + 15 Short Answers")
                elif "Board Pattern Paper 2" in paper_type:
                    st.info("✅ 10 Short + 10 Long Answer Questions")
                elif "Sample Paper Format" in paper_type or "Mock" in paper_type:
                    st.info("✅ Full Board Exam Pattern")
                elif "ICSE Board Format Paper 1" in paper_type:
                    st.info("✅ 40 Multiple Choice Questions")
                elif "ICSE Board Format Paper 2" in paper_type:
                    st.info("✅ Descriptive Answer Questions")
                elif "Theory" in paper_type:
                    st.info("✅ Theory Questions (Mixed Format)")
                elif "Practical" in paper_type:
                    st.info("✅ Practical-based Questions")
                elif "A-Level" in paper_type:
                    st.info("✅ Advanced Level Questions")
                elif "HSC Board Pattern" in paper_type:
                    st.info("✅ 40 Higher Secondary Questions")
                elif "State Board" in paper_type:
                    st.info("✅ State Board Exam Pattern")
                elif "Criterion-Based" in paper_type:
                    st.info("✅ 25 Criterion-based Questions")
                elif "Personal Project" in paper_type:
                    st.info("✅ 15 Research Questions")
                elif "Certificate Practice" in paper_type:
                    st.info("✅ 40 Certificate Exam Questions")
                elif "Data Analysis" in paper_type:
                    st.info("✅ Data Analysis & Application")
                elif "Cambridge Primary" in paper_type:
                    st.info("✅ 20 Primary Level Questions")
                elif "Checkpoint" in paper_type:
                    st.info("✅ 30 Checkpoint Assessment Questions")
                elif "Oral Assessment" in paper_type:
                    st.info("✅ 10 Oral Questions")
                else:
                    st.info("✅ Custom Question Format")
        else:
            st.error("❌ No paper types available for this grade")
            paper_type = ""
    else:
        st.radio("Choose paper type:", ["Please select Board and Grade first"], disabled=True, key="paper_type_disabled")
        paper_type = ""
    
    include_answers = st.checkbox("Show answers on screen after generation", value=False, key="show_answers_checkbox")
    
    # Enhanced Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        create_btn = st.button("🚀 GENERATE CURRICULUM-ALIGNED TEST", use_container_width=True, key="big_generate_btn")
        
        if create_btn:
            if not all_valid or not paper_type:
                st.error("❌ Please fix validation errors and select paper type before creating the test")
            else:
                with st.spinner("🤖 Generating curriculum-aligned questions..."):
                    test_data = generate_questions(board, grade_num if board == "IB" else grade, subject, topic, paper_type, include_answers)
                    
                    if test_data:
                        st.success("✅ Curriculum-aligned test generated successfully!")
                        st.balloons()
                        st.session_state.generated_test = test_data
                        st.session_state.current_page = 'test_display'
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate test. Please check your API connection and try again.")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()

elif st.session_state.current_page == 'test_display':
    if st.session_state.generated_test:
        test_data = st.session_state.generated_test
        
        # Enhanced Header buttons with PDF download functionality
        st.markdown("### Navigation & Downloads")
        
        # Create uniform button layout
        button_col1, button_col2, button_col3, button_col4, button_col5 = st.columns([1, 1, 1, 1, 1])
        
        with button_col1:
            if st.button("← Back to Create", key="back_create", use_container_width=True):
                st.session_state.current_page = 'create_test'
                st.rerun()
        
        with button_col2:
            if st.button("🏠 Home", key="home", use_container_width=True):
                st.session_state.current_page = 'home'
                st.rerun()
        
        with button_col3:
            if st.button("📄 Questions PDF", key="q_pdf", use_container_width=True):
                if PDF_AVAILABLE:
                    with st.spinner("Generating questions PDF..."):
                        questions_pdf = create_questions_pdf(test_data, "questions.pdf")
                        if questions_pdf:
                            with open(questions_pdf, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Download Questions",
                                    data=pdf_file.read(),
                                    file_name=f"mock_test_questions_{test_data['test_info']['subject']}_grade_{test_data['test_info']['grade']}.pdf",
                                    mime="application/pdf",
                                    key="download_q"
                                )
                else:
                    st.error("PDF generation not available. Please install reportlab: pip install reportlab")
        
        with button_col4:
            if st.button("📝 Answers PDF", key="a_pdf", use_container_width=True):
                if PDF_AVAILABLE:
                    with st.spinner("Generating answers PDF..."):
                        answers_pdf = create_answers_pdf(test_data, "answers.pdf")
                        if answers_pdf:
                            with open(answers_pdf, "rb") as pdf_file:
                                st.download_button(
                                    label="⬇️ Download Answers",
                                    data=pdf_file.read(),
                                    file_name=f"mock_test_answers_{test_data['test_info']['subject']}_grade_{test_data['test_info']['grade']}.pdf",
                                    mime="application/pdf",
                                    key="download_a"
                                )
                else:
                    st.error("PDF generation not available. Please install reportlab: pip install reportlab")
        
        with button_col5:
            if st.button("🔄 Generate New", key="gen_new", use_container_width=True):
                st.session_state.current_page = 'create_test'
                st.rerun()
        
        # PDF Installation Notice
        if not PDF_AVAILABLE:
            st.warning("📋 **PDF functionality requires additional package.** Run: `pip install reportlab` to enable PDF downloads.")
        
        # Display the generated test with enhanced curriculum info
        display_generated_test(test_data)
        
    else:
        st.warning("No test generated yet. Please create a test first.")
        if st.button("← Back to Create Test"):
            st.session_state.current_page = 'create_test'
            st.rerun()

# Entry point
if __name__ == "__main__":
    pass
