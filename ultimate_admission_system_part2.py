"""
Ultimate Admission System - Part 2
Advanced ML predictions and recommendation engine
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

class UltimateAdmissionSystemPart2:
    def __init__(self, part1_system):
        self.system = part1_system
        self.ml_models = {}
        self.encoders = {}
        
    def validate_olevel_requirements(self, course, student_olevel_grades):
        """Enhanced O'Level validation"""
        if course not in self.system.courses:
            return False, f"Course '{course}' not found"
        
        grade_values = {'A1': 9, 'B2': 8, 'B3': 7, 'C4': 6, 'C5': 5, 'C6': 4, 'D7': 3, 'E8': 2, 'F9': 1}
        
        total_credits = 0
        required_subjects = set(self.system.courses[course]['olevel'])
        
        # Count total credits (C6 and above)
        for subject, grade in student_olevel_grades.items():
            if grade in grade_values and grade_values[grade] >= 4:
                total_credits += 1
        
        # Must have minimum 5 credits
        if total_credits < 5:
            return False, f"Need 5 credits minimum (you have {total_credits})"
        
        # Check course-specific requirements
        missing_requirements = []
        for req_subject in required_subjects:
            if req_subject not in student_olevel_grades:
                missing_requirements.append(f"{req_subject} (not taken)")
            elif student_olevel_grades[req_subject] not in grade_values or grade_values[student_olevel_grades[req_subject]] < 4:
                current_grade = student_olevel_grades.get(req_subject, 'Not taken')
                missing_requirements.append(f"{req_subject} (need C6+, you have {current_grade})")
        
        if missing_requirements:
            return False, f"Requirements not met: {'; '.join(missing_requirements)}"
        
        return True, f"Valid O'Level ({total_credits} credits)"
    
    def calculate_university_specific_eligibility(self, course, jamb_score, jamb_subjects, olevel_grades, state):
        """Check eligibility for specific universities"""
        if course not in self.system.courses:
            return {}
        
        course_data = self.system.courses[course]
        university_results = {}
        
        for uni_code, uni_data in course_data.get('universities', {}).items():
            result = {
                'university': self.system.universities[uni_code]['name'],
                'cutoff': uni_data['cutoff'],
                'special_requirements': uni_data.get('special', 'None'),
                'eligible': False,
                'catchment_advantage': False,
                'reason': ''
            }
            
            # Check basic eligibility
            jamb_valid, jamb_msg = self.system.validate_jamb_subjects(course, jamb_subjects)
            olevel_valid, olevel_msg = self.validate_olevel_requirements(course, olevel_grades)
            
            if not jamb_valid:
                result['reason'] = f"JAMB: {jamb_msg}"
            elif not olevel_valid:
                result['reason'] = f"O'Level: {olevel_msg}"
            elif jamb_score < uni_data['cutoff']:
                result['reason'] = f"Score too low ({jamb_score}/{uni_data['cutoff']})"
            else:
                result['eligible'] = True
                result['reason'] = "Eligible"
                
                # Check catchment advantage
                if state in self.system.universities[uni_code].get('catchment', []):
                    result['catchment_advantage'] = True
                    result['reason'] += " + Catchment advantage"
            
            university_results[uni_code] = result
        
        return university_results
    
    def assess_advanced_student_strengths(self, olevel_grades, learning_style, study_niche, jamb_subjects):
        """Advanced student strength assessment"""
        grade_values = {'A1': 9, 'B2': 8, 'B3': 7, 'C4': 6, 'C5': 5, 'C6': 4, 'D7': 3, 'E8': 2, 'F9': 1}
        
        strengths = {}
        
        # Subject area strengths
        subject_areas = {
            'Science': ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'Further Mathematics'],
            'Medical': ['Biology', 'Chemistry', 'Physics', 'Mathematics'],
            'Engineering': ['Mathematics', 'Physics', 'Chemistry', 'Further Mathematics', 'Technical Drawing'],
            'Commercial': ['Mathematics', 'Economics', 'Commerce', 'Accounting', 'Government'],
            'Arts': ['English Language', 'Literature in English', 'Government', 'History', 'CRS', 'IRS'],
            'Agriculture': ['Biology', 'Chemistry', 'Agricultural Science', 'Mathematics', 'Physics']
        }
        
        for area, subjects in subject_areas.items():
            scores = []
            for subject in subjects:
                if subject in olevel_grades:
                    grade = olevel_grades[subject]
                    if grade in grade_values:
                        scores.append(grade_values[grade])
            
            if scores:
                strengths[area] = {
                    'average_score': np.mean(scores),
                    'subject_count': len(scores),
                    'strength_level': self._categorize_strength(np.mean(scores))
                }
            else:
                strengths[area] = {
                    'average_score': 1,
                    'subject_count': 0,
                    'strength_level': 'Very Weak'
                }
        
        # Learning style compatibility
        learning_compatibility = {
            'Visual': {'Science': 1.1, 'Engineering': 1.2, 'Arts': 1.0, 'Medical': 1.1},
            'Auditory': {'Arts': 1.2, 'Commercial': 1.1, 'Education': 1.2, 'Medical': 1.0},
            'Kinesthetic': {'Engineering': 1.3, 'Agriculture': 1.2, 'Medical': 1.1, 'Science': 1.1},
            'Reading/Writing': {'Arts': 1.3, 'Commercial': 1.1, 'Education': 1.2, 'Science': 1.0}
        }
        
        # Apply learning style multiplier
        for area in strengths:
            multiplier = learning_compatibility.get(learning_style, {}).get(area, 1.0)
            strengths[area]['adjusted_score'] = strengths[area]['average_score'] * multiplier
        
        # Study niche compatibility
        niche_compatibility = {
            'Theoretical': {'Science': 1.2, 'Arts': 1.1, 'Medical': 1.0, 'Engineering': 0.9},
            'Practical': {'Engineering': 1.3, 'Medical': 1.2, 'Agriculture': 1.2, 'Science': 1.1},
            'Research': {'Science': 1.3, 'Medical': 1.2, 'Arts': 1.1, 'Agriculture': 1.1},
            'Applied': {'Engineering': 1.2, 'Commercial': 1.2, 'Agriculture': 1.1, 'Medical': 1.1}
        }
        
        # Apply study niche multiplier
        for area in strengths:
            multiplier = niche_compatibility.get(study_niche, {}).get(area, 1.0)
            strengths[area]['final_score'] = strengths[area]['adjusted_score'] * multiplier
        
        return strengths
    
    def _categorize_strength(self, score):
        """Categorize strength level based on score"""
        if score >= 8:
            return 'Excellent'
        elif score >= 7:
            return 'Very Good'
        elif score >= 6:
            return 'Good'
        elif score >= 5:
            return 'Average'
        elif score >= 4:
            return 'Below Average'
        else:
            return 'Weak'
    
    def predict_success_probability(self, course, student_profile):
        """Predict student success probability in a course using ML"""
        if course not in self.system.courses:
            return 0.5
        
        course_data = self.system.courses[course]
        
        # Extract features for ML prediction
        features = self._extract_ml_features(student_profile, course_data)
        
        # Use category-specific model if available
        category = course_data['category']
        if category in self.ml_models:
            try:
                probability = self.ml_models[category].predict_proba([features])[0][1]
                return min(0.95, max(0.05, probability))
            except:
                pass
        
        # Fallback to rule-based prediction
        return self._rule_based_success_prediction(student_profile, course_data)
    
    def _extract_ml_features(self, student_profile, course_data):
        """Extract features for ML model"""
        grade_values = {'A1': 9, 'B2': 8, 'B3': 7, 'C4': 6, 'C5': 5, 'C6': 4, 'D7': 3, 'E8': 2, 'F9': 1}
        
        # Basic features
        jamb_score = student_profile.get('jamb_score', 0)
        
        # O'Level performance
        olevel_grades = student_profile.get('olevel_grades', {})
        olevel_total = sum(grade_values.get(grade, 1) for grade in olevel_grades.values())
        olevel_average = olevel_total / max(len(olevel_grades), 1)
        
        # Course-specific subject performance
        required_subjects = course_data.get('olevel', [])
        course_subject_scores = []
        for subject in required_subjects:
            if subject in olevel_grades:
                course_subject_scores.append(grade_values.get(olevel_grades[subject], 1))
        
        course_subject_average = np.mean(course_subject_scores) if course_subject_scores else 1
        
        # Difficulty vs capability
        difficulty_map = {'Very High': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        course_difficulty = difficulty_map.get(course_data.get('difficulty', 'Medium'), 2)
        
        # Learning style encoding
        learning_styles = ['Visual', 'Auditory', 'Kinesthetic', 'Reading/Writing']
        learning_style_encoded = learning_styles.index(student_profile.get('learning_style', 'Visual'))
        
        # Study niche encoding
        study_niches = ['Theoretical', 'Practical', 'Research', 'Applied']
        study_niche_encoded = study_niches.index(student_profile.get('study_niche', 'Practical'))
        
        return [
            jamb_score / 400.0,  # Normalized JAMB score
            olevel_average / 9.0,  # Normalized O'Level average
            course_subject_average / 9.0,  # Normalized course-specific average
            len(olevel_grades) / 10.0,  # Number of subjects taken
            course_difficulty / 4.0,  # Course difficulty
            learning_style_encoded / 3.0,  # Learning style
            study_niche_encoded / 3.0,  # Study niche
        ]
    
    def _rule_based_success_prediction(self, student_profile, course_data):
        """Rule-based success prediction as fallback"""
        grade_values = {'A1': 9, 'B2': 8, 'B3': 7, 'C4': 6, 'C5': 5, 'C6': 4, 'D7': 3, 'E8': 2, 'F9': 1}
        
        jamb_score = student_profile.get('jamb_score', 0)
        olevel_grades = student_profile.get('olevel_grades', {})
        
        # Base probability from JAMB score
        cutoff = min(course_data.get('universities', {}).values(), key=lambda x: x['cutoff'])['cutoff'] if course_data.get('universities') else 200
        jamb_factor = min(1.0, jamb_score / cutoff)
        
        # O'Level factor
        required_subjects = course_data.get('olevel', [])
        subject_scores = []
        for subject in required_subjects:
            if subject in olevel_grades:
                subject_scores.append(grade_values.get(olevel_grades[subject], 1))
        
        olevel_factor = (np.mean(subject_scores) / 9.0) if subject_scores else 0.1
        
        # Difficulty adjustment
        difficulty_penalties = {'Very High': 0.8, 'High': 0.9, 'Medium': 1.0, 'Low': 1.1}
        difficulty_factor = difficulty_penalties.get(course_data.get('difficulty', 'Medium'), 1.0)
        
        # Calculate final probability
        probability = (jamb_factor * 0.4 + olevel_factor * 0.6) * difficulty_factor
        
        return min(0.95, max(0.05, probability))
    
    def recommend_intelligent_alternatives(self, student_profile):
        """Intelligent course recommendations based on comprehensive analysis"""
        jamb_score = student_profile.get('jamb_score', 0)
        jamb_subjects = student_profile.get('jamb_subjects', [])
        olevel_grades = student_profile.get('olevel_grades', {})
        learning_style = student_profile.get('learning_style', 'Visual')
        study_niche = student_profile.get('study_niche', 'Practical')
        state = student_profile.get('state', '')
        
        # Get advanced strengths
        strengths = self.assess_advanced_student_strengths(olevel_grades, learning_style, study_niche, jamb_subjects)
        
        recommendations = []
        
        for course, course_data in self.system.courses.items():
            # Check basic eligibility
            jamb_valid, _ = self.system.validate_jamb_subjects(course, jamb_subjects)
            olevel_valid, _ = self.validate_olevel_requirements(course, olevel_grades)
            
            if not jamb_valid or not olevel_valid:
                continue
            
            # Check if meets any university cutoff
            universities = course_data.get('universities', {})
            min_cutoff = min([uni['cutoff'] for uni in universities.values()]) if universities else 180
            
            if jamb_score < min_cutoff:
                continue
            
            # Calculate comprehensive match score
            category = course_data['category']
            strength_data = strengths.get(category, {'final_score': 1})
            
            # Success probability
            success_prob = self.predict_success_probability(course, student_profile)
            
            # Career prospects score
            career_data = self.system.career_paths.get(category, {})
            career_score = self._calculate_career_score(career_data)
            
            # University options
            university_options = self.calculate_university_specific_eligibility(
                course, jamb_score, jamb_subjects, olevel_grades, state
            )
            eligible_unis = [uni for uni, data in university_options.items() if data['eligible']]
            
            if not eligible_unis:
                continue
            
            # Final recommendation score
            match_score = (
                strength_data['final_score'] * 0.3 +
                success_prob * 10 * 0.4 +
                career_score * 0.2 +
                len(eligible_unis) * 0.1
            )
            
            recommendations.append({
                'course': course,
                'category': category,
                'match_score': match_score,
                'success_probability': success_prob,
                'strength_level': strength_data.get('strength_level', 'Average'),
                'career_prospects': course_data.get('career_prospects', []),
                'salary_range': course_data.get('salary_range', 'Not specified'),
                'job_demand': course_data.get('job_demand', 'Medium'),
                'eligible_universities': len(eligible_unis),
                'university_options': university_options,
                'duration': course_data.get('duration', 4),
                'difficulty': course_data.get('difficulty', 'Medium'),
                'recommendation_reason': self._generate_recommendation_reason(
                    strength_data, success_prob, career_data, eligible_unis
                )
            })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:15]  # Top 15 recommendations
    
    def _calculate_career_score(self, career_data):
        """Calculate career prospects score"""
        scores = {
            'Very High': 5, 'High': 4, 'Medium': 3, 'Low': 2, 'Very Low': 1
        }
        
        growth_score = scores.get(career_data.get('growth_rate', 'Medium'), 3)
        security_score = scores.get(career_data.get('job_security', 'Medium'), 3)
        mobility_score = scores.get(career_data.get('international_mobility', 'Medium'), 3)
        entrepreneur_score = scores.get(career_data.get('entrepreneurship_potential', 'Medium'), 3)
        
        return (growth_score + security_score + mobility_score + entrepreneur_score) / 4
    
    def _generate_recommendation_reason(self, strength_data, success_prob, career_data, eligible_unis):
        """Generate personalized recommendation reason"""
        reasons = []
        
        # Strength-based reason
        strength_level = strength_data.get('strength_level', 'Average')
        if strength_level in ['Excellent', 'Very Good']:
            reasons.append(f"Strong academic foundation ({strength_level})")
        elif strength_level == 'Good':
            reasons.append("Good academic match")
        
        # Success probability reason
        if success_prob > 0.8:
            reasons.append("Very high success probability")
        elif success_prob > 0.6:
            reasons.append("Good success probability")
        
        # Career prospects reason
        growth_rate = career_data.get('growth_rate', 'Medium')
        if growth_rate in ['Very High', 'High']:
            reasons.append(f"{growth_rate.lower()} career growth potential")
        
        # University options reason
        if len(eligible_unis) > 3:
            reasons.append("Multiple university options available")
        
        return "; ".join(reasons) if reasons else "Meets basic requirements"
    
    def process_comprehensive_admission(self, student_data):
        """Main comprehensive admission processing"""
        name = student_data['name']
        preferred_course = student_data['preferred_course']
        jamb_score = student_data['jamb_score']
        jamb_subjects = student_data['jamb_subjects']
        olevel_grades = student_data['olevel_grades']
        learning_style = student_data['learning_style']
        study_niche = student_data['study_niche']
        state = student_data.get('state', '')
        
        result = {
            'student_name': name,
            'preferred_course': preferred_course,
            'admission_status': None,
            'message': None,
            'university_options': {},
            'recommendations': [],
            'success_prediction': None,
            'career_analysis': None
        }
        
        # Check preferred course eligibility
        jamb_valid, jamb_msg = self.system.validate_jamb_subjects(preferred_course, jamb_subjects)
        olevel_valid, olevel_msg = self.validate_olevel_requirements(preferred_course, olevel_grades)
        
        if jamb_valid and olevel_valid:
            # Check university-specific eligibility
            university_options = self.calculate_university_specific_eligibility(
                preferred_course, jamb_score, jamb_subjects, olevel_grades, state
            )
            
            eligible_unis = [uni for uni, data in university_options.items() if data['eligible']]
            
            if eligible_unis:
                result['admission_status'] = 'ADMITTED'
                result['message'] = f"Congratulations! You are eligible for {preferred_course} at {len(eligible_unis)} universities."
                result['university_options'] = university_options
                
                # Success prediction
                success_prob = self.predict_success_probability(preferred_course, student_data)
                result['success_prediction'] = {
                    'probability': success_prob,
                    'level': 'High' if success_prob > 0.7 else 'Medium' if success_prob > 0.5 else 'Low',
                    'advice': self._generate_success_advice(success_prob)
                }
                
                # Career analysis
                course_data = self.system.courses[preferred_course]
                category = course_data['category']
                career_data = self.system.career_paths.get(category, {})
                
                result['career_analysis'] = {
                    'prospects': course_data.get('career_prospects', []),
                    'salary_range': course_data.get('salary_range', 'Not specified'),
                    'job_demand': course_data.get('job_demand', 'Medium'),
                    'growth_rate': career_data.get('growth_rate', 'Medium'),
                    'job_security': career_data.get('job_security', 'Medium'),
                    'international_mobility': career_data.get('international_mobility', 'Medium')
                }
            else:
                result['admission_status'] = 'NOT_ADMITTED'
                result['message'] = f"You meet the subject requirements for {preferred_course} but your JAMB score is below all university cutoffs."
        else:
            result['admission_status'] = 'NOT_ADMITTED'
            if not jamb_valid:
                result['message'] = f"JAMB subjects invalid for {preferred_course}. {jamb_msg}"
            else:
                result['message'] = f"O'Level requirements not met for {preferred_course}. {olevel_msg}"
        
        # Always provide recommendations
        recommendations = self.recommend_intelligent_alternatives(student_data)
        result['recommendations'] = recommendations
        
        if result['admission_status'] == 'NOT_ADMITTED' and recommendations:
            result['message'] += f"\n\nHowever, we found {len(recommendations)} alternative courses that match your profile:"
        
        return result
    
    def _generate_success_advice(self, success_prob):
        """Generate advice based on success probability"""
        if success_prob > 0.8:
            return "Excellent match! You have strong potential for success in this course."
        elif success_prob > 0.6:
            return "Good match. Focus on strengthening your foundation in key subjects."
        elif success_prob > 0.4:
            return "Moderate match. Consider additional preparation and study support."
        else:
            return "Challenging match. Strongly consider alternative courses better suited to your strengths."