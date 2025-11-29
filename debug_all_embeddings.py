import pickle
import os
import sys

files = ["embeddings_students.pkl", "embeddings_courses.pkl", "embeddings_jobs.pkl"]

with open("debug_log.txt", "w") as log:
    for filename in files:
        path = os.path.join("embeddings", filename)
        log.write(f"\nChecking {filename}...\n")
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
                log.write(f"Type: {type(data)}\n")
                if isinstance(data, dict):
                    log.write(f"Keys: {list(data.keys())}\n")
                    if 'embeddings' in data:
                        log.write(f"Embeddings shape: {getattr(data['embeddings'], 'shape', 'No shape')}\n")
                else:
                    log.write("Not a dict\n")
        except Exception as e:
            log.write(f"Error: {e}\n")
