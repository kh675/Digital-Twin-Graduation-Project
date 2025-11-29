from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np

class SkillEmbeddingBuilder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text_list(self, texts):
        # Embed a list of texts into vectors
        return self.model.encode(texts, show_progress_bar=True)

    def build_student_skill_vector(self, student_data):
        # Combine relevant student fields into one text per student
        combined_texts = (
            student_data['Skills'].fillna('') + ' ' +
            student_data['TechnicalSkills'].fillna('') + ' ' +
            student_data['SoftSkills'].fillna('') + ' ' +
            student_data['CoursesCompleted'].fillna('') + ' ' +
            student_data['MajorCourseGrades'].fillna('')  # Using MajorCourseGrades as it contains grade information
        )
        return self.embed_text_list(combined_texts.tolist())

    def build_job_skill_vector(self, job_data):
        # Safely get each column with .get() and handle case where job_data might be a Series
        job_title = job_data.get('job_title', '') if hasattr(job_data, 'get') else ''
        skills = job_data.get('skills_required', '') if hasattr(job_data, 'get') else ''
        certs = job_data.get('certificates_required', '') if hasattr(job_data, 'get') else ''
        responsibilities = job_data.get('responsibilities', '') if hasattr(job_data, 'get') else ''
        
        # Combine all available fields
        combined_texts = f"{job_title} {skills} {certs} {responsibilities}"
        
        # Handle both Series and single row cases
        if hasattr(combined_texts, 'tolist'):
            return self.embed_text_list(combined_texts.tolist())
        return self.embed_text_list([combined_texts])

    def build_course_skill_vector(self, course_data):
        # Safely get each column with .get()
        desc = course_data.get('course_description', '') if hasattr(course_data, 'get') else ''
        skills = course_data.get('skills_gained', '') if hasattr(course_data, 'get') else ''
        level = course_data.get('level', '') if hasattr(course_data, 'get') else ''
        
        # Combine all available fields
        combined_texts = f"{desc} {skills} {level}"
        
        # Handle both Series and single row cases
        if hasattr(combined_texts, 'tolist'):
            return self.embed_text_list(combined_texts.tolist())
        return self.embed_text_list([combined_texts])

    def build_student_interest_vector(self, interest_data):
        # Safely get each column with .get()
        interests = interest_data.get('UserInterests', '') if hasattr(interest_data, 'get') else ''
        track = interest_data.get('PreferredTrack', '') if hasattr(interest_data, 'get') else ''
        
        # Combine all available fields
        combined_texts = f"{interests} {track}"
        
        # Handle both Series and single row cases
        if hasattr(combined_texts, 'tolist'):
            return self.embed_text_list(combined_texts.tolist())
        return self.embed_text_list([combined_texts])

# Example usage:
# student_df, job_df, course_df, interest_df are pandas DataFrames loaded with your cleaned data
# builder = SkillEmbeddingBuilder()
# student_vectors = builder.build_student_skill_vector(student_df)
# job_vectors = builder.build_job_skill_vector(job_df)
# course_vectors = builder.build_course_skill_vector(course_df)
# interest_vectors = builder.build_student_interest_vector(interest_df)

# Save or use the vectors as needed
