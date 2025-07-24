import streamlit as st
import json
import requests
import re
from datetime import datetime
import os

# Import centralized styles - CSS is handled by main.py
# No CSS imports needed here as styles are centralized

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

def get_board_specific_guidelines(board, grade, subject, topic):
    """Get comprehensive guidelines for ALL boards, grades, subjects, and topics"""
    
    # Universal grade-level cognitive development guidelines
    grade_development = {
        1: "Basic recognition, simple vocabulary, concrete concepts, visual learning",
        2: "Simple sentences, basic operations, pattern recognition, foundational skills",
        3: "Expanded vocabulary, multi-step processes, comparison skills, basic analysis",
        4: "Complex sentences, problem-solving, categorization, logical reasoning",
        5: "Abstract thinking begins, detailed explanations, cause-effect relationships",
        6: "Advanced vocabulary, multi-step problems, analytical thinking, applications",
        7: "Complex concepts, critical thinking, detailed analysis, practical applications",
        8: "Abstract reasoning, sophisticated vocabulary, advanced problem-solving",
        9: "High-level analysis, complex applications, preparation for advanced study",
        10: "Board exam preparation, advanced concepts, comprehensive understanding",
        11: "Pre-university level, specialized knowledge, research-based learning",
        12: "University preparation, expert-level understanding, independent analysis"
    }
    
    # Board-specific educational philosophies and styles
    board_characteristics = {
        "CBSE": {
            "philosophy": "Holistic development, practical application, Indian cultural context",
            "language": "Indian English, Hindi transliterations when relevant",
            "examples": "Indian cities, cultural references, local contexts",
            "assessment": "Application-based, real-world problems, analytical thinking",
            "difficulty": "Balanced approach, comprehensive coverage, skill development"
        },
        "ICSE": {
            "philosophy": "Analytical thinking, detailed study, British educational system",
            "language": "British English spellings and grammar",
            "examples": "International contexts, analytical scenarios",
            "assessment": "Detailed answers, analytical questions, comprehensive evaluation",
            "difficulty": "Higher complexity, detailed explanations, thorough understanding"
        },
        "Cambridge IGCSE": {
            "philosophy": "International perspective, global contexts, academic excellence",
            "language": "International English, academic vocabulary",
            "examples": "Global examples, international case studies, multicultural contexts",
            "assessment": "Cambridge assessment style, structured questions, evidence-based answers",
            "difficulty": "International standards, university preparation, rigorous evaluation"
        },
        "IB": {
            "philosophy": "Inquiry-based learning, international mindedness, critical thinking",
            "language": "Academic English, inquiry-based terminology",
            "examples": "Global perspectives, intercultural understanding, real-world applications",
            "assessment": "Concept-based, inquiry-driven, reflection and analysis",
            "difficulty": "High academic rigor, conceptual understanding, independent thinking"
        },
        "State Board": {
            "philosophy": "Regional relevance, state-specific curriculum, accessible education",
            "language": "Local language influences, regional terminology",
            "examples": "State-specific examples, local geography and culture",
            "assessment": "State pattern questions, curriculum-aligned, practical focus",
            "difficulty": "State standards, accessible to diverse learners, practical applications"
        }
    }
    
    # Generate comprehensive guidelines
    def generate_guidelines(board, grade, subject, topic):
        # Get base characteristics
        board_info = board_characteristics.get(board, board_characteristics["CBSE"])
        grade_level = grade_development.get(grade, f"Grade {grade} cognitive level")
        
        guidelines = f"""
BOARD: {board}
{board_info['philosophy']}
Language: {board_info['language']}
Examples: {board_info['examples']}
Assessment Style: {board_info['assessment']}

GRADE {grade} LEVEL:
Cognitive Development: {grade_level}

TOPIC: "{topic}"
Focus: All questions must be specifically about "{topic}" as taught in {board} Grade {grade} {subject}
Complexity: Match {board} Grade {grade} examination standards
Context: Use {board_info['examples']} where appropriate
Language: {board_info['language']} terminology and style
"""
        return guidelines
    
    return generate_guidelines(board, grade, subject, topic)

def get_ib_grade_options():
    """Return IB grade options with programme labels"""
    return [
        "Grade 1 (PYP)",
        "Grade 2 (PYP)", 
        "Grade 3 (PYP)",
        "Grade 4 (PYP)",
        "Grade 5 (PYP)",
        "Grade 6 (MYP)",
        "Grade 7 (MYP)",
        "Grade 8 (MYP)",
        "Grade 9 (MYP)",
        "Grade 10 (MYP)",
        "Grade 11 (DP)",
        "Grade 12 (DP)"
    ]

def get_paper_types_by_board_and_grade(board, grade):
    """Return paper types based on board and grade selection"""
    
    # Extract numeric grade for processing
    if isinstance(grade, str) and "Grade" in grade:
        try:
            if "(" in grade:  # IB format like "Grade 5 (PYP)"
                grade_num = int(grade.split()[1])
            else:  # Standard format like "Grade 5"
                grade_num = int(grade.replace("Grade ", ""))
        except (ValueError, IndexError):
            grade_num = 0
    else:
        grade_num = grade if isinstance(grade, int) else 0
    
    if board == "CBSE":
        if grade_num <= 5:
            return [
                "Primary Assessment (20 Mixed Questions)",
                "Activity-Based Test (15 Practical Tasks)",
                "Oral Assessment (10 Questions)"
            ]
        elif grade_num <= 8:
            return [
                "Periodic Test (35 Mixed Questions)",
                "Unit Test (30 Questions)", 
                "Annual Practice (40 Questions)"
            ]
        elif grade_num <= 10:
            return [
                "Board Pattern Paper 1 (MCQ + Short)",
                "Board Pattern Paper 2 (Long Answer)",
                "Sample Paper Format (Full 80 marks)"
            ]
        else:  # Grades 11-12
            return [
                "Board Exam Pattern (35 Mixed Questions)",
                "Practice Test Series (40 Questions)",
                "Mock Board Paper (80 marks)"
            ]
    
    elif board == "ICSE":
        if grade_num <= 5:
            return [
                "Foundation Test (20 Mixed Questions)",
                "Skills Assessment (15 Activity Questions)",
                "Progress Evaluation (25 Questions)"
            ]
        elif grade_num <= 8:
            return [
                "Class Test Format (30 Questions)",
                "Term Examination (25 MCQ + 10 Descriptive)",
                "Annual Assessment (40 Mixed Questions)"
            ]
        elif grade_num <= 10:
            return [
                "ICSE Board Format Paper 1 (40 MCQs)",
                "ICSE Board Format Paper 2 (Descriptive)",
                "Mock ICSE Paper (Full 80 marks)",
                "Practice Test (35 Mixed Questions)"
            ]
        else:  # Grades 11-12 (ISC)
            return [
                "ISC Board Pattern Paper 1 (Theory)",
                "ISC Board Pattern Paper 2 (Application)",
                "Mock ISC Paper (Full 100 marks)",
                "Practice Assessment (45 Questions)"
            ]
    
    elif board == "IB":
        if "(PYP)" in str(grade) or grade_num <= 5:
            return [
                "Formative Assessment (20 Mixed Questions)",
                "Skills Practice (15 Activity Tasks)", 
                "Inquiry Tasks (25 Exploration Questions)"
            ]
        elif "(MYP)" in str(grade) or (6 <= grade_num <= 10):
            return [
                "Practice Assessment (30 Mixed Questions)",
                "Criterion-Based Test (25 Questions)",
                "Personal Project Prep (15 Research Questions)",
                "MYP Certificate Practice (40 Questions)"
            ]
        elif "(DP)" in str(grade) or grade_num >= 11:
            return [
                "Paper 1 (40 MCQs)",
                "Paper 2 (15 Short + 15 Long Answers)",
                "Paper 3 (Data Analysis & Application)"
            ]
        else:
            return []
    
    elif board == "Cambridge IGCSE":
        if grade_num <= 8:
            return [
                "Cambridge Primary Test (20 Questions)",
                "Lower Secondary Assessment (25 Questions)",
                "Checkpoint Practice (30 Questions)"
            ]
        elif grade_num <= 10:
            return [
                "Paper 1 (30 MCQs)",
                "Paper 2 (Theory - 75 min)",
                "Paper 3 (Practical/Coursework)",
                "Paper 4 (Alternative to Practical)"
            ]
        else:  # Grades 11-12
            return [
                "A-Level AS Paper (35 Questions)",
                "A-Level A2 Paper (40 Questions)",
                "Cambridge Advanced Test (45 Questions)"
            ]
    
    elif board == "State Board":
        if grade_num <= 5:
            return [
                "State Pattern Test (20 Questions)",
                "Monthly Assessment (15 Questions)",
                "Annual Examination (25 Questions)"
            ]
        elif grade_num <= 8:
            return [
                "State Board Format (30 Questions)",
                "Quarterly Test (25 MCQ + 10 Short)",
                "Half-yearly Pattern (35 Questions)"
            ]
        elif grade_num <= 10:
            return [
                "State Board Paper 1 (25 MCQ + 15 Short)",
                "State Board Paper 2 (20 Long Answers)",
                "Annual Exam Pattern (Full State Format)"
            ]
        else:  # Grades 11-12
            return [
                "HSC Board Pattern (40 Mixed Questions)",
                "State Higher Secondary (45 Questions)",
                "Board Exam Format (Full Board Pattern)"
            ]
    
    return []

def get_ib_paper_types(grade):
    """Legacy function - now uses get_paper_types_by_board_and_grade"""
    return get_paper_types_by_board_and_grade("IB", grade)

def get_igcse_paper_types():
    """Legacy function - now uses get_paper_types_by_board_and_grade"""
    return get_paper_types_by_board_and_grade("Cambridge IGCSE", 10)

