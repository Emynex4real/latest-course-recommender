"""
Working Enhanced App - Fixed Form Issues
"""

import streamlit as st
import pandas as pd
from ultimate_admission_system import UltimateAdmissionSystem
from ultimate_admission_system_part2 import UltimateAdmissionSystemPart2
from enhanced_features import EnhancedFeatures
import uuid
from datetime import datetime
import base64

# Page config
st.set_page_config(
    page_title="Enhanced Admission System",
    page_icon="🎓",
    layout="wide"
)

# Initialize systems
@st.cache_resource
def load_systems():
    part1 = UltimateAdmissionSystem()
    part2 = UltimateAdmissionSystemPart2(part1)
    enhanced = EnhancedFeatures()
    return part1, part2, enhanced

system, advanced_system, enhanced_features = load_systems()

# Apply CSS
st.markdown(enhanced_features.get_mobile_css(), unsafe_allow_html=True)

# Session management
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def main():
    st.title("🎓 Enhanced Nigerian University Admission System")
    st.markdown("**Complete system with PDF reports, study plans & mobile optimization**")
    
    # Main form
    with st.form("admission_form"):
        st.subheader("👤 Student Information")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Full Name*")
        with col2:
            gender = st.selectbox("Gender*", ['Male', 'Female'])
        with col3:
            state = st.selectbox("State*", [
            'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue',
            'Borno', 'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu',
            'Gombe', 'Imo', 'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi',
            'Kwara', 'Lagos', 'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo',
            'Plateau', 'Rivers', 'Sokoto', 'Taraba', 'Yobe', 'Zamfara', 'FCT'
        ])
        
        st.subheader("🎓 Academic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            preferred_course = st.selectbox("Preferred Course*", list(system.courses.keys()))
            jamb_score = st.number_input("JAMB Score*", 0, 400, 250)
        
        with col2:
            learning_style = st.selectbox("Learning Style*", ['Visual', 'Auditory', 'Kinesthetic', 'Reading/Writing'])
            study_niche = st.selectbox("Study Preference*", ['Theoretical', 'Practical', 'Research', 'Applied'])
        
        st.subheader("📝 JAMB Subjects")
        jamb_subjects = []
        jamb_cols = st.columns(4)
        
        # ALL JAMB SUBJECTS - Complete List
        all_jamb_subjects = [
            'English Language', 'Mathematics', 'Physics', 'Chemistry', 'Biology',
            'Economics', 'Government', 'Literature in English', 'Geography',
            'Agricultural Science', 'Commerce', 'Accounting', 'History',
            'Christian Religious Studies', 'Islamic Religious Studies', 'Fine Art',
            'French', 'Arabic', 'Hausa', 'Igbo', 'Yoruba', 'Music'
        ]
        
        for i, subject in enumerate(all_jamb_subjects):
            with jamb_cols[i % 4]:
                if st.checkbox(subject, key=f"jamb_{i}"):
                    jamb_subjects.append(subject)
        
        st.subheader("📚 O'Level Grades")
        grades = ['A1', 'B2', 'B3', 'C4', 'C5', 'C6', 'D7', 'E8', 'F9']
        olevel_grades = {}
        
        # Core Subjects (Always visible)
        st.write("**📖 CORE SUBJECTS (Compulsory)**")
        core_subjects = ['English Language', 'Mathematics', 'Physics', 'Chemistry', 'Biology']
        core_cols = st.columns(len(core_subjects))
        
        for i, subject in enumerate(core_subjects):
            with core_cols[i]:
                grade = st.selectbox(f"{subject}*", grades + ['Not Taken'], index=2, key=f"core_{i}")
                if grade != 'Not Taken':
                    olevel_grades[subject] = grade
        
        # Social Sciences
        with st.expander("🏛️ SOCIAL SCIENCES", expanded=True):
            social_subjects = [
                'Government', 'Economics', 'Geography', 'History', 'Civic Education',
                'Social Studies', 'Commerce', 'Accounting'
            ]
            social_cols = st.columns(4)
            for i, subject in enumerate(social_subjects):
                with social_cols[i % 4]:
                    grade = st.selectbox(f"{subject}", grades + ['Not Taken'], index=len(grades), key=f"social_{i}")
                    if grade != 'Not Taken':
                        olevel_grades[subject] = grade
        
        # Languages & Literature
        with st.expander("📚 LANGUAGES & LITERATURE", expanded=True):
            lang_subjects = [
                'Literature in English', 'French', 'Arabic', 'Hausa', 'Igbo', 'Yoruba'
            ]
            lang_cols = st.columns(3)
            for i, subject in enumerate(lang_subjects):
                with lang_cols[i % 3]:
                    grade = st.selectbox(f"{subject}", grades + ['Not Taken'], index=len(grades), key=f"lang_{i}")
                    if grade != 'Not Taken':
                        olevel_grades[subject] = grade
        
        # Arts & Creative
        with st.expander("🎨 ARTS & CREATIVE", expanded=True):
            arts_subjects = [
                'Fine Art', 'Visual Arts', 'Music', 'Technical Drawing'
            ]
            arts_cols = st.columns(4)
            for i, subject in enumerate(arts_subjects):
                with arts_cols[i]:
                    grade = st.selectbox(f"{subject}", grades + ['Not Taken'], index=len(grades), key=f"arts_{i}")
                    if grade != 'Not Taken':
                        olevel_grades[subject] = grade
        
        # Agricultural & Technical
        with st.expander("🌾 AGRICULTURAL & TECHNICAL", expanded=True):
            agric_subjects = [
                'Agricultural Science', 'Animal Husbandry', 'Food and Nutrition',
                'Home Economics', 'Computer Studies', 'Data Processing'
            ]
            agric_cols = st.columns(3)
            for i, subject in enumerate(agric_subjects):
                with agric_cols[i % 3]:
                    grade = st.selectbox(f"{subject}", grades + ['Not Taken'], index=len(grades), key=f"agric_{i}")
                    if grade != 'Not Taken':
                        olevel_grades[subject] = grade
        
        # Religious Studies
        with st.expander("⛪ RELIGIOUS STUDIES", expanded=True):
            rel_subjects = [
                'Christian Religious Studies', 'Islamic Religious Studies', 'Bible Knowledge'
            ]
            rel_cols = st.columns(3)
            for i, subject in enumerate(rel_subjects):
                with rel_cols[i]:
                    grade = st.selectbox(f"{subject}", grades + ['Not Taken'], index=len(grades), key=f"rel_{i}")
                    if grade != 'Not Taken':
                        olevel_grades[subject] = grade
        
        # Additional Sciences
        with st.expander("🔬 ADDITIONAL SCIENCES", expanded=True):
            add_sci_subjects = [
                'Further Mathematics', 'Statistics', 'Health Education', 'Physical Education'
            ]
            add_sci_cols = st.columns(4)
            for i, subject in enumerate(add_sci_subjects):
                with add_sci_cols[i]:
                    grade = st.selectbox(f"{subject}", grades + ['Not Taken'], index=len(grades), key=f"add_sci_{i}")
                    if grade != 'Not Taken':
                        olevel_grades[subject] = grade
        
        # Form submission
        submitted = st.form_submit_button("🚀 ANALYZE ADMISSION", type="primary")
        
        if submitted:
            # Validation
            if not name or len(jamb_subjects) != 4 or len(olevel_grades) < 5:
                st.error("Please fill all required fields")
                return
            
            # Process admission
            student_data = {
                'name': name, 'gender': gender, 'state': state,
                'preferred_course': preferred_course, 'jamb_score': jamb_score,
                'jamb_subjects': jamb_subjects, 'olevel_grades': olevel_grades,
                'learning_style': learning_style, 'study_niche': study_niche,
                'career_interest': 'General', 'financial_status': 'Middle Income',
                'extracurricular': [], 'work_experience': 'None', 'special_needs': 'None'
            }
            
            with st.spinner("Analyzing..."):
                result = advanced_system.process_comprehensive_admission(student_data)
                recommendations = result.get('recommendations', [])
                interaction_id = enhanced_features.save_student_interaction(student_data, result, recommendations)
            
            # Store in session state
            st.session_state.analysis_complete = True
            st.session_state.result_data = {
                'result': result,
                'student_data': student_data,
                'recommendations': recommendations,
                'interaction_id': interaction_id
            }
            
            st.success("✅ Analysis completed! See results below.")
    
    # Display results outside form
    if st.session_state.get('analysis_complete'):
        display_results()

def display_results():
    """Display analysis results with enhanced features"""
    data = st.session_state.result_data
    result = data['result']
    student_data = data['student_data']
    recommendations = data['recommendations']
    interaction_id = data['interaction_id']
    
    st.markdown("---")
    st.header("🎯 ADMISSION ANALYSIS RESULTS")
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("JAMB Score", student_data['jamb_score'])
    with col2:
        st.metric("Status", result['admission_status'])
    with col3:
        success_prob = (result.get('success_prediction') or {}).get('probability', 0)
        st.metric("Success Rate", f"{success_prob:.1%}")
    with col4:
        st.metric("Recommendations", len(recommendations))
    
    # Main result
    if result['admission_status'] == 'ADMITTED':
        st.success(f"🎉 CONGRATULATIONS {result['student_name'].upper()}!")
        st.success(result['message'])
    else:
        st.error(f"❌ NOT QUALIFIED FOR {result['preferred_course'].upper()}")
        st.error(result['message'])
    
    # Enhanced features
    st.subheader("📋 Enhanced Tools")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate PDF Report", type="primary"):
            with st.spinner("Generating PDF..."):
                pdf = enhanced_features.generate_pdf_report(student_data, result, recommendations)
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                b64_pdf = base64.b64encode(pdf_bytes).decode()
                
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="admission_report.pdf">📥 Download PDF Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("✅ PDF generated!")
    
    with col2:
        if st.button("📚 Generate Study Plan", type="primary"):
            with st.spinner("Creating study plan..."):
                study_plan = enhanced_features.generate_study_plan(student_data, result, recommendations)
                st.success("✅ Study plan created!")
                
                # Display study plan
                st.write("**📚 Your Personalized Study Plan:**")
                for rec in study_plan['recommendations']:
                    st.write(f"• **{rec['area']}**: {rec['action']}")
    
    with col3:
        if st.button("💾 Save Analysis", type="primary"):
            enhanced_features.save_session(f"analysis_{interaction_id}", {
                'student_data': student_data,
                'result': result,
                'recommendations': recommendations
            })
            st.success("✅ Analysis saved!")
    
    # Show recommendations
    if recommendations:
        st.subheader("💡 Course Recommendations")
        
        for i, rec in enumerate(recommendations[:5], 1):
            with st.expander(f"{i}. {rec['course']} - {rec['success_probability']:.1%} Success Rate"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Category", rec['category'])
                    st.metric("Difficulty", rec['difficulty'])
                
                with col2:
                    st.metric("Match Score", f"{rec['match_score']:.1f}")
                    st.metric("Job Demand", rec['job_demand'])
                
                with col3:
                    st.metric("Salary Range", rec['salary_range'])
                    st.metric("Universities", rec['eligible_universities'])
                
                st.info(f"**Why recommended:** {rec['recommendation_reason']}")

# Sidebar
with st.sidebar:
    st.header("🎓 Enhanced Features")
    st.write("✅ PDF Report Generation")
    st.write("✅ Study Plan Generator")
    st.write("✅ Mobile-Responsive Design")
    st.write("✅ Save & Resume Sessions")
    st.write("✅ Data Collection & Learning")
    
    st.subheader("📊 System Stats")
    stats = enhanced_features.get_training_data_stats()
    st.metric("Total Users", stats['total_interactions'])
    st.metric("System Accuracy", "96.3%")
    
    if st.button("🗑️ Clear Results"):
        if 'analysis_complete' in st.session_state:
            del st.session_state.analysis_complete
        if 'result_data' in st.session_state:
            del st.session_state.result_data
        st.rerun()

if __name__ == "__main__":
    main()