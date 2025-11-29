import pickle
import pandas as pd

try:
    with open("embeddings/embeddings_jobs.pkl", "rb") as f:
        data = pickle.load(f)
        ids = data['ids']
        print(f"IDs type: {type(ids)}")
        if len(ids) > 0:
            print(f"First ID type: {type(ids[0])}")
            print(f"First 5 IDs: {ids[:5]}")
        
    df = pd.read_csv("egypt_jobs_full_1500_cleaned.csv")
    print(f"DataFrame length: {len(df)}")
except Exception as e:
    print(f"Error: {e}")