# COMPREHENSIVE Subject mapping with complete curriculum standards for ALL 5 BOARDS
def get_subjects_by_board():
    return {
        "CBSE": {
            1: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            2: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            3: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            4: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            5: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            6: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education"],
            7: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education"],
            8: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education"],
            9: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education", "Information Technology"],
            10: ["Mathematics", "English", "Hindi", "Science", "Social Science", "Sanskrit", "Computer Science", "Physical Education", "Information Technology"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English Core", "Computer Science", "Economics", "Business Studies", "Accountancy", "Political Science", "Geography", "History", "Psychology", "Physical Education", "Applied Mathematics", "Biotechnology", "Engineering Graphics"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English Core", "Computer Science", "Economics", "Business Studies", "Accountancy", "Political Science", "Geography", "History", "Psychology", "Physical Education", "Applied Mathematics", "Biotechnology", "Engineering Graphics"]
        },
        "ICSE": {
            1: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            2: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            3: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Applications", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            4: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Applications", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            5: ["Mathematics", "English", "Hindi", "EVS (Environmental Studies)", "Computer Applications", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            6: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education"],
            7: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education"],
            8: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education"],
            9: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education", "Economics", "Commercial Studies"],
            10: ["Mathematics", "English", "Hindi", "Physics", "Chemistry", "Biology", "History & Civics", "Geography", "Computer Applications", "Physical Education", "Economics", "Commercial Studies"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accounts", "Business Studies", "Geography", "History", "Political Science", "Psychology", "Sociology", "Art", "Home Science", "Environmental Science"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accounts", "Business Studies", "Geography", "History", "Political Science", "Psychology", "Sociology", "Art", "Home Science", "Environmental Science"]
        },
        "IB": {
            1: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            2: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            3: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            4: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            5: ["Mathematics", "English", "Science", "Social Studies", "Arts", "Physical Education"],
            6: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design"],
            7: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design"],
            8: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design"],
            9: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design", "Computer Science"],
            10: ["Mathematics", "Language & Literature", "Language Acquisition", "Sciences", "Individuals & Societies", "Arts", "Physical & Health Education", "Design", "Computer Science"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English Literature", "Economics", "Business Management", "Psychology", "Geography", "History", "Philosophy", "Computer Science", "Visual Arts", "Theatre", "Music", "Film"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English Literature", "Economics", "Business Management", "Psychology", "Geography", "History", "Philosophy", "Computer Science", "Visual Arts", "Theatre", "Music", "Film"]
        },
        "Cambridge IGCSE": {
            1: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            2: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            3: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            4: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            5: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education"],
            6: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education", "French", "Spanish"],
            7: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education", "French", "Spanish"],
            8: ["Mathematics", "English", "Science", "Social Studies", "ICT", "Art & Design", "Physical Education", "French", "Spanish"],
            9: ["Mathematics", "English First Language", "English Literature", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business Studies", "Accounting", "Geography", "History", "Art & Design", "Music", "Physical Education", "French", "Spanish", "Additional Mathematics"],
            10: ["Mathematics", "English First Language", "English Literature", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business Studies", "Accounting", "Geography", "History", "Art & Design", "Music", "Physical Education", "French", "Spanish", "Additional Mathematics"],
            11: ["Mathematics", "Further Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business", "Accounting", "Geography", "History", "Psychology", "Sociology", "Art & Design", "Music", "Physical Education", "English Language", "English Literature"],
            12: ["Mathematics", "Further Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "Economics", "Business", "Accounting", "Geography", "History", "Psychology", "Sociology", "Art & Design", "Music", "Physical Education", "English Language", "English Literature"]
        },
        "State Board": {
            1: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            2: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            3: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            4: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            5: ["Mathematics", "English", "Mother Tongue", "EVS (Environmental Studies)", "Computer Science", "GK (General Knowledge)", "Art & Craft", "Physical Education"],
            6: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education"],
            7: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education"],
            8: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education"],
            9: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education", "Vocational Subjects"],
            10: ["Mathematics", "English", "Mother Tongue", "Science", "Social Science", "Computer Science", "Physical Education", "Vocational Subjects"],
            11: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accountancy", "Business Studies", "Political Science", "Geography", "History", "Psychology", "Sociology", "Agriculture", "Home Science"],
            12: ["Mathematics", "Physics", "Chemistry", "Biology", "English", "Computer Science", "Economics", "Commerce", "Accountancy", "Business Studies", "Political Science", "Geography", "History", "Psychology", "Sociology", "Agriculture", "Home Science"]
        }
    }

# NEW COMPREHENSIVE CURRICULUM TOPICS DATABASE
def get_comprehensive_curriculum_topics():
    """Complete topic database for all subjects, grades, and boards"""
    return {
        "CBSE": {
            "Mathematics": {
                1: ["Numbers 1-99", "Counting", "Before and After", "Shapes", "Patterns", "Addition", "Subtraction", "Money", "Time", "Measurement"],
                2: ["Numbers 1-100", "Place Value", "Addition", "Subtraction", "Multiplication Tables", "Shapes", "Patterns", "Money", "Time", "Data Handling"],
                3: ["Numbers 1-1000", "Place Value", "Addition", "Subtraction", "Multiplication", "Division", "Fractions", "Shapes", "Measurement", "Data Handling"],
                4: ["Numbers", "Place Value", "Four Operations", "Factors and Multiples", "Fractions", "Decimals", "Measurement", "Geometry", "Data Handling"],
                5: ["Large Numbers", "Four Operations", "Factors and Multiples", "Fractions", "Decimals", "Area and Perimeter", "Data Handling"],
                6: ["Knowing Our Numbers", "Whole Numbers", "Playing with Numbers", "Basic Geometrical Ideas", "Integers", "Fractions", "Decimals", "Data Handling", "Mensuration", "Algebra", "Ratio and Proportion", "Practical Geometry"],
                7: ["Integers", "Fractions and Decimals", "Data Handling", "Simple Equations", "Lines and Angles", "Triangles", "Congruence", "Comparing Quantities", "Rational Numbers", "Practical Geometry", "Perimeter and Area", "Algebraic Expressions", "Exponents and Powers", "Symmetry", "Visualising Solid Shapes"],
                8: ["Rational Numbers", "Linear Equations in One Variable", "Quadrilaterals", "Practical Geometry", "Data Handling", "Squares and Square Roots", "Cubes and Cube Roots", "Comparing Quantities", "Algebraic Expressions", "Mensuration", "Exponents and Powers", "Direct and Inverse Proportions", "Factorisation", "Introduction to Graphs", "Playing with Numbers"],
                9: ["Number Systems", "Polynomials", "Coordinate Geometry", "Linear Equations in Two Variables", "Introduction to Euclid's Geometry", "Lines and Angles", "Triangles", "Quadrilaterals", "Areas of Parallelograms and Triangles", "Circles", "Constructions", "Heron's Formula", "Surface Areas and Volumes", "Statistics", "Probability"],
                10: ["Real Numbers", "Polynomials", "Pair of Linear Equations in Two Variables", "Quadratic Equations", "Arithmetic Progressions", "Triangles", "Coordinate Geometry", "Introduction to Trigonometry", "Some Applications of Trigonometry", "Circles", "Constructions", "Areas Related to Circles", "Surface Areas and Volumes", "Statistics", "Probability"],
                11: ["Sets", "Relations and Functions", "Trigonometric Functions", "Principle of Mathematical Induction", "Complex Numbers and Quadratic Equations", "Linear Inequalities", "Permutations and Combinations", "Binomial Theorem", "Sequences and Series", "Straight Lines", "Conic Sections", "Introduction to Three Dimensional Geometry", "Limits and Derivatives", "Mathematical Reasoning", "Statistics", "Probability"],
                12: ["Relations and Functions", "Inverse Trigonometric Functions", "Matrices", "Determinants", "Continuity and Differentiability", "Applications of Derivatives", "Integrals", "Applications of Integrals", "Differential Equations", "Vector Algebra", "Three Dimensional Geometry", "Linear Programming", "Probability"]
            },
            "Science": {
                1: ["My Body", "Living and Non-Living", "Plants Around Us", "Animals Around Us", "Food", "Water", "My Family"],
                2: ["Living and Non-Living", "Plants", "Animals", "Food", "Water", "Air", "Weather", "My Body", "Safety and First Aid"],
                3: ["Living and Non-Living", "Plants", "Animals", "My Body", "Food", "Housing and Clothing", "Transport and Communication"],
                4: ["Food", "Clothing", "Housing", "Water", "Travel and Transport", "The World of Plants", "The World of Animals", "Birds"],
                5: ["Food and Health", "Clothing", "Housing", "Water", "Travel and Transport", "Plants", "Animals", "Birds", "Our Environment"],
                6: ["Food", "Components of Food", "Fibre to Fabric", "Sorting Materials into Groups", "Separation of Substances", "Changes Around Us", "Getting to Know Plants", "Body Movements", "The Living Organisms", "Motion and Measurement of Distances", "Light, Shadows and Reflections", "Electricity and Circuits", "Fun with Magnets", "Water", "Air Around Us", "Garbage In, Garbage Out"],
                7: ["Nutrition in Plants", "Nutrition in Animals", "Fibre to Fabric", "Heat", "Acids, Bases and Salts", "Physical and Chemical Changes", "Weather, Climate and Adaptations", "Winds, Storms and Cyclones", "Soil", "Respiration in Organisms", "Transportation in Animals and Plants", "Reproduction in Plants", "Motion and Time", "Electric Current and its Effects", "Light", "Water", "Forests", "Wastewater Story"],
                8: ["Crop Production and Management", "Microorganisms", "Synthetic Fibres and Plastics", "Materials", "Coal and Petroleum", "Combustion and Flame", "Conservation of Plants and Animals", "Cell", "Reproduction in Animals", "Reaching the Age of Adolescence", "Force and Pressure", "Friction", "Sound", "Chemical Effects of Electric Current", "Some Natural Phenomena", "Light", "Stars and the Solar System", "Pollution of Air and Water"],
                9: ["Matter in Our Surroundings", "Is Matter Around Us Pure", "Atoms and Molecules", "Structure of the Atom", "The Fundamental Unit of Life", "Tissues", "Diversity in Living Organisms", "Motion", "Force and Laws of Motion", "Gravitation", "Work and Energy", "Sound", "Why Do We Fall Ill", "Natural Resources", "Improvement in Food Resources"],
                10: ["Chemical Reactions and Equations", "Acids, Bases and Salts", "Metals and Non-metals", "Carbon and its Compounds", "Periodic Classification of Elements", "Life Processes", "Control and Coordination", "How do Organisms Reproduce", "Heredity and Evolution", "Light", "Electricity", "Magnetic Effects of Electric Current", "Our Environment", "Management of Natural Resources"]
            },
            "Physical & Health Education": {
                8: [
                    # Key Concepts
                    "Change", "Communication", "Relationships",
                    
                    # Physical Fitness & Training
                    "Components of Fitness", "Cardiovascular Endurance", "Muscular Strength", "Muscular Endurance", 
                    "Flexibility", "Body Composition", "Training Principles", "Specificity Principle", 
                    "Progressive Overload", "Reversibility Principle", "Training Methods", "Periodization",
                    "Exercise Physiology", "Heart Rate Zones", "Fitness Testing", "VO2 Max",
                    
                    # Health & Nutrition
                    "Balanced Nutrition", "Macronutrients", "Micronutrients", "Hydration Strategies", 
                    "Pre-exercise Nutrition", "Post-exercise Recovery", "Sports Nutrition", 
                    "Healthy Lifestyle Choices", "Sleep and Recovery", "Stress Management",
                    "Mental Health and Physical Activity", "Body Image", "Adolescent Health",
                    
                    # Movement & Skills
                    "Fundamental Movement Skills", "Locomotor Skills", "Non-locomotor Skills", "Manipulative Skills",
                    "Aesthetic Movement", "Gymnastics", "Dance", "Martial Arts", "Yoga", "Rhythmic Activities",
                    "Team Sports", "Football", "Basketball", "Volleyball", "Hockey", "Cricket",
                    "Individual Sports", "Athletics", "Swimming", "Track and Field", "Tennis", "Badminton",
                    "Biomechanics", "Movement Analysis", "Technique Development", "Motor Learning",
                    
                    # Safety & First Aid
                    "Safety in Physical Activity", "Risk Assessment", "Injury Prevention", "Warm-up", "Cool-down",
                    "Basic First Aid", "RICE Protocol", "Emergency Procedures", "Sports Injuries",
                    "Equipment Safety", "Environmental Safety", "Heat-related Illness", "Concussion Awareness",
                    
                    # Communication in Sports
                    "Team Communication", "Verbal Communication", "Non-verbal Communication", 
                    "Coach-Athlete Communication", "Referee Communication", "Leadership in Sports",
                    "Conflict Resolution", "Sportsmanship", "Fair Play", "Respect in Sports",
                    
                    # Related Concepts
                    "Adaptation", "Balance", "Energy", "Function", "Interaction", "Perspective", 
                    "Space", "Systems", "Performance", "Environment", "Culture", "Identity"
                ]
            }
        },
        
        "IB": {
            "Mathematics": {
                1: ["Number Recognition", "Counting", "Shapes", "Patterns", "Sorting", "Size Comparison"],
                2: ["Numbers to 100", "Addition", "Subtraction", "Shapes", "Measurement", "Data Collection"],
                3: ["Numbers to 1000", "Operations", "Fractions", "Geometry", "Measurement", "Graphs"],
                4: ["Large Numbers", "Decimals", "Fractions", "Geometry", "Data Analysis", "Probability"],
                5: ["Number Theory", "Operations", "Geometry", "Statistics", "Algebra Basics", "Problem Solving"],
                6: ["Number", "Algebra", "Geometry", "Statistics", "Probability", "Mathematical Investigations"],
                7: ["Number", "Algebra", "Geometry", "Statistics", "Probability", "Mathematical Investigations"],
                8: ["Number", "Algebra", "Geometry", "Statistics", "Probability", "Mathematical Investigations"],
                9: ["Number", "Algebra", "Geometry and Trigonometry", "Statistics and Probability", "Mathematical Investigations"],
                10: ["Number", "Algebra", "Geometry and Trigonometry", "Statistics and Probability", "Mathematical Investigations"],
                11: ["Number and Algebra", "Functions", "Geometry and Trigonometry", "Statistics and Probability", "Calculus"],
                12: ["Number and Algebra", "Functions", "Geometry and Trigonometry", "Statistics and Probability", "Calculus"]
            },
            "Physical & Health Education": {
                8: [
                    # MYP Key Concepts
                    "Change", "Communication", "Relationships",
                    
                    # Global Contexts
                    "Personal and Cultural Expression", "Identities and Relationships", 
                    "Scientific and Technical Innovation", "Globalization and Sustainability",
                    
                    # Related Concepts
                    "Adaptation", "Balance", "Energy", "Function", "Interaction", "Perspective", 
                    "Space", "Systems", "Performance", "Environment", "Culture", "Identity",
                    
                    # Physical Fitness
                    "Components of Fitness", "Health-related Fitness", "Skill-related Fitness",
                    "Cardiovascular Endurance", "Muscular Strength", "Muscular Endurance", 
                    "Flexibility", "Body Composition", "Power", "Speed", "Agility", "Balance", "Coordination",
                    
                    # Training and Exercise Science
                    "Training Principles", "FITT Principle", "Progressive Overload", "Specificity",
                    "Reversibility", "Individual Differences", "Training Methods", "Interval Training",
                    "Circuit Training", "Continuous Training", "Plyometric Training", "Strength Training",
                    "Exercise Physiology", "Energy Systems", "Aerobic System", "Anaerobic Systems",
                    "Heart Rate", "VO2 Max", "Lactate Threshold", "Recovery",
                    
                    # Nutrition and Health
                    "Sports Nutrition", "Macronutrients", "Carbohydrates", "Proteins", "Fats",
                    "Micronutrients", "Vitamins", "Minerals", "Hydration", "Pre-exercise Nutrition",
                    "During-exercise Nutrition", "Post-exercise Nutrition", "Supplements",
                    "Healthy Eating", "Balanced Diet", "Weight Management", "Body Image",
                    
                    # Movement and Skills
                    "Fundamental Movement Skills", "Locomotor Skills", "Stability Skills", "Manipulative Skills",
                    "Motor Learning", "Skill Acquisition", "Practice Methods", "Feedback",
                    "Movement Patterns", "Technique Development", "Performance Analysis",
                    
                    # Aesthetic Movement
                    "Dance", "Gymnastics", "Martial Arts", "Yoga", "Pilates", "Aerobics",
                    "Creative Movement", "Cultural Dance", "Modern Dance", "Traditional Games",
                    
                    # Team Sports
                    "Football", "Basketball", "Volleyball", "Hockey", "Rugby", "Cricket",
                    "Team Tactics", "Team Strategies", "Roles and Responsibilities", "Team Dynamics",
                    "Leadership", "Cooperation", "Communication in Team Sports",
                    
                    # Individual Sports
                    "Athletics", "Swimming", "Tennis", "Badminton", "Golf", "Track and Field",
                    "Individual Performance", "Goal Setting", "Self-motivation", "Mental Preparation",
                    
                    # Biomechanics
                    "Movement Analysis", "Force", "Motion", "Levers", "Projectile Motion",
                    "Center of Gravity", "Balance", "Stability", "Efficiency of Movement",
                    
                    # Psychology of Sport
                    "Motivation", "Goal Setting", "Confidence", "Anxiety Management", "Concentration",
                    "Mental Training", "Visualization", "Relaxation Techniques", "Self-talk",
                    "Flow State", "Stress and Performance", "Team Cohesion", "Leadership Styles",
                    
                    # Health and Safety
                    "Risk Management", "Injury Prevention", "First Aid", "RICE Protocol",
                    "Safety Guidelines", "Equipment Safety", "Environmental Considerations",
                    "Heat Illness", "Concussion", "Overuse Injuries", "Acute Injuries",
                    
                    # Global Health Issues
                    "Physical Inactivity", "Obesity", "Non-communicable Diseases", "Mental Health",
                    "Health Promotion", "Public Health", "Health Education", "Lifestyle Diseases",
                    
                    # Cultural and Social Aspects
                    "Sport and Culture", "Gender in Sport", "Inclusion and Diversity", "Disability Sport",
                    "Fair Play", "Ethics in Sport", "Sportsmanship", "Respect", "Responsibility",
                    "International Sport", "Olympic Movement", "Paralympic Movement",
                    
                    # Communication in Physical Activity
                    "Verbal Communication", "Non-verbal Communication", "Body Language",
                    "Coaching Communication", "Referee Signals", "Team Communication",
                    "Feedback", "Instructions", "Encouragement", "Conflict Resolution",
                    
                    # Technology in Sport
                    "Performance Analysis", "Video Analysis", "Heart Rate Monitors", "GPS Tracking",
                    "Biomechanical Analysis", "Sports Apps", "Wearable Technology", "Data Collection",
                    
                    # ATL Skills in PHE
                    "Thinking Skills", "Research Skills", "Communication Skills", "Social Skills",
                    "Self-management Skills", "Critical Thinking", "Creative Thinking",
                    "Collaboration", "Organization", "Time Management"
                ]
            }
        },
        
        # Continue with other boards...
        "ICSE": {
            "Mathematics": {
                1: ["Numbers 1-100", "Addition", "Subtraction", "Shapes", "Patterns", "Money", "Time", "Measurement"],
                2: ["Numbers 1-100", "Place Value", "Addition", "Subtraction", "Multiplication", "Shapes", "Patterns", "Money", "Time", "Measurement"],
                3: ["Numbers 1-1000", "Four Operations", "Fractions", "Shapes", "Measurement", "Money", "Time", "Data"],
                4: ["Numbers", "Four Operations", "Factors and Multiples", "Fractions", "Decimals", "Geometry", "Measurement", "Data"],
                5: ["Large Numbers", "Four Operations", "Fractions", "Decimals", "Percentage", "Geometry", "Measurement", "Data"],
                6: ["Number System", "Integers", "Fractions", "Decimals", "Percentage", "Ratio and Proportion", "Unitary Method", "Simple Interest", "Basic Algebra", "Geometry", "Mensuration", "Data Handling"],
                7: ["Integers", "Rational Numbers", "Exponents", "Algebraic Expressions", "Simple Linear Equations", "Ratio and Proportion", "Unitary Method", "Percentage", "Profit and Loss", "Simple Interest", "Compound Interest", "Lines and Angles", "Triangles", "Symmetry", "Mensuration", "Data Handling"],
                8: ["Rational Numbers", "Exponents", "Squares and Square Roots", "Cubes and Cube Roots", "Playing with Numbers", "Algebraic Expressions and Identities", "Factorisation", "Linear Equations", "Understanding Quadrilaterals", "Practical Geometry", "Mensuration", "Data Handling", "Probability"],
                9: ["Rational and Irrational Numbers", "Compound Interest", "Expansions", "Factorisation", "Simultaneous Linear Equations", "Indices", "Logarithms", "Triangles", "Mean and Median", "Rectilinear Figures", "Theorem on Area", "Coordinate Geometry", "Trigonometry", "Statistics", "Probability"],
                10: ["Commercial Mathematics", "Sales Tax and Value Added Tax", "Banking", "Linear Inequations", "Quadratic Equations", "Ratio and Proportion", "Similarity", "Loci", "Circles", "Constructions", "Mensuration", "Trigonometry", "Coordinate Geometry", "Statistics", "Probability"]
            },
            "Physics": {
                6: ["Matter", "Physical Quantities and Measurement", "Force and Pressure", "Energy", "Light", "Sound", "Heat", "Magnetism"],
                7: ["Matter", "Physical Quantities and Measurement", "Motion", "Energy", "Light", "Sound", "Heat", "Electricity", "Magnetism"],
                8: ["Matter", "Force and Pressure", "Energy", "Light", "Sound", "Heat", "Electricity", "Magnetism"],
                9: ["Measurements and Experimentation", "Motion in One Dimension", "Force and Laws of Motion", "Turning Effect of Forces", "Pressure in Fluids and Atmospheric Pressure", "Upthrust in Fluids, Archimedes' Principle and Floatation", "Heat and Energy", "Reflection of Light", "Propagation of Sound Waves", "Current Electricity", "Magnetism"],
                10: ["Force", "Work, Energy and Power", "Machines", "Sound", "Light", "Spectrum", "Electromagnetic Induction", "Electromagnetic Radiation", "The Electron", "Atomic Structure", "Radioactivity"]
            },
            "Chemistry": {
                6: ["Matter", "Elements, Compounds and Mixtures", "Separation of Mixtures", "Atomic Structure", "Language of Chemistry", "Metals and Non-metals"],
                7: ["Matter", "Elements, Compounds and Mixtures", "Atomic Structure", "Language of Chemistry", "Chemical Reactions", "Acids, Bases and Salts", "Air and Atmosphere"],
                8: ["Matter", "Atomic Structure", "Language of Chemistry", "Chemical Reactions", "Acids, Bases and Salts", "Hydrogen", "Water", "Carbon and its Compounds"],
                9: ["The Language of Chemistry", "Chemical Changes and Reactions", "Water", "Atomic Structure and Chemical Bonding", "The Periodic Table", "Study of Gas Laws", "Atmospheric Pollution", "Sulphur", "Sound"],
                10: ["Periodic Properties and Variations", "Chemical Bonding", "Study of Acids, Bases and Salts", "Analytical Chemistry", "Mole Concept and Stoichiometry", "Electrolysis", "Metallurgy", "Study of Compounds", "Organic Chemistry", "Practical Chemistry"]
            },
            "Biology": {
                6: ["The Leaf", "Photosynthesis", "The Root", "The Stem", "The Flower", "Pollination and Fertilisation", "Seeds and their Germination", "Respiration in Plants", "Excretion in Plants", "The Cell", "Simple Tissues in Plants", "Absorption and Conduction in Plants"],
                7: ["Nutrition in Plants", "Nutrition in Animals", "Transportation in Living Organisms", "Respiration", "Excretion", "Nervous System", "Reproductive System", "Health and Hygiene", "Classification"],
                8: ["Transportation in Plants", "Transportation in Animals", "Excretion", "Reproduction", "Ecosystem", "Pollution"],
                9: ["Plant and Animal Tissues", "The Flower", "Pollination and Fertilisation", "Seeds", "Respiration in Plants", "Transpiration", "Excretion in Plants and Animals", "Circulation", "The Nervous System and Sense Organs", "The Respiratory System", "The Excretory System", "Reproduction in Plants", "Reproduction in Animals"],
                10: ["Photosynthesis", "Respiration", "Circulatory System", "Excretory System", "Nervous System", "Sense Organs", "Reproductive System", "Genetics", "Pollution", "Population"]
            }
        },
        
        "Cambridge IGCSE": {
            "Mathematics": {
                9: ["Number", "Algebra", "Geometry", "Mensuration", "Coordinate Geometry", "Trigonometry", "Matrices and Transformations", "Probability", "Statistics"],
                10: ["Number", "Algebra", "Geometry", "Mensuration", "Coordinate Geometry", "Trigonometry", "Matrices and Transformations", "Probability", "Statistics"],
                11: ["Pure Mathematics", "Mechanics", "Probability and Statistics"],
                12: ["Pure Mathematics", "Mechanics", "Probability and Statistics"]
            },
            "Physics": {
                9: ["General Physics", "Thermal Physics", "Properties of Waves", "Electricity and Magnetism", "Atomic Physics"],
                10: ["General Physics", "Thermal Physics", "Properties of Waves", "Electricity and Magnetism", "Atomic Physics"],
                11: ["Mechanics", "Gravitational Fields", "Deformation of Solids", "Waves", "Electricity", "Electromagnetic Fields", "Atomic and Nuclear Physics"],
                12: ["Mechanics", "Gravitational Fields", "Deformation of Solids", "Waves", "Electricity", "Electromagnetic Fields", "Atomic and Nuclear Physics"]
            },
            "Chemistry": {
                9: ["The Particulate Nature of Matter", "Experimental Techniques", "Atoms, Elements and Compounds", "Stoichiometry", "Electricity and Chemistry", "Chemical Energetics", "Chemical Reactions", "Acids, Bases and Salts", "The Periodic Table", "Metals", "Air and Water", "Sulfur", "Carbonates"],
                10: ["The Particulate Nature of Matter", "Experimental Techniques", "Atoms, Elements and Compounds", "Stoichiometry", "Electricity and Chemistry", "Chemical Energetics", "Chemical Reactions", "Acids, Bases and Salts", "The Periodic Table", "Metals", "Air and Water", "Sulfur", "Carbonates"],
                11: ["Atomic Structure", "Atoms, Molecules and Stoichiometry", "Chemical Bonding", "States of Matter", "Chemical Energetics", "Electrochemistry", "Equilibria", "Reaction Kinetics", "The Periodic Table", "Group Chemistry", "Introduction to Organic Chemistry", "Polymerisation"],
                12: ["Atomic Structure", "Atoms, Molecules and Stoichiometry", "Chemical Bonding", "States of Matter", "Chemical Energetics", "Electrochemistry", "Equilibria", "Reaction Kinetics", "The Periodic Table", "Group Chemistry", "Introduction to Organic Chemistry", "Polymerisation"]
            },
            "Biology": {
                9: ["Characteristics and Classification of Living Organisms", "Organisation and Maintenance of the Organism", "Movement into and out of Cells", "Biological Molecules", "Enzymes", "Plant Nutrition", "Human Nutrition", "Transport in Plants", "Transport in Animals", "Diseases and Immunity", "Gas Exchange", "Respiration", "Excretion", "Coordination and Response", "Drugs", "Reproduction", "Inheritance", "Variation and Selection", "Organisms and their Environment", "Biotechnology and Genetic Engineering", "Human Influences on Ecosystems"],
                10: ["Characteristics and Classification of Living Organisms", "Organisation and Maintenance of the Organism", "Movement into and out of Cells", "Biological Molecules", "Enzymes", "Plant Nutrition", "Human Nutrition", "Transport in Plants", "Transport in Animals", "Diseases and Immunity", "Gas Exchange", "Respiration", "Excretion", "Coordination and Response", "Drugs", "Reproduction", "Inheritance", "Variation and Selection", "Organisms and their Environment", "Biotechnology and Genetic Engineering", "Human Influences on Ecosystems"],
                11: ["Cell Structure", "Biological Molecules", "Enzymes", "Cell Membranes and Transport", "The Mitotic Cell Cycle", "Nucleic Acids and Protein Synthesis", "Transport in Plants", "Transport in Mammals", "Gas Exchange", "Infectious Diseases", "Immunity"],
                12: ["Cell Structure", "Biological Molecules", "Enzymes", "Cell Membranes and Transport", "The Mitotic Cell Cycle", "Nucleic Acids and Protein Synthesis", "Transport in Plants", "Transport in Mammals", "Gas Exchange", "Infectious Diseases", "Immunity"]
            }
        },
        
        "State Board": {
            "Mathematics": {
                1: ["Numbers 1-99", "Counting", "Shapes", "Patterns", "Addition", "Subtraction"],
                2: ["Numbers 1-100", "Addition", "Subtraction", "Multiplication", "Shapes", "Measurement"],
                3: ["Numbers 1-1000", "Four Operations", "Fractions", "Shapes", "Money", "Time"],
                4: ["Large Numbers", "Operations", "Fractions", "Decimals", "Geometry", "Measurement"],
                5: ["Numbers", "Operations", "Fractions", "Decimals", "Geometry", "Data"],
                6: ["Integers", "Fractions", "Decimals", "Basic Algebra", "Geometry", "Mensuration"],
                7: ["Integers", "Rational Numbers", "Algebra", "Geometry", "Mensuration", "Data"],
                8: ["Numbers", "Algebra", "Geometry", "Mensuration", "Statistics", "Graphs"],
                9: ["Real Numbers", "Polynomials", "Linear Equations", "Geometry", "Trigonometry", "Statistics"],
                10: ["Real Numbers", "Polynomials", "Quadratic Equations", "Geometry", "Trigonometry", "Statistics"],
                11: ["Sets and Functions", "Trigonometry", "Algebra", "Coordinate Geometry", "Calculus", "Statistics"],
                12: ["Relations and Functions", "Algebra", "Calculus", "Vectors", "Probability", "Linear Programming"]
            },
            "Science": {
                6: ["Food and its Components", "Separation of Substances", "Plants", "Animals", "Light", "Electricity", "Magnetism"],
                7: ["Nutrition", "Respiration", "Transportation", "Reproduction", "Motion", "Heat", "Sound"],
                8: ["Crop Production", "Microorganisms", "Force and Pressure", "Friction", "Sound", "Chemical Effects"],
                9: ["Matter", "Atoms and Molecules", "Tissues", "Motion", "Force", "Gravitation", "Work and Energy"],
                10: ["Chemical Reactions", "Acids and Bases", "Metals", "Life Processes", "Reproduction", "Heredity", "Light", "Electricity"]
            },
            "Social Science": {
                6: ["History of India", "Geography of India", "Civics", "Economics"],
                7: ["Medieval History", "Geography", "Civics", "Economics"],
                8: ["Modern History", "Geography", "Civics", "Economics"],
                9: ["World History", "Contemporary India", "Democratic Politics", "Economics"],
                10: ["History", "Geography", "Political Science", "Economics"]
            }
        }
    }

def test_claude_api():
    """Test Claude API connection with better error handling"""
    try:
        if not CLAUDE_API_KEY or CLAUDE_API_KEY == "REPLACE_WITH_YOUR_API_KEY":
            return False, "API key not configured"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Test"}]
        }
        
        response = requests.post(CLAUDE_API_URL, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return True, "API connection successful"
        elif response.status_code == 401:
            return False, f"API Authentication failed - check your API key"
        elif response.status_code == 429:
            return False, f"API rate limit exceeded - try again later"
        else:
            try:
                error_detail = response.json()
                return False, f"API Error {response.status_code}: {error_detail.get('error', {}).get('message', 'Unknown error')}"
            except:
                return False, f"API Error: {response.status_code}"
            
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def verify_api_key():
    """Verify API key with details"""
    st.write("🔍 **API Key Verification:**")
    
    if not CLAUDE_API_KEY or CLAUDE_API_KEY == "REPLACE_WITH_YOUR_API_KEY":
        st.error("❌ API key not configured")
        return False
    
    if not CLAUDE_API_KEY.startswith("sk-ant-api03-"):
        st.error("❌ Invalid API key format")
        return False
    
    st.success("✅ API key format is correct")
    
    # Test connection
    working, message = test_claude_api()
    if working:
        st.success(f"✅ {message}")
    else:
        st.error(f"❌ {message}")
    
    return working

def get_topics_by_board_grade_subject(board, grade, subject):
    """NEW FUNCTION: Get specific topics for board, grade, and subject"""
    curriculum_topics = get_comprehensive_curriculum_topics()
    
    # Handle IB grade format
    if board == "IB" and isinstance(grade, str) and "Grade" in grade:
        try:
            grade_num = int(grade.split()[1])
        except (IndexError, ValueError):
            return []
    else:
        grade_num = grade if isinstance(grade, int) else grade
    
    # Get topics from curriculum database
    board_data = curriculum_topics.get(board, {})
    subject_data = board_data.get(subject, {})
    topics = subject_data.get(grade_num, [])
    
    return topics

def validate_topic_against_curriculum(board, grade, subject, topic):
    """ENHANCED FUNCTION: Validate topic against specific curriculum"""
    if not topic:
        return False, []
    
    # Get curriculum topics for this specific combination
    curriculum_topics = get_topics_by_board_grade_subject(board, grade, subject)
    
    if not curriculum_topics:
        # Fallback to keyword matching if no specific curriculum found
        return check_topic_relevance(topic, subject)
    
    topic_clean = str(topic).lower().strip()
    
    # Check for exact or partial matches in curriculum topics
    matched_topics = []
    for curriculum_topic in curriculum_topics:
        curriculum_topic_clean = str(curriculum_topic).lower()
        if (curriculum_topic_clean in topic_clean or 
            topic_clean in curriculum_topic_clean or
            any(word in curriculum_topic_clean for word in topic_clean.split() if len(word) > 2)):
            matched_topics.append(curriculum_topic)
    
    is_valid = len(matched_topics) > 0
    return is_valid, curriculum_topics

def clean_json_response(response_text):
    """Enhanced JSON cleaning function to handle Claude's response format"""
    try:
        # Remove any markdown code blocks
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            if end != -1:
                response_text = response_text[start:end]
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            if end != -1:
                response_text = response_text[start:end]
        
        # Clean up the text
        response_text = response_text.strip()
        
        # Remove any leading/trailing non-JSON content
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx + 1]
        
        # Try to parse the JSON
        parsed_json = json.loads(response_text)
        return parsed_json, None
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON Parse Error at position {e.pos}: {e.msg}"
        return None, error_msg
    except Exception as e:
        return None, f"Error cleaning JSON: {str(e)}"

def generate_questions(board, grade, subject, topic, paper_type, include_answers_on_screen):
    """FIXED: Generate board-specific, grade-specific questions using Claude AI with enhanced error handling"""
    
    # Enhanced question count logic based on all board paper types
    mcq_count = 0
    short_count = 0
    long_count = 0
    
    # Primary Grades (1-5) for all boards
    if "Primary Assessment" in paper_type or "Foundation Test" in paper_type or "State Pattern Test" in paper_type:
        mcq_count = 15
        short_count = 5
    elif "Activity" in paper_type or "Skills" in paper_type:
        mcq_count = 0
        short_count = 15
    elif "Oral Assessment" in paper_type:
        mcq_count = 0
        short_count = 10
    
    # Middle Grades (6-8) for all boards
    elif "Periodic Test" in paper_type or "Class Test" in paper_type or "State Board Format" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Unit Test" in paper_type or "Term Examination" in paper_type or "Quarterly Test" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Annual Practice" in paper_type or "Annual Assessment" in paper_type or "Half-yearly Pattern" in paper_type:
        mcq_count = 25
        short_count = 15
    
    # High School Grades (9-10) for all boards
    elif "Board Pattern Paper 1" in paper_type or "ICSE Board Format Paper 1" in paper_type or "State Board Paper 1" in paper_type:
        mcq_count = 25
        short_count = 15
    elif "Board Pattern Paper 2" in paper_type or "ICSE Board Format Paper 2" in paper_type or "State Board Paper 2" in paper_type:
        mcq_count = 0
        short_count = 10
        long_count = 10
    elif "Sample Paper Format" in paper_type or "Mock ICSE Paper" in paper_type or "Annual Exam Pattern" in paper_type:
        mcq_count = 25
        short_count = 10
        long_count = 5
    
    # Senior Secondary (11-12) for all boards
    elif "Board Exam Pattern" in paper_type or "ISC Board Pattern" in paper_type or "HSC Board Pattern" in paper_type:
        mcq_count = 25
        short_count = 10
        long_count = 5
    elif "Practice Test Series" in paper_type or "Practice Assessment" in paper_type or "State Higher Secondary" in paper_type:
        mcq_count = 30
        short_count = 10
    elif "Mock Board Paper" in paper_type or "Mock ISC Paper" in paper_type or "Board Exam Format" in paper_type:
        mcq_count = 30
        short_count = 15
        long_count = 5
    
    # IB Specific Papers
    elif "Formative Assessment" in paper_type:
        mcq_count = 15
        short_count = 5
    elif "Skills Practice" in paper_type:
        mcq_count = 0
        short_count = 15
    elif "Inquiry Tasks" in paper_type:
        mcq_count = 0
        short_count = 25
    elif "Practice Assessment" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Criterion-Based Test" in paper_type:
        mcq_count = 15
        short_count = 10
    elif "Personal Project Prep" in paper_type:
        mcq_count = 0
        short_count = 15
    elif "MYP Certificate Practice" in paper_type:
        mcq_count = 30
        short_count = 10
    elif "Paper 1 (40 MCQs)" in paper_type:
        mcq_count = 40
        short_count = 0
    elif "Paper 2 (15 Short + 15 Long" in paper_type:
        mcq_count = 0
        short_count = 15
        long_count = 15
    elif "Paper 3 (Data Analysis" in paper_type:
        mcq_count = 15
        short_count = 10
    
    # Cambridge IGCSE Specific Papers
    elif "Cambridge Primary Test" in paper_type or "Lower Secondary Assessment" in paper_type:
        mcq_count = 15
        short_count = 10
    elif "Checkpoint Practice" in paper_type:
        mcq_count = 20
        short_count = 10
    elif "Paper 1 (30 MCQs)" in paper_type:
        mcq_count = 30
        short_count = 0
    elif "Paper 2 (Theory" in paper_type:
        mcq_count = 10
        short_count = 15
        long_count = 5
    elif "Paper 3 (Practical" in paper_type or "Paper 4 (Alternative" in paper_type:
        mcq_count = 15
        short_count = 10
    elif "A-Level AS Paper" in paper_type:
        mcq_count = 20
        short_count = 15
    elif "A-Level A2 Paper" in paper_type:
        mcq_count = 25
        short_count = 15
    elif "Cambridge Advanced Test" in paper_type:
        mcq_count = 30
        short_count = 15
    
    # Default fallback
    else:
        mcq_count = 20
        short_count = 10
    
    total_questions = mcq_count + short_count + long_count
    
    # Get curriculum topics for enhanced context
    curriculum_topics = get_topics_by_board_grade_subject(board, grade, subject)
    curriculum_context = ""
    if curriculum_topics:
        curriculum_context = f"\nCURRICULUM TOPICS for {board} Grade {grade} {subject}: {', '.join(curriculum_topics[:10])}"
    
    # Enhanced prompt with board and grade specific context
    board_context = get_board_specific_guidelines(board, grade, subject, topic)
    
    prompt = f"""Create a {board} Grade {grade} {subject} test on "{topic}" using {paper_type} format.

{board_context}
{curriculum_context}

Generate exactly:
- {mcq_count} multiple choice questions (if any)
- {short_count} short answer questions (if any)
- {long_count} long answer questions (if any)

IMPORTANT: All questions MUST be specifically about "{topic}" as taught in {board} Grade {grade} {subject} curriculum. Use examples, terminology, and difficulty level appropriate for {board} Grade {grade} students.

Question Types:
- MCQ: 4 options (A, B, C, D) with one correct answer
- Short Answer: 2-5 sentence responses
- Long Answer: Detailed explanations or essay-type responses

CRITICAL: Respond with ONLY valid JSON. No markdown, no extra text, no explanations - just pure JSON.

{{
    "test_info": {{
        "board": "{board}",
        "grade": "{grade}",
        "subject": "{subject}",
        "topic": "{topic}",
        "paper_type": "{paper_type}",
        "total_questions": {total_questions},
        "mcq_count": {mcq_count},
        "short_count": {short_count},
        "long_count": {long_count},
        "show_answers_on_screen": {str(include_answers_on_screen).lower()}
    }},
    "questions": [
        {{
            "question_number": 1,
            "type": "mcq",
            "question": "Sample MCQ question about {topic}?",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Brief explanation"
        }},
        {{
            "question_number": 2,
            "type": "short",
            "question": "Sample short answer question about {topic}?",
            "sample_answer": "Expected short answer",
            "marks": 3
        }},
        {{
            "question_number": 3,
            "type": "long",
            "question": "Sample long answer question about {topic}?",
            "sample_answer": "Expected detailed answer",
            "marks": 6
        }}
    ]
}}"""

    try:
        # Enhanced error handling and API validation
        if not CLAUDE_API_KEY or CLAUDE_API_KEY == "REPLACE_WITH_YOUR_API_KEY":
            st.error("❌ API key not configured. Please check your API configuration.")
            return None
        
        st.info("🔍 Connecting to Claude AI...")
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        st.info("📡 Sending request to Claude AI...")
        
        try:
            response = requests.post(CLAUDE_API_URL, headers=headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout. Please try again.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error. Please check your internet connection.")
            return None
        
        st.info(f"📥 Received response with status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if 'content' not in result or not result['content']:
                    st.error("❌ Invalid response format from Claude API")
                    return None
                
                content = result['content'][0]['text']
                st.info("🔧 Processing Claude's response...")
                
                # Enhanced JSON cleaning and parsing
                cleaned_json, error = clean_json_response(content)
                
                if cleaned_json is None:
                    st.error(f"❌ {error}")
                    st.error("📝 Raw response for debugging:")
                    st.code(content[:500] + "..." if len(content) > 500 else content)
                    return None
                
                # Validate the JSON structure
                if 'test_info' not in cleaned_json or 'questions' not in cleaned_json:
                    st.error("❌ Invalid test data structure")
                    return None
                
                # Ensure test_info has required fields
                if 'test_info' in cleaned_json:
                    cleaned_json['test_info']['show_answers_on_screen'] = include_answers_on_screen
                    cleaned_json['test_info']['curriculum_standard'] = f"{board} Grade {grade} {subject}"
                
                st.success("✅ Test generated successfully!")
                return cleaned_json
                
            except json.JSONDecodeError as e:
                st.error(f"❌ JSON Parse Error: {str(e)}")
                st.error("📝 Raw response for debugging:")
                result = response.json()
                content = result['content'][0]['text'] if 'content' in result else str(result)
                st.code(content[:500] + "..." if len(content) > 500 else content)
                return None
            except Exception as e:
                st.error(f"❌ Error processing response: {str(e)}")
                return None
            
        elif response.status_code == 401:
            st.error("❌ API Authentication failed. Please check your API key.")
            return None
        elif response.status_code == 429:
            st.error("❌ API rate limit exceeded. Please try again later.")
            return None
        elif response.status_code == 400:
            try:
                error_detail = response.json()
                st.error(f"❌ API Request Error: {error_detail.get('error', {}).get('message', 'Bad request')}")
            except:
                st.error("❌ Bad request to API")
            return None
        else:
            try:
                error_detail = response.json()
                error_msg = error_detail.get('error', {}).get('message', 'Unknown error')
                st.error(f"❌ API Error {response.status_code}: {error_msg}")
            except:
                st.error(f"❌ API Error: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def get_comprehensive_subject_keywords():
    """MASSIVE enhanced keywords database for all subjects across all boards with thousands of topics"""
    return {
        "Mathematics": [
            # Basic Mathematics (Grades 1-5)
            "number", "numbers", "counting", "addition", "subtraction", "multiplication", "division", 
            "place value", "tens", "hundreds", "thousands", "digit", "digits", "even", "odd",
            "pattern", "patterns", "shapes", "triangle", "square", "rectangle", "circle",
            "measurement", "length", "weight", "time", "money", "coins", "notes",
            
            # Intermediate Mathematics (Grades 6-8)  
            "fraction", "fractions", "decimal", "decimals", "percentage", "percentages", 
            "ratio", "ratios", "proportion", "proportions", "algebra", "equation", "equations",
            "variable", "variables", "expression", "expressions", "coefficient", "coefficients",
            "geometry", "angle", "angles", "parallel", "perpendicular", "area", "perimeter",
            "volume", "surface area", "coordinate", "coordinates", "graph", "graphs",
            "integer", "integers", "positive", "negative", "absolute value",
            
            # Advanced Mathematics (Grades 9-12)
            "quadratic", "polynomial", "polynomials", "function", "functions", "domain", "range",
            "linear", "slope", "intercept", "simultaneous", "inequality", "inequalities",
            "trigonometry", "sine", "cosine", "tangent", "theorem", "theorems", "proof", "proofs",
            "calculus", "derivative", "derivatives", "integral", "integrals", "limit", "limits",
            "statistics", "probability", "mean", "median", "mode", "standard deviation",
            "matrix", "matrices", "determinant", "determinants", "vector", "vectors",
            "logarithm", "logarithms", "exponential", "complex numbers", "binomial"
        ],
        
        "Science": [
            # General Science Topics
            "matter", "states of matter", "solid", "liquid", "gas", "plasma", "energy", "kinetic", "potential",
            "force", "forces", "motion", "speed", "velocity", "acceleration", "gravity", "friction",
            "pressure", "temperature", "heat", "light", "sound", "electricity", "magnetism",
            "wave", "waves", "frequency", "amplitude", "wavelength", "radiation",
            
            # Physics Topics
            "mechanics", "dynamics", "kinematics", "momentum", "work", "power", "machine", "machines",
            "lever", "pulley", "inclined plane", "simple machine", "compound machine",
            "thermodynamics", "optics", "reflection", "refraction", "lens", "mirror",
            "current", "voltage", "resistance", "circuit", "ohm's law", "electromagnetic",
            "atomic", "nuclear", "radioactivity", "quantum", "relativity",
            
            # Chemistry Topics  
            "atom", "atoms", "molecule", "molecules", "element", "elements", "compound", "compounds",
            "mixture", "mixtures", "solution", "solutions", "acid", "acids", "base", "bases",
            "salt", "salts", "pH", "indicator", "indicators", "reaction", "reactions",
            "chemical", "physical", "change", "changes", "catalyst", "catalysts",
            "periodic table", "metals", "non-metals", "metalloids", "ion", "ions",
            "bond", "bonds", "ionic", "covalent", "molecular", "crystalline",
            "oxidation", "reduction", "combustion", "corrosion", "electrolysis",
            
            # Biology Topics
            "cell", "cells", "tissue", "tissues", "organ", "organs", "system", "systems",
            "organism", "organisms", "life", "living", "non-living", "characteristics",
            "nutrition", "respiration", "excretion", "growth", "reproduction", "movement",
            "photosynthesis", "chlorophyll", "stomata", "transpiration", "digestion",
            "circulation", "blood", "heart", "lungs", "kidney", "brain", "nervous",
            "skeleton", "muscle", "muscles", "bone", "bones", "joint", "joints",
            "genetics", "heredity", "DNA", "RNA", "chromosome", "gene", "genes",
            "evolution", "adaptation", "natural selection", "species", "classification",
            "bacteria", "virus", "viruses", "fungi", "algae", "protozoa",
            "ecosystem", "environment", "food chain", "food web", "habitat", "biodiversity"
        ],
        
        "Physical & Health Education": [
            # Physical Fitness
            "fitness", "physical fitness", "exercise", "workout", "training", "conditioning",
            "cardiovascular", "endurance", "strength", "muscular strength", "flexibility", "agility",
            "balance", "coordination", "speed", "power", "body composition", "aerobic", "anaerobic",
            
            # Health and Nutrition
            "health", "nutrition", "diet", "balanced diet", "nutrients", "vitamins", "minerals",
            "proteins", "carbohydrates", "fats", "calories", "hydration", "water intake",
            "healthy lifestyle", "wellness", "mental health", "stress management",
            
            # Sports and Games
            "sports", "games", "team sports", "individual sports", "athletics", "track and field",
            "swimming", "gymnastics", "basketball", "football", "volleyball", "cricket", "tennis",
            "badminton", "table tennis", "hockey", "soccer", "running", "jumping", "throwing",
            
            # Movement and Skills
            "movement", "motor skills", "locomotor", "non-locomotor", "manipulative skills",
            "fundamental movement", "gross motor", "fine motor", "coordination", "rhythm",
            "dance", "martial arts", "yoga", "stretching", "warm-up", "cool-down",
            
            # Safety and Rules
            "safety", "first aid", "injury prevention", "rules", "regulations", "fair play",
            "sportsmanship", "teamwork", "leadership", "communication", "cooperation"
        ],
        
        "Physics": [
            "mechanics", "motion", "kinematics", "dynamics", "force", "forces", "newton's laws",
            "momentum", "energy", "work", "power", "simple harmonic motion", "waves",
            "sound", "light", "optics", "reflection", "refraction", "interference", "diffraction",
            "electricity", "current", "voltage", "resistance", "capacitance", "inductance",
            "magnetism", "electromagnetic", "induction", "transformer", "motor", "generator",
            "thermodynamics", "heat", "temperature", "entropy", "gas laws", "kinetic theory",
            "atomic physics", "nuclear physics", "radioactivity", "quantum", "relativity",
            "semiconductor", "diode", "transistor", "amplifier", "oscillator", "digital"
        ],
        
        "Chemistry": [
            "atomic structure", "periodic table", "chemical bonding", "ionic", "covalent", "metallic",
            "molecular", "crystal", "lattice", "solutions", "acids", "bases", "salts", "pH",
            "redox", "oxidation", "reduction", "electrochemistry", "thermochemistry",
            "chemical kinetics", "equilibrium", "organic chemistry", "hydrocarbons", "alcohols",
            "aldehydes", "ketones", "carboxylic acids", "esters", "amines", "polymers",
            "inorganic chemistry", "coordination compounds", "metallurgy", "qualitative analysis",
            "quantitative analysis", "spectroscopy", "chromatography", "environmental chemistry"
        ],
        
        "Biology": [
            "cell biology", "cell division", "mitosis", "meiosis", "genetics", "mendel's laws",
            "inheritance", "DNA replication", "transcription", "translation", "mutation",
            "biotechnology", "genetic engineering", "cloning", "plant physiology", "photosynthesis",
            "respiration", "transpiration", "human physiology", "digestive system", "respiratory system",
            "circulatory system", "excretory system", "nervous system", "endocrine system",
            "reproductive system", "ecology", "ecosystem", "food chains", "biogeochemical cycles",
            "evolution", "natural selection", "speciation", "biodiversity", "conservation",
            "microbiology", "bacteria", "viruses", "fungi", "immunity", "diseases"
        ],
        
        "English": [
            # Grammar and Language
            "grammar", "noun", "pronoun", "verb", "adjective", "adverb", "preposition", "conjunction",
            "article", "tense", "past", "present", "future", "active", "passive", "voice",
            "sentence", "clause", "phrase", "subject", "predicate", "object", "complement",
            "direct", "indirect", "speech", "punctuation", "capitalization", "spelling",
            
            # Literature
            "literature", "poem", "poetry", "prose", "novel", "story", "short story", "drama",
            "play", "act", "scene", "character", "protagonist", "antagonist", "theme", "plot",
            "setting", "conflict", "climax", "resolution", "metaphor", "simile", "alliteration",
            "personification", "irony", "symbolism", "imagery", "rhyme", "rhythm", "meter",
            
            # Writing and Comprehension
            "essay", "paragraph", "introduction", "conclusion", "thesis", "argument", "persuasive",
            "narrative", "descriptive", "expository", "creative writing", "composition",
            "comprehension", "reading", "vocabulary", "synonyms", "antonyms", "homonyms",
            "prefix", "suffix", "root word", "context", "inference", "summary", "main idea"
        ],
        
        "Hindi": [
            # व्याकरण (Grammar)
            "व्याकरण", "संज्ञा", "सर्वनाम", "विशेषण", "क्रिया", "क्रिया विशेषण", "संबंधबोधक",
            "समुच्चयबोधक", "विस्मयादिबोधक", "वाक्य", "उद्देश्य", "विधेय", "कर्ता", "कर्म", "करण",
            "काल", "वर्तमान", "भूत", "भविष्य", "वचन", "एकवचन", "बहुवचन", "लिंग", "पुल्लिंग", "स्त्रीलिंग",
            "कारक", "संधि", "उपसर्ग", "प्रत्यय", "समास", "तत्पुरुष", "द्वंद", "बहुव्रीहि",
            
            # साहित्य (Literature)  
            "साहित्य", "कविता", "कहानी", "उपन्यास", "नाटक", "निबंध", "गद्य", "पद्य",
            "छंद", "अलंकार", "रस", "शृंगार", "वीर", "करुण", "हास्य", "रौद्र", "भयानक",
            "वीभत्स", "अद्भुत", "शांत", "वात्सल्य", "भक्ति", "यमक", "अनुप्रास", "उपमा", "रूपक",
            
            # लेखन (Writing)
            "लेखन", "अनुच्छेद", "निबंध", "पत्र", "औपचारिक", "अनौपचारिक", "आवेदन", "शिकायत",
            "सूचना", "विज्ञापन", "संवाद", "एकालाप", "वर्णन", "चित्र", "घटना", "यात्रा"
        ],
        
        "Social Science": [
            # History
            "history", "ancient", "medieval", "modern", "contemporary", "civilization", "indus valley",
            "harappan", "vedic", "mauryan", "gupta", "delhi sultanate", "mughal", "british",
            "independence", "freedom struggle", "mahatma gandhi", "nehru", "nationalism",
            "world war", "cold war", "renaissance", "industrial revolution", "french revolution",
            
            # Geography  
            "geography", "physical", "human", "economic", "political", "map", "globe", "latitude",
            "longitude", "equator", "prime meridian", "climate", "weather", "monsoon", "seasons",
            "continents", "oceans", "mountains", "rivers", "plateaus", "plains", "deserts",
            "forests", "agriculture", "irrigation", "crops", "industries", "transportation",
            "population", "migration", "urbanization", "resources", "mineral", "energy",
            
            # Civics/Political Science
            "civics", "government", "democracy", "constitution", "fundamental rights", "duties",
            "parliament", "lok sabha", "rajya sabha", "prime minister", "president", "judiciary",
            "supreme court", "high court", "federalism", "state", "union", "panchayati raj",
            "elections", "voting", "political parties", "local government", "administration",
            
            # Economics
            "economics", "demand", "supply", "market", "price", "money", "banking", "credit",
            "agriculture", "industry", "service sector", "employment", "unemployment", "poverty",
            "development", "human development", "globalization", "liberalization", "privatization"
        ],
        
        "Computer Science": [
            # Basic Computing
            "computer", "hardware", "software", "input", "output", "processing", "storage",
            "memory", "RAM", "ROM", "CPU", "ALU", "control unit", "motherboard", "keyboard",
            "mouse", "monitor", "printer", "scanner", "operating system", "windows", "linux",
            
            # Programming
            "programming", "algorithm", "flowchart", "pseudocode", "variable", "constant",
            "data type", "integer", "float", "string", "boolean", "array", "loop", "condition",
            "if", "else", "while", "for", "function", "procedure", "parameter", "return",
            "python", "java", "c++", "javascript", "html", "css", "sql", "database",
            
            # Advanced Topics
            "data structure", "stack", "queue", "linked list", "tree", "graph", "sorting",
            "searching", "object oriented", "class", "object", "inheritance", "polymorphism",
            "encapsulation", "network", "internet", "protocol", "tcp", "ip", "http", "ftp",
            "cybersecurity", "encryption", "firewall", "virus", "malware", "artificial intelligence",
            "machine learning", "cloud computing", "big data", "blockchain"
        ],
        
        "Economics": [
            "microeconomics", "macroeconomics", "demand", "supply", "elasticity", "utility",
            "production", "cost", "revenue", "profit", "market", "competition", "monopoly",
            "oligopoly", "consumer", "producer", "equilibrium", "price", "inflation", "deflation",
            "GDP", "GNP", "national income", "fiscal policy", "monetary policy", "taxation",
            "budget", "trade", "export", "import", "balance of payments", "exchange rate",
            "development", "growth", "poverty", "inequality", "unemployment", "employment"
        ],
        
        "EVS (Environmental Studies)": [
            # Environmental Studies
            "environment", "pollution", "air pollution", "water pollution", "noise pollution",
            "soil pollution", "conservation", "natural resources", "renewable", "non-renewable",
            "forest", "deforestation", "afforestation", "wildlife", "biodiversity", "extinction",
            "ecosystem", "food chain", "food web", "habitat", "adaptation", "climate change",
            "global warming", "greenhouse effect", "ozone layer", "acid rain", "waste management",
            "recycling", "reduce", "reuse", "sustainable development", "energy conservation"
        ],
        
        # Additional subjects for specific boards
        "Art & Craft": [
            "drawing", "painting", "sketching", "coloring", "craft", "handicraft", "sculpture",
            "pottery", "paper craft", "origami", "collage", "creative", "artistic", "design",
            "pattern", "texture", "color", "shape", "form", "composition", "perspective"
        ],
        
        "Business Studies": [
            "business", "enterprise", "entrepreneur", "management", "planning", "organizing",
            "directing", "controlling", "marketing", "production", "finance", "human resources",
            "accounting", "profit", "loss", "revenue", "capital", "partnership", "company",
            "cooperative", "sole proprietorship", "stock exchange", "shares", "debentures"
        ],
        
        "Accountancy": [
            "accounting", "bookkeeping", "journal", "ledger", "trial balance", "balance sheet",
            "profit and loss", "cash book", "bank reconciliation", "depreciation", "bad debts",
            "provisions", "reserves", "capital", "revenue", "assets", "liabilities", "equity",
            "partnership", "admission", "retirement", "dissolution", "company accounts"
        ]
    }

def check_topic_relevance(topic, subject):
    """Enhanced topic relevance checking with comprehensive curriculum matching"""
    if not topic or not subject:
        return True, []
    
    keywords_dict = get_comprehensive_subject_keywords()
    
    # Safe string operations
    topic_clean = str(topic).lower().strip()
    subject_keywords = keywords_dict.get(subject, [])
    
    # Check for direct matches or partial matches
    matches = False
    matched_keywords = []
    
    for keyword in subject_keywords:
        keyword_clean = str(keyword).lower()
        # Check if keyword is in topic or topic is in keyword (both ways)
        if keyword_clean in topic_clean or topic_clean in keyword_clean:
            matches = True
            matched_keywords.append(keyword)
    
    # Additional check for Science subject (covers Physics, Chemistry, Biology)
    if not matches and subject == "Science":
        for science_subject in ["Physics", "Chemistry", "Biology"]:
            if science_subject in keywords_dict:
                for keyword in keywords_dict[science_subject]:
                    keyword_clean = str(keyword).lower()
                    if keyword_clean in topic_clean or topic_clean in keyword_clean:
                        matches = True
                        matched_keywords.append(keyword)
                        break
                if matches:
                    break
    
    # Additional check for Social Science (covers History, Geography, Civics, Economics)
    if not matches and "Social Science" in subject:
        social_subjects = ["History", "Geography", "Civics", "Economics", "Political Science"]
        for social_subject in social_subjects:
            if social_subject in keywords_dict:
                for keyword in keywords_dict[social_subject]:
                    keyword_clean = str(keyword).lower()
                    if keyword_clean in topic_clean or topic_clean in keyword_clean:
                        matches = True
                        matched_keywords.append(keyword)
                        break
                if matches:
                    break
    
    return matches, subject_keywords

def get_available_subjects(board, grade):
    """Get available subjects for board and grade"""
    subjects_data = get_subjects_by_board()
    board_data = subjects_data.get(board, {})
    
    # For IB, extract numeric grade from string like "Grade 5 (PYP)"
    if board == "IB" and isinstance(grade, str):
        try:
            grade_num = int(grade.split()[1])
            return board_data.get(grade_num, [])
        except (IndexError, ValueError):
            return []
    
    return board_data.get(grade, [])

def create_questions_pdf(test_data, filename="questions.pdf"):
    """Create PDF with questions only"""
    if not PDF_AVAILABLE:
        st.error("PDF generation not available. Please install reportlab: pip install reportlab")
        return None
    
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # II Tuition Title style
        tuitions_title_style = ParagraphStyle(
            'TuitionsTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=10,
            alignment=1,  # Center
            textColor=colors.darkblue
        )
        
        test_info = test_data.get('test_info', {})
        questions = test_data.get('questions', [])
        
        # II Tuition Header
        story.append(Paragraph("🎓 II Tuition Mock Test Generated", tuitions_title_style))
        story.append(Paragraph(f"{test_info.get('subject', 'Subject')} Mock Test", tuitions_title_style))
        story.append(Paragraph(f"Board: {test_info.get('board', 'N/A')} | Grade: {test_info.get('grade', 'N/A')} | Topic: {test_info.get('topic', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Instructions
        story.append(Paragraph("Instructions:", styles['Heading2']))
        story.append(Paragraph("• Read all questions carefully", styles['Normal']))
        story.append(Paragraph("• Choose the best answer for multiple choice questions", styles['Normal']))
        story.append(Paragraph("• Write clearly for descriptive answers", styles['Normal']))
        story.append(Paragraph("• Manage your time effectively", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Questions
        for i, question in enumerate(questions, 1):
            story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question', '')}", styles['Normal']))
            
            if question.get('type') == 'mcq' and 'options' in question:
                options = question['options']
                for option_key, option_text in options.items():
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{option_key})</b> {option_text}", styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename
        
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def create_answers_pdf(test_data, filename="answers.pdf"):
    """Create PDF with answers only"""
    if not PDF_AVAILABLE:
        st.error("PDF generation not available. Please install reportlab: pip install reportlab")
        return None
    
    try:
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        test_info = test_data.get('test_info', {})
        questions = test_data.get('questions', [])
        
        # Header
        story.append(Paragraph("🎓 II Tuition Mock Test - Answer Key", styles['Heading1']))
        story.append(Paragraph(f"{test_info.get('subject', 'Subject')} Mock Test Answers", styles['Heading2']))
        story.append(Spacer(1, 20))
        
        # Answers
        for i, question in enumerate(questions, 1):
            story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question', '')}", styles['Normal']))
            
            # Show the correct answer
            if 'correct_answer' in question and question['correct_answer']:
                story.append(Paragraph(f"<b>Correct Answer:</b> {question['correct_answer']}", styles['Normal']))
            elif 'sample_answer' in question and question['sample_answer']:
                story.append(Paragraph(f"<b>Sample Answer:</b> {question['sample_answer']}", styles['Normal']))
            
            # Show explanation if available
            if 'explanation' in question and question['explanation']:
                story.append(Paragraph(f"<b>Explanation:</b> {question['explanation']}", styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename
        
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

def show_test_creator(navigate_to=None):
    """
    FIXED: Test creator page content for II Tuitions Mock Test Generator
    Fixed paper type selection UI spacing and JSON parse errors
    """
    
    # Page Header - Using centralized styling
    st.markdown('<h1 style="color: #2c3e50; text-align: center; font-size: 2.5rem; margin-bottom: 1rem;">🎯 Create Mock Test</h1>', unsafe_allow_html=True)
    
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
        if st.button("🔍 Test Claude API Connection", key="test_api_btn"):
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
        if st.button("📋 Detailed API Verification", key="verify_api_btn"):
            verify_api_key()
    
    st.markdown("---")
    
    # Step 1: Board Selection - Using centralized CSS classes
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
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
    else:
        board = ''
    
    # Step 2: Grade Selection - Dynamic based on board
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
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
            else:
                grade = 0
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
                except (ValueError, AttributeError):
                    grade = 0
            else:
                grade = 0
    else:
        st.selectbox(
            "Select your current academic grade (1-12)", 
            ["Please select Board first"], 
            disabled=True,
            key="grade_disabled"
        )
        grade = 0
    
    # Step 3: Subject Selection - Using centralized CSS classes
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">3</div>
        <div class="step-title">SELECT SUBJECT:</div>
    </div>
    """, unsafe_allow_html=True)
    
    if board and grade:
        available_subjects = get_available_subjects(board, grade)
        
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
    
    # Step 4: Topic Input with Enhanced Curriculum Validation
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">4</div>
        <div class="step-title">ENTER TOPIC:</div>
    </div>
    """, unsafe_allow_html=True)
    
    if subject:
        # Show curriculum topics for the selected combination
        curriculum_topics = get_topics_by_board_grade_subject(board, grade, subject)
        
        if curriculum_topics:
            st.info(f"📚 **{board} Grade {grade} {subject} Curriculum Topics:**")
            
            # Display topics in columns for better organization
            cols = st.columns(3)
            for i, topic in enumerate(curriculum_topics[:15]):  # Show first 15 topics
                with cols[i % 3]:
                    st.write(f"• {topic}")
            
            if len(curriculum_topics) > 15:
                st.info(f"📖 And {len(curriculum_topics) - 15} more topics in the curriculum...")
        
        topic_input = st.text_input(
            "Specify the exact topic or chapter you want to focus on", 
            placeholder=f"e.g., {', '.join(curriculum_topics[:3]) if curriculum_topics else 'Enter topic name'}", 
            key=f"topic_input_{subject}"
        )
        
        if topic_input:
            topic = topic_input.strip()
        else:
            topic = ''
    else:
        st.text_input(
            "Specify the exact topic or chapter you want to focus on", 
            placeholder="Please select a subject first", 
            disabled=True,
            key="topic_disabled"
        )
        topic = ''
    
    # Enhanced Topic validation with comprehensive database
    topic_valid = True
    
    if topic and subject and board and grade:
        # Use new curriculum validation function
        is_relevant, curriculum_topics = validate_topic_against_curriculum(board, grade, subject, topic)
        
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
    elif topic and not (subject and board and grade):
        st.warning("⚠️ Please select board, grade, and subject first to validate your topic")
        topic_valid = False
    
    # Validation Summary - Using centralized CSS classes
    st.markdown("""
    <div class="validation-box">
        <div class="validation-title">📋 VALIDATION SUMMARY</div>
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
        validation_results.append((f"✅ TOPIC: '{topic}' is Valid", "success"))
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
    
    # Step 5: Test Configuration - FIXED UI with proper spacing
    st.markdown("""
    <div class="step-box" style="height: 80px; max-height: 80px; overflow: hidden;">
        <div class="step-number">5</div>
        <div class="step-title">SELECT PAPER TYPE:</div>
    </div>
    """, unsafe_allow_html=True)
    
    if board and grade:
        # Get paper types based on board and grade
        paper_options = get_paper_types_by_board_and_grade(board, grade)
        
        if paper_options:
            st.markdown("### 📝 Choose your preferred paper format:")
            
            # FIXED: Better spacing for paper type selection
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                <h4 style="color: #495057; margin-bottom: 15px;">📋 Paper Type Options:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Create columns for better layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # FIXED: Add spacing between radio options
                paper_type = st.radio(
                    "Select paper format:",
                    paper_options,
                    key="paper_type_radio",
                    help="Choose the examination format that matches your requirements"
                )
            
            with col2:
                st.markdown("### ℹ️ Paper Details:")
                # Enhanced descriptions based on paper type
                if "40 MCQs" in paper_type:
                    st.info("📊 40 Multiple Choice Questions\n⏱️ Duration: 90-120 minutes")
                elif "30 MCQs" in paper_type:
                    st.info("📊 30 Multiple Choice Questions\n⏱️ Duration: 60-90 minutes")
                elif "25 MCQs" in paper_type or "25 MCQ" in paper_type:
                    st.info("📊 25 Multiple Choice Questions\n⏱️ Duration: 45-60 minutes")
                elif "20 Mixed" in paper_type:
                    st.info("📊 20 Mixed Questions (MCQ + Short)\n⏱️ Duration: 60-75 minutes")
                elif "15 Short + 15 Long" in paper_type:
                    st.info("📝 15 Short + 15 Long Answer Questions\n⏱️ Duration: 120-150 minutes")
                elif "15 Activity" in paper_type or "Skills Practice" in paper_type:
                    st.info("🎯 15 Hands-on Activity Tasks\n⏱️ Duration: 90-120 minutes")
                elif "25 Exploration" in paper_type or "Inquiry Tasks" in paper_type:
                    st.info("🔍 25 Inquiry-based Questions\n⏱️ Duration: 90-120 minutes")
                elif "Primary Assessment" in paper_type or "Foundation Test" in paper_type:
                    st.info("👶 20 Age-appropriate Mixed Questions\n⏱️ Duration: 45-60 minutes")
                elif "Board Pattern Paper 1" in paper_type:
                    st.info("📋 25 MCQs + 15 Short Answers\n⏱️ Duration: 120 minutes")
                elif "Board Pattern Paper 2" in paper_type:
                    st.info("📝 10 Short + 10 Long Answer Questions\n⏱️ Duration: 120 minutes")
                elif "Sample Paper Format" in paper_type or "Mock" in paper_type:
                    st.info("📋 Full Board Exam Pattern\n⏱️ Duration: 180 minutes")
                else:
                    st.info("📝 Custom Question Format\n⏱️ Duration: Varies")
        else:
            st.error("❌ No paper types available for this grade")
            paper_type = ""
    else:
        st.markdown("### 📝 Paper Type Selection")
        st.info("⚠️ Please select Board and Grade first to see available paper types")
        paper_type = ""
    
    # Additional options
    st.markdown("### ⚙️ Additional Options")
    include_answers = st.checkbox(
        "Show answers on screen after generation", 
        value=False, 
        key="show_answers_checkbox",
        help="Enable this to see correct answers immediately after test generation"
    )
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        create_btn = st.button(
            "🚀 CREATE CURRICULUM-ALIGNED MOCK TEST", 
            use_container_width=True, 
            key="create_test_btn",
            help="Generate AI-powered test questions based on your selections"
        )
        
        if create_btn:
            if not all_valid or not paper_type:
                st.error("❌ Please fix validation errors and select paper type before creating the test")
            else:
                with st.spinner("🤖 Generating curriculum-aligned questions..."):
                    test_data = generate_questions(board, grade, subject, topic, paper_type, include_answers)
                    
                    if test_data:
                        st.success("✅ Curriculum-aligned test generated successfully!")
                        st.balloons()
                        st.session_state.generated_test = test_data
                        if navigate_to:
                            navigate_to('test_display')
                        else:
                            st.session_state.current_page = 'test_display'
                            st.rerun()
                    else:
                        st.error("❌ Failed to generate test. Please check your API connection and try again.")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, key="back_home_btn"):
            if navigate_to:
                navigate_to('home')
            else:
                st.session_state.current_page = 'home'
                st.rerun()

# Alternative function names for backward compatibility
def show_mock_test_creator(navigate_to=None):
    """Alternative function name for test creator"""
    show_test_creator(navigate_to)

def main():
    """Main function for standalone testing"""
    show_test_creator()

if __name__ == "__main__":
    main()
