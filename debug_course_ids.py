import pickle
import pandas as pd

try:
    with open("embeddings/embeddings_courses.pkl", "rb") as f:
        data = pickle.load(f)
        ids = data['ids']
        print(f"IDs length: {len(ids)}")
        print(f"First 5 IDs: {ids[:5]}")
        print(f"Last 5 IDs: {ids[-5:]}")
        
    df = pd.read_csv("digital_twin_courses_1500_cleaned.csv")
    print(f"DataFrame length: {len(df)}")
except Exception as e:
    print(f"Error: {e}")
