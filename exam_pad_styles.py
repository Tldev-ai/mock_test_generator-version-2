# styles/exam_pad_styles.py
# Centralized styling for II Tuitions Mock Test Generator

def get_exam_pad_css():
    """Centralized CSS for exam pad design with proper scrolling"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman:wght@400;700&display=swap');
    
    /* ==============================================
       RESET & BASE STYLES
    ============================================== */
    .stApp > header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        font-family: 'Times New Roman', serif !important;
        overflow: hidden !important;
        height: 100vh !important;
    }
    
    .main .block-container {
        padding: 0 !important;
        max-width: none !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    section.main > div {
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    /* ==============================================
       EXAM PAD CONTAINER - FIXED VIEWPORT APPROACH
    ============================================== */
    .exam-pad-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        font-family: 'Times New Roman', serif;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    
    .exam-pad-clipboard {
        width: 800px;
        height: 600px;
        background: #8B4513;
        border-radius: 15px 15px 8px 8px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        position: relative;
        transform: perspective(1000px) rotateX(1deg);
        overflow: hidden;
        flex-shrink: 0;
    }
    
    /* Metal clip */
    .exam-pad-clipboard::before {
        content: '';
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        width: 120px;
        height: 40px;
        background: linear-gradient(145deg, #E8E8E8, #A0A0A0);
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.4);
        border: 2px solid #999;
        z-index: 10;
    }
    
    /* Metal clip detail */
    .exam-pad-clipboard::after {
        content: '';
        position: absolute;
        top: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 3px;
        background: linear-gradient(90deg, #666, #888, #666);
        border-radius: 2px;
        z-index: 11;
    }
    
    /* ==============================================
       PAPER CONTENT AREA - SCROLLABLE CONTENT
    ============================================== */
    .exam-pad-paper {
        position: absolute;
        top: 25px;
        left: 15px;
        right: 15px;
        bottom: 25px;
        background: #FFFEF7;
        border-radius: 8px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #E0E0E0;
        overflow-y: auto;
        overflow-x: hidden;
    }
    
    /* Paper lines - FIXED BACKGROUND */
    .exam-pad-paper::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            linear-gradient(90deg, transparent 78px, #FF6B6B 78px, #FF6B6B 80px, transparent 80px),
            repeating-linear-gradient(180deg, transparent 0px, transparent 28px, #B8E6FF 28px, #B8E6FF 30px);
        background-size: 100% 32px;
        pointer-events: none;
        opacity: 0.3;
        z-index: 1;
        background-attachment: fixed;
    }
    
    /* Paper holes - FIXED BACKGROUND */
    .exam-pad-paper::after {
        content: '';
        position: fixed;
        left: 25px;
        top: 0;
        width: 20px;
        height: 100vh;
        background-image: 
            radial-gradient(circle at 50% 35px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 105px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 175px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 245px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 315px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 385px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 455px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 525px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 595px, #F0F0F0 5px, transparent 5px),
            radial-gradient(circle at 50% 665px, #F0F0F0 5px, transparent 5px);
        background-repeat: repeat-y;
        z-index: 2;
        pointer-events: none;
        background-attachment: fixed;
    }
    
    /* Content inside paper */
    .exam-pad-content {
        position: relative;
        z-index: 10;
        color: #2c3e50;
        font-family: 'Times New Roman', serif;
        padding: 60px 40px 100px 100px;
        min-height: 100%;
    }
    
    /* ==============================================
       TYPOGRAPHY STYLES
    ============================================== */
    .exam-pad-content h1 {
        color: #2c3e50 !important;
        text-align: center !important;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
        font-family: 'Times New Roman', serif !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .exam-pad-content h2 {
        color: #34495e !important;
        text-align: center !important;
        font-size: 1.5rem !important;
        font-style: italic !important;
        margin-bottom: 1rem !important;
        font-family: 'Times New Roman', serif !important;
    }
    
    .exam-pad-content h3, .exam-pad-content h4, .exam-pad-content h5 {
        color: #2c3e50 !important;
        font-family: 'Times New Roman', serif !important;
    }
    
    .exam-pad-content p, .exam-pad-content div {
        color: #2c3e50 !important;
        font-family: 'Times New Roman', serif !important;
        line-height: 1.6;
    }
    
    /* ==============================================
       COMPONENT STYLES
    ============================================== */
    
    /* Instructions Box */
    .instructions-box {
        background: rgba(255, 248, 220, 0.9) !important;
        border: 2px solid #f39c12 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 25px 0 !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    .instructions-title {
        font-size: 1.3rem !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
        margin-bottom: 15px !important;
        text-decoration: underline !important;
        text-align: center !important;
        font-family: 'Times New Roman', serif !important;
    }
    
    /* Step Boxes */
    .step-box {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #DDD !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 20px 0 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
        border-left: 4px solid #667eea !important;
    }
    
    .step-number {
        position: absolute !important;
        top: -12px !important;
        left: 15px !important;
        background: #667eea !important;
        color: white !important;
        width: 30px !important;
        height: 30px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2) !important;
    }
    
    .step-title {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
        margin-bottom: 10px !important;
        margin-left: 20px !important;
        font-family: 'Times New Roman', serif !important;
    }
    
    /* Validation Box */
    .validation-box {
        background: rgba(240, 248, 255, 0.95) !important;
        border: 2px dashed #667eea !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 25px 0 !important;
        text-align: center !important;
    }
    
    .validation-title {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        color: #667eea !important;
        margin-bottom: 10px !important;
        font-family: 'Times New Roman', serif !important;
    }
    
    /* Question Boxes */
    .question-box {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #DDD !important;
        border-radius: 12px !important;
        padding: 25px !important;
        margin: 25px 0 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1) !important;
        border-left: 4px solid #667eea !important;
    }
    
    /* Stats Badge */
    .stats-badge {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        padding: 12px 25px !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        display: inline-block !important;
        margin: 10px auto !important;
        text-align: center !important;
    }
    
    /* Review Section */
    .review-section {
        background: linear-gradient(135deg, #2c3e50, #34495e) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 30px !important;
        margin: 30px 0 !important;
        text-align: center !important;
    }
    
    .review-card {
        background: rgba(255, 255, 255, 0.15) !important;
        padding: 20px !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        text-align: center !important;
        transition: transform 0.3s ease !important;
        margin: 10px 0 !important;
    }
    
    .review-card:hover {
        transform: translateY(-3px) !important;
    }
    
    /* ==============================================
       FORM ELEMENT STYLES
    ============================================== */
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        font-family: 'Times New Roman', serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3) !important;
        font-size: 1rem !important;
        padding: 10px 25px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Select boxes */
    div[data-testid="stSelectbox"] > div > div {
        background: white !important;
        border: 2px solid #DDD !important;
        border-radius: 8px !important;
        font-family: 'Times New Roman', serif !important;
    }
    
    /* Text inputs */
    div[data-testid="stTextInput"] > div > div > input {
        background: white !important;
        border: 2px solid #DDD !important;
        border-radius: 8px !important;
        font-family: 'Times New Roman', serif !important;
        padding: 12px 15px !important;
        font-size: 1rem !important;
    }
    
    /* Success/Error/Warning/Info messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        font-family: 'Times New Roman', serif !important;
    }
    
    /* ==============================================
       MOBILE RESPONSIVENESS
    ============================================== */
    @media (max-width: 768px) {
        .exam-pad-clipboard {
            width: 90vw;
            height: 70vh;
            transform: none;
        }
        
        .exam-pad-content {
            padding: 40px 20px 60px 60px;
            font-size: 14px;
        }
        
        .exam-pad-content h1 {
            font-size: 2rem !important;
        }
        
        .exam-pad-content h2 {
            font-size: 1.2rem !important;
        }
    }
    </style>
    """

def get_exam_pad_html():
    """Get exam pad HTML structure"""
    exam_pad_start = """
    <div class="exam-pad-wrapper">
        <div class="exam-pad-clipboard">
            <div class="exam-pad-paper">
                <div class="exam-pad-content">
    """
    
    exam_pad_end = """
                </div>
            </div>
        </div>
    </div>
    """
    
    return exam_pad_start, exam_pad_end
