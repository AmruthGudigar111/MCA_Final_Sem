import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class StudentPerformancePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = 'student_model.pkl'
        self.scaler_path = 'scaler.pkl'
        
    def load_model(self):
        """Load trained model if exists"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            return True
        return False
    
    def train_model(self, data):
        """Train the prediction model"""
        # Prepare features
        X = data[['attendance_percentage', 'internal_marks', 'behavior_score']]
        y = data['risk_level']  # 0: Low, 1: Medium, 2: High
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model Accuracy: {accuracy:.2f}")
        print(classification_report(y_test, y_pred))
        
        # Save model
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        return accuracy
    
    def generate_sample_data(self, n_samples=200):
        """Create synthetic training data for model training."""
        rng = np.random.default_rng(seed=42)
        attendance = rng.integers(50, 100, size=n_samples)
        internal_marks = rng.integers(30, 100, size=n_samples)
        behavior_score = rng.integers(1, 11, size=n_samples)
        risk_level = []

        for a, m, b in zip(attendance, internal_marks, behavior_score):
            score = (a * 0.4) + (m * 0.5) + ((b / 10) * 10 * 0.1)
            if score >= 75:
                risk_level.append(0)
            elif score >= 55:
                risk_level.append(1)
            else:
                risk_level.append(2)

        return pd.DataFrame({
            'attendance_percentage': attendance,
            'internal_marks': internal_marks,
            'behavior_score': behavior_score,
            'risk_level': risk_level
        })

    def predict_risk(self, attendance, marks, behavior=0):
        """Predict risk level for a student"""
        if not self.model or not self.scaler:
            return None, None
            
        # Prepare input
        input_data = np.array([[attendance, marks, behavior]])
        input_scaled = self.scaler.transform(input_data)
        
        # Predict
        risk_level = self.model.predict(input_scaled)[0]
        confidence = max(self.model.predict_proba(input_scaled)[0])
        
        risk_labels = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}
        
        return risk_labels[risk_level], confidence
    
    def generate_study_plan(self, student_data):
        """
        Generate a personalized study plan based on student's performance data
        student_data should contain subject marks and other relevant info
        """
        study_plan = {
            'weak_subjects': [],
            'strong_subjects': [],
            'recommendations': [],
            'daily_schedule': [],
            'monthly_goals': []
        }
        
        # Analyze subject performance
        subject_scores = {}
        for subject, marks in student_data.get('subject_totals', {}).items():
            if marks is not None:
                subject_scores[subject] = marks
        
        if not subject_scores:
            return study_plan
        
        # Identify weak and strong subjects (below/above 60%)
        for subject, marks in subject_scores.items():
            percentage = (marks / 100) * 100  # Assuming marks are out of 100
            if percentage < 60:
                study_plan['weak_subjects'].append({
                    'subject': subject,
                    'current_score': marks,
                    'percentage': percentage,
                    'priority': 'High' if percentage < 40 else 'Medium'
                })
            else:
                study_plan['strong_subjects'].append({
                    'subject': subject,
                    'current_score': marks,
                    'percentage': percentage
                })
        
        # Generate recommendations
        for weak_subject in study_plan['weak_subjects']:
            subject = weak_subject['subject']
            priority = weak_subject['priority']
            
            if priority == 'High':
                study_plan['recommendations'].append(f"Focus intensively on {subject} - dedicate 2-3 hours daily")
                study_plan['recommendations'].append(f"Seek additional help for {subject} from teachers or tutors")
            else:
                study_plan['recommendations'].append(f"Practice regularly in {subject} - 1-2 hours daily")
        
        # Create daily schedule
        weak_count = len(study_plan['weak_subjects'])
        if weak_count > 0:
            daily_hours = min(4, weak_count * 1.5)  # Max 4 hours study
            study_plan['daily_schedule'] = [
                "6:00 AM - 7:00 AM: Morning revision of weak subjects",
                f"7:00 PM - {7 + int(daily_hours)}:00 PM: Focused study on weak subjects",
                "Include 15-minute breaks every hour",
                "Review strong subjects briefly to maintain performance"
            ]
        
        # Monthly goals
        study_plan['monthly_goals'] = [
            "Improve weak subject scores by 15-20 points",
            "Complete all assignments on time",
            "Maintain attendance above 85%",
            "Practice previous year question papers",
            "Take regular mock tests"
        ]
        
        return study_plan