"""
Enhanced Features: PDF Report, Study Plan, Data Collection, Mobile Design
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from fpdf import FPDF
import streamlit as st

class EnhancedFeatures:
    def __init__(self):
        self.data_storage_path = "data/student_interactions.csv"
        self.session_storage_path = "data/saved_sessions.json"
        
    def save_student_interaction(self, student_data, result, recommendations):
        """Save student interaction for continuous model improvement"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'student_id': f"{student_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'name': student_data['name'],
            'state': student_data['state'],
            'jamb_score': student_data['jamb_score'],
            'jamb_subjects': ','.join(student_data['jamb_subjects']),
            'preferred_course': student_data['preferred_course'],
            'admission_status': result['admission_status'],
            'success_probability': (result.get('success_prediction') or {}).get('probability', 0),
            'top_recommendation': recommendations[0]['course'] if recommendations else '',
            'recommendation_match_score': recommendations[0]['match_score'] if recommendations else 0,
            'learning_style': student_data['learning_style'],
            'study_niche': student_data['study_niche'],
            'olevel_credits': sum(1 for grade in student_data['olevel_grades'].values() 
                                if grade in ['A1','B2','B3','C4','C5','C6']),
            'career_interest': student_data.get('career_interest', ''),
            'extracurricular_count': len(student_data.get('extracurricular', [])),
            'financial_status': student_data.get('financial_status', ''),
            'special_needs': student_data.get('special_needs', 'None')
        }
        
        # Save to CSV for model retraining
        df_new = pd.DataFrame([interaction])
        
        if os.path.exists(self.data_storage_path):
            df_existing = pd.read_csv(self.data_storage_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
            
        os.makedirs(os.path.dirname(self.data_storage_path), exist_ok=True)
        df_combined.to_csv(self.data_storage_path, index=False)
        
        return interaction['student_id']
    
    def generate_pdf_report(self, student_data, result, recommendations):
        """Generate comprehensive PDF report"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Header
        pdf.cell(0, 10, 'Nigerian University Admission Analysis Report', 0, 1, 'C')
        pdf.ln(5)
        
        # Student Information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'STUDENT INFORMATION', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        info_lines = [
            f"Name: {student_data['name']}",
            f"State: {student_data['state']}",
            f"JAMB Score: {student_data['jamb_score']}/400",
            f"JAMB Subjects: {', '.join(student_data['jamb_subjects'])}",
            f"Preferred Course: {student_data['preferred_course']}",
            f"Learning Style: {student_data['learning_style']}",
            f"Study Preference: {student_data['study_niche']}"
        ]
        
        for line in info_lines:
            pdf.cell(0, 6, line, 0, 1)
        
        pdf.ln(5)
        
        # Admission Status
        pdf.set_font('Arial', 'B', 12)
        status_color = (0, 128, 0) if result['admission_status'] == 'ADMITTED' else (255, 0, 0)
        pdf.set_text_color(*status_color)
        pdf.cell(0, 8, f"ADMISSION STATUS: {result['admission_status']}", 0, 1)
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, result['message'])
        pdf.ln(5)
        
        # Success Prediction
        pred = result.get('success_prediction')
        if pred:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'SUCCESS PREDICTION', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, f"Success Probability: {pred['probability']:.1%}", 0, 1)
            pdf.cell(0, 6, f"Success Level: {pred['level']}", 0, 1)
            pdf.multi_cell(0, 6, f"Advice: {pred['advice']}")
            pdf.ln(3)
        
        # University Options
        university_options = result.get('university_options')
        if university_options:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'UNIVERSITY OPTIONS', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            for uni_code, uni_data in university_options.items():
                status = "ELIGIBLE" if uni_data['eligible'] else "NOT ELIGIBLE"
                catchment = " (Catchment Advantage)" if uni_data.get('catchment_advantage') else ""
                pdf.cell(0, 6, f"{uni_data['university']}: {status}{catchment}", 0, 1)
                pdf.cell(0, 6, f"  Cutoff: {uni_data['cutoff']}, Your Score: {student_data['jamb_score']}", 0, 1)
        
        pdf.ln(5)
        
        # Top Recommendations
        if recommendations:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'TOP COURSE RECOMMENDATIONS', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            for i, rec in enumerate(recommendations[:5], 1):
                pdf.cell(0, 6, f"{i}. {rec['course']} ({rec['category']})", 0, 1)
                pdf.cell(0, 6, f"   Match Score: {rec['match_score']:.1f}, Success Rate: {rec['success_probability']:.1%}", 0, 1)
                pdf.cell(0, 6, f"   Salary Range: {rec['salary_range']}, Job Demand: {rec['job_demand']}", 0, 1)
                pdf.ln(2)
        
        # Footer
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 6, f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 0, 1, 'C')
        pdf.cell(0, 6, "Nigerian University Admission Prediction System", 0, 1, 'C')
        
        return pdf
    
    def generate_study_plan(self, student_data, result, recommendations):
        """Generate personalized study improvement plan"""
        jamb_score = student_data['jamb_score']
        olevel_grades = student_data['olevel_grades']
        preferred_course = student_data['preferred_course']
        
        # Analyze weaknesses
        grade_values = {'A1': 9, 'B2': 8, 'B3': 7, 'C4': 6, 'C5': 5, 'C6': 4, 'D7': 3, 'E8': 2, 'F9': 1}
        
        weak_subjects = []
        strong_subjects = []
        
        for subject, grade in olevel_grades.items():
            score = grade_values.get(grade, 1)
            if score <= 4:  # Below C6
                weak_subjects.append((subject, grade, score))
            elif score >= 7:  # B3 and above
                strong_subjects.append((subject, grade, score))
        
        # Generate plan
        plan = {
            'assessment': {
                'jamb_score': jamb_score,
                'jamb_status': 'Excellent' if jamb_score >= 300 else 'Good' if jamb_score >= 250 else 'Needs Improvement',
                'olevel_credits': len([g for g in olevel_grades.values() if grade_values.get(g, 0) >= 4]),
                'weak_subjects': weak_subjects,
                'strong_subjects': strong_subjects
            },
            'recommendations': [],
            'timeline': self._generate_timeline(jamb_score, weak_subjects),
            'resources': self._get_study_resources(preferred_course, weak_subjects)
        }
        
        # Generate specific recommendations
        if jamb_score < 200:
            plan['recommendations'].append({
                'priority': 'HIGH',
                'area': 'JAMB Score Improvement',
                'action': 'Focus on intensive JAMB preparation',
                'target': 'Increase score by 50+ points',
                'timeline': '3-6 months'
            })
        
        if len(weak_subjects) > 2:
            plan['recommendations'].append({
                'priority': 'HIGH',
                'area': 'O\'Level Retakes',
                'action': f'Retake {len(weak_subjects)} subjects: {", ".join([s[0] for s in weak_subjects[:3]])}',
                'target': 'Achieve minimum C6 in all subjects',
                'timeline': '6-12 months'
            })
        
        if result['admission_status'] == 'NOT_ADMITTED':
            plan['recommendations'].append({
                'priority': 'MEDIUM',
                'area': 'Alternative Courses',
                'action': f'Consider {recommendations[0]["course"] if recommendations else "alternative courses"}',
                'target': 'Secure admission in a related field',
                'timeline': 'Current application cycle'
            })
        
        # Learning style specific advice
        learning_advice = {
            'Visual': 'Use diagrams, charts, and visual aids. Create mind maps for complex topics.',
            'Auditory': 'Join study groups, use audio materials, and explain concepts aloud.',
            'Kinesthetic': 'Use hands-on practice, experiments, and physical activities while studying.',
            'Reading/Writing': 'Take detailed notes, create summaries, and practice writing exercises.'
        }
        
        plan['recommendations'].append({
            'priority': 'MEDIUM',
            'area': 'Study Method Optimization',
            'action': learning_advice.get(student_data['learning_style'], 'Use varied study methods'),
            'target': 'Improve learning efficiency',
            'timeline': 'Ongoing'
        })
        
        return plan
    
    def _generate_timeline(self, jamb_score, weak_subjects):
        """Generate study timeline based on current status"""
        timeline = []
        
        if jamb_score < 250:
            timeline.extend([
                {'period': 'Month 1-2', 'focus': 'JAMB fundamentals and practice tests'},
                {'period': 'Month 3-4', 'focus': 'Intensive JAMB preparation and mock exams'},
                {'period': 'Month 5-6', 'focus': 'Final JAMB preparation and registration'}
            ])
        
        if weak_subjects:
            timeline.extend([
                {'period': 'Month 1-3', 'focus': f'O\'Level preparation for {len(weak_subjects)} subjects'},
                {'period': 'Month 4-6', 'focus': 'O\'Level examinations and results'},
                {'period': 'Month 7-8', 'focus': 'University applications with improved grades'}
            ])
        
        return timeline
    
    def _get_study_resources(self, course, weak_subjects):
        """Get study resources based on course and weaknesses"""
        resources = {
            'jamb_prep': [
                'JAMB Past Questions (2010-2024)',
                'JAMB CBT Practice Software',
                'Online JAMB Tutorials (YouTube/Educational platforms)',
                'JAMB Study Groups and Forums'
            ],
            'olevel_prep': [],
            'course_specific': []
        }
        
        # Add O'Level resources for weak subjects
        for subject, _, _ in weak_subjects:
            resources['olevel_prep'].append(f'{subject} WAEC Past Questions')
            resources['olevel_prep'].append(f'{subject} Textbooks and Study Guides')
        
        # Add course-specific resources
        course_lower = course.lower()
        if 'medicine' in course_lower or 'nursing' in course_lower:
            resources['course_specific'].extend([
                'Biology and Chemistry intensive courses',
                'Medical terminology resources',
                'Healthcare career guidance materials'
            ])
        elif 'engineering' in course_lower or 'computer' in course_lower:
            resources['course_specific'].extend([
                'Mathematics and Physics advanced courses',
                'Programming tutorials (if Computer Engineering)',
                'Engineering career pathway guides'
            ])
        elif 'law' in course_lower:
            resources['course_specific'].extend([
                'Government and Literature intensive study',
                'Legal terminology and concepts',
                'Law school preparation materials'
            ])
        
        return resources
    
    def save_session(self, session_id, student_data):
        """Save user session for resume functionality"""
        session_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'student_data': student_data,
            'expires': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Load existing sessions
        sessions = {}
        if os.path.exists(self.session_storage_path):
            try:
                with open(self.session_storage_path, 'r') as f:
                    sessions = json.load(f)
            except:
                sessions = {}
        
        # Add new session
        sessions[session_id] = session_data
        
        # Save updated sessions
        os.makedirs(os.path.dirname(self.session_storage_path), exist_ok=True)
        with open(self.session_storage_path, 'w') as f:
            json.dump(sessions, f, indent=2)
    
    def load_session(self, session_id):
        """Load saved session"""
        if not os.path.exists(self.session_storage_path):
            return None
        
        try:
            with open(self.session_storage_path, 'r') as f:
                sessions = json.load(f)
            
            if session_id in sessions:
                session = sessions[session_id]
                # Check if session is expired
                expires = datetime.fromisoformat(session['expires'])
                if datetime.now() < expires:
                    return session['student_data']
        except:
            pass
        
        return None
    
    def get_mobile_css(self):
        """Get CSS for mobile-responsive design"""
        return """
        <style>
        /* Mobile-first responsive design */
        .main > div {
            padding-top: 2rem;
        }
        
        /* Mobile optimization */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: 100%;
            }
            
            /* Stack columns on mobile */
            .row-widget.stColumns > div {
                min-width: 100% !important;
                margin-bottom: 1rem;
            }
            
            /* Adjust form elements */
            .stSelectbox > div > div {
                font-size: 14px;
            }
            
            .stTextInput > div > div > input {
                font-size: 16px; /* Prevent zoom on iOS */
            }
            
            /* Adjust metrics */
            .metric-container {
                background: #f0f2f6;
                padding: 0.5rem;
                border-radius: 0.5rem;
                margin-bottom: 0.5rem;
            }
            
            /* Adjust expandable sections */
            .streamlit-expanderHeader {
                font-size: 14px;
            }
            
            /* Adjust buttons */
            .stButton > button {
                width: 100%;
                margin-top: 1rem;
            }
        }
        
        /* Tablet optimization */
        @media (min-width: 769px) and (max-width: 1024px) {
            .main .block-container {
                max-width: 90%;
            }
        }
        
        /* Desktop optimization */
        @media (min-width: 1025px) {
            .main .block-container {
                max-width: 1200px;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .metric-container {
                background: #262730;
            }
        }
        
        /* Print styles for PDF generation */
        @media print {
            .sidebar .sidebar-content {
                display: none;
            }
            .main .block-container {
                max-width: 100%;
                padding: 0;
            }
        }
        
        /* Accessibility improvements */
        .stButton > button:focus {
            outline: 2px solid #ff6b6b;
            outline-offset: 2px;
        }
        
        /* Loading states */
        .stSpinner > div {
            border-color: #ff6b6b transparent transparent transparent;
        }
        
        /* Success/Error states */
        .success-message {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        .error-message {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        </style>
        """
    
    def display_study_plan(self, plan):
        """Display study plan in Streamlit"""
        st.subheader("📚 Personalized Study Improvement Plan")
        
        # Assessment Summary
        assessment = plan['assessment']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("JAMB Status", assessment['jamb_status'])
        with col2:
            st.metric("O'Level Credits", f"{assessment['olevel_credits']}/9")
        with col3:
            st.metric("Weak Subjects", len(assessment['weak_subjects']))
        
        # Recommendations
        st.write("**🎯 Priority Actions:**")
        for rec in plan['recommendations']:
            priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            st.write(f"{priority_color.get(rec['priority'], '🔵')} **{rec['area']}**")
            st.write(f"   Action: {rec['action']}")
            st.write(f"   Target: {rec['target']}")
            st.write(f"   Timeline: {rec['timeline']}")
            st.write("")
        
        # Timeline
        if plan['timeline']:
            st.write("**📅 Study Timeline:**")
            for item in plan['timeline']:
                st.write(f"• **{item['period']}**: {item['focus']}")
        
        # Resources
        st.write("**📖 Recommended Study Resources:**")
        
        resources = plan['resources']
        
        with st.expander("JAMB Preparation Resources"):
            for resource in resources['jamb_prep']:
                st.write(f"• {resource}")
        
        if resources['olevel_prep']:
            with st.expander("O'Level Preparation Resources"):
                for resource in resources['olevel_prep']:
                    st.write(f"• {resource}")
        
        if resources['course_specific']:
            with st.expander("Course-Specific Resources"):
                for resource in resources['course_specific']:
                    st.write(f"• {resource}")
    
    def get_training_data_stats(self):
        """Get statistics about collected training data"""
        if not os.path.exists(self.data_storage_path):
            return {"total_interactions": 0, "latest_interaction": None}
        
        try:
            df = pd.read_csv(self.data_storage_path)
            return {
                "total_interactions": len(df),
                "latest_interaction": df['timestamp'].max() if len(df) > 0 else None,
                "admission_rate": df['admission_status'].value_counts().get('ADMITTED', 0) / len(df) if len(df) > 0 else 0,
                "top_courses": df['preferred_course'].value_counts().head(5).to_dict() if len(df) > 0 else {},
                "avg_jamb_score": df['jamb_score'].mean() if len(df) > 0 else 0
            }
        except:
            return {"total_interactions": 0, "latest_interaction": None}