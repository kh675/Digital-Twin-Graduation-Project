import pickle
import numpy as np

try:
    with open("embeddings/embeddings_students.pkl", "rb") as f:
        data = pickle.load(f)
        embeddings = data['embeddings']
        print(f"Embeddings type: {type(embeddings)}")
        if isinstance(embeddings, np.ndarray):
            print(f"Shape: {embeddings.shape}")
        elif isinstance(embeddings, list):
            print(f"Length: {len(embeddings)}")
            print(f"First item type: {type(embeddings[0])}")
            
except Exception as e:
    print(f"Error: {e}")
