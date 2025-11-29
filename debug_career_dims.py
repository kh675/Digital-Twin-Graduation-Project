import pandas as pd
import pickle
import numpy as np
from pathlib import Path

BASE = Path(".")

# Load data
print("Loading data...")
df = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)
print(f"Students: {len(df)}")

# Load embeddings
with open(BASE / "embeddings" / "embeddings_students.pkl", "rb") as f:
    emb_data = pickle.load(f)
    student_ids = emb_data['ids']
    student_embeddings = np.vstack(emb_data['embeddings'])

print(f"Embedding shape: {student_embeddings.shape}")
print(f"Number of student IDs: {len(student_ids)}")
print(f"DataFrame shape: {df.shape}")

# Check alignment
emb_map = {str(sid): emb for sid, emb in zip(student_ids, student_embeddings)}
emb_matrix = np.vstack([
    emb_map.get(str(sid), np.zeros(student_embeddings.shape[1])) 
    for sid in df['StudentID']
])

print(f"Aligned embedding matrix shape: {emb_matrix.shape}")
print(f"Max PCA components: min(32, {emb_matrix.shape[1]}, {emb_matrix.shape[0] - 1})")
n_components = min(32, emb_matrix.shape[1], emb_matrix.shape[0] - 1)
print(f"Will use {n_components} components")
