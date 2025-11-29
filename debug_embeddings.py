import pickle
import os

try:
    with open("embeddings/embeddings_students.pkl", "rb") as f:
        data = pickle.load(f)
        print(f"Type: {type(data)}")
        if hasattr(data, 'shape'):
            print(f"Shape: {data.shape}")
        elif isinstance(data, dict):
            print(f"Keys: {list(data.keys())[:5]}")
        elif isinstance(data, list):
            print(f"Length: {len(data)}")
            print(f"First item type: {type(data[0])}")
except Exception as e:
    print(f"Error: {e}")
