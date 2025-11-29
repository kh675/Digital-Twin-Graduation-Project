"""
Step 7: Clustering Engine - Production Script
Groups students into 7 clusters based on skills, embeddings, and academic features
"""
import pandas as pd
import numpy as np
import json
import pickle
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("STEP 7: CLUSTERING ENGINE")
print("=" * 70)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n1️⃣  Loading data...")

BASE = Path(".")

# Load features from Step 4
df_features = pd.read_csv(BASE / "models" / "features_all.csv")
print(f"   Loaded {len(df_features)} student features")

# Load embeddings from Step 1
with open(BASE / "embeddings" / "embeddings_students.pkl", "rb") as f:
    emb_students = pickle.load(f)
print(f"   Loaded student embeddings")

# Load skill gap profiles from Step 2
with open(BASE / "skill_gap_profiles" / "student_profiles.json", "r") as f:
    profiles = json.load(f)
profiles_map = {p['student_id']: p for p in profiles}
print(f"   Loaded {len(profiles)} skill gap profiles")

# Load student data
df_students = pd.read_csv(BASE / "digital_twin_students_1500_cleaned.csv", low_memory=False)
print(f"   Loaded {len(df_students)} student records")

# ============================================================================
# 2. BUILD FEATURE MATRIX
# ============================================================================
print("\n2️⃣  Building feature matrix...")

def build_feature_matrix():
    """Build comprehensive feature matrix for clustering"""
    features_list = []
    student_ids = []
    
    for _, row in df_features.iterrows():
        student_id = row['StudentID']
        student_ids.append(student_id)
        
        feature_vec = []
        
        # 1. Academic features (from features_all.csv)
        academic_cols = ['GPA', 'Attendance', 'FailedCourses', 'CompletedCourses']
        for col in academic_cols:
            if col in row:
                feature_vec.append(row[col] if pd.notna(row[col]) else 0)
        
        # 2. PCA embedding features (32 dimensions)
        emb_cols = [col for col in df_features.columns if col.startswith('emb_pca_')]
        for col in emb_cols[:32]:  # Use first 32 PCA components
            if col in row:
                feature_vec.append(row[col] if pd.notna(row[col]) else 0)
        
        # 3. Skill gap features
        profile = profiles_map.get(student_id, {})
        skill_gaps = profile.get('skill_gaps', {})
        
        # Number of missing skills
        missing_skills = skill_gaps.get('missing_skills', [])
        feature_vec.append(len(missing_skills))
        
        # Top missing skill priority (if available)
        if 'priority_scores' in skill_gaps and skill_gaps['priority_scores']:
            top_priority = max(skill_gaps['priority_scores'].values())
            feature_vec.append(top_priority)
        else:
            feature_vec.append(0)
        
        # 4. Career prediction one-hot encoding
        career_categories = ['Data', 'Machine Learning', 'Cloud', 'Cybersecurity', 
                           'Software', 'Network', 'DevOps', 'Other']
        predicted_career = row.get('predicted_career', 'Other')
        for cat in career_categories:
            feature_vec.append(1 if predicted_career == cat else 0)
        
        features_list.append(feature_vec)
    
    X = np.array(features_list)
    print(f"   Feature matrix shape: {X.shape}")
    print(f"   Features per student: {X.shape[1]}")
    
    return X, student_ids

X, student_ids = build_feature_matrix()

# ============================================================================
# 3. NORMALIZE FEATURES
# ============================================================================
print("\n3️⃣  Normalizing features...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(f"   Scaled feature matrix: {X_scaled.shape}")

# ============================================================================
# 4. CLUSTERING
# ============================================================================
print("\n4️⃣  Running clustering algorithms...")

# KMeans (Primary clustering)
n_clusters = 7
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X_scaled)

print(f"   KMeans clustering complete")
print(f"   Number of clusters: {n_clusters}")

# Cluster distribution
cluster_counts = Counter(cluster_labels)
for cluster_id, count in sorted(cluster_counts.items()):
    print(f"   Cluster {cluster_id}: {count} students")

# ============================================================================
# 5. MAP CLUSTERS TO CAREER LABELS
# ============================================================================
print("\n5️⃣  Mapping clusters to career labels...")

def map_cluster_to_career(cluster_id, student_indices):
    """Map cluster to dominant career based on predictions"""
    careers = []
    for idx in student_indices:
        student_id = student_ids[idx]
        row = df_features[df_features['StudentID'] == student_id]
        if not row.empty:
            career = row.iloc[0].get('predicted_career', 'Other')
            careers.append(career)
    
    if careers:
        most_common = Counter(careers).most_common(1)[0][0]
        return most_common
    return "Other"

# Create cluster to career mapping
cluster_career_map = {}
for cluster_id in range(n_clusters):
    cluster_indices = np.where(cluster_labels == cluster_id)[0]
    career_label = map_cluster_to_career(cluster_id, cluster_indices)
    cluster_career_map[cluster_id] = career_label
    print(f"   Cluster {cluster_id} → {career_label}")

# ============================================================================
# 6. COMPUTE SIMILAR STUDENTS
# ============================================================================
print("\n6️⃣  Computing student similarities...")

# Compute cosine similarity matrix
similarity_matrix = cosine_similarity(X_scaled)

# Find top 10 similar students for each student
similar_students = {}
for i, student_id in enumerate(student_ids):
    # Get similarity scores for this student
    similarities = similarity_matrix[i]
    
    # Get indices of top 11 (excluding self)
    top_indices = np.argsort(similarities)[::-1][1:11]
    
    # Get student IDs
    similar_ids = [student_ids[idx] for idx in top_indices]
    similar_students[student_id] = similar_ids

print(f"   Computed similarities for {len(similar_students)} students")

# ============================================================================
# 7. GENERATE CLUSTER PROFILES
# ============================================================================
print("\n7️⃣  Generating cluster profiles...")

cluster_profiles = {}

for cluster_id in range(n_clusters):
    cluster_indices = np.where(cluster_labels == cluster_id)[0]
    cluster_student_ids = [student_ids[idx] for idx in cluster_indices]
    
    # Compute cluster statistics
    cluster_features = X[cluster_indices]
    
    # Get academic stats
    cluster_students = df_students[df_students['StudentID'].isin(cluster_student_ids)]
    
    avg_gpa = cluster_students['GPA'].mean() if 'GPA' in cluster_students else 0
    avg_attendance = cluster_students['Attendance'].mean() if 'Attendance' in cluster_students else 0
    
    # Get top missing skills for cluster
    all_missing_skills = []
    for sid in cluster_student_ids:
        profile = profiles_map.get(sid, {})
        missing = profile.get('skill_gaps', {}).get('missing_skills', [])
        all_missing_skills.extend(missing[:5])  # Top 5 per student
    
    top_missing = Counter(all_missing_skills).most_common(10)
    
    cluster_profiles[cluster_career_map[cluster_id]] = {
        "cluster_id": int(cluster_id),
        "career_label": cluster_career_map[cluster_id],
        "member_count": len(cluster_student_ids),
        "avg_gpa": float(avg_gpa),
        "avg_attendance": float(avg_attendance),
        "top_missing_skills": [skill for skill, count in top_missing],
        "members": cluster_student_ids[:100]  # Store first 100 for reference
    }

print(f"   Generated profiles for {len(cluster_profiles)} clusters")

# ============================================================================
# 8. EVALUATE CLUSTERING QUALITY
# ============================================================================
print("\n8️⃣  Evaluating clustering quality...")

silhouette = silhouette_score(X_scaled, cluster_labels)
davies_bouldin = davies_bouldin_score(X_scaled, cluster_labels)

print(f"   Silhouette Score: {silhouette:.3f} (higher is better, range: -1 to 1)")
print(f"   Davies-Bouldin Score: {davies_bouldin:.3f} (lower is better)")

# ============================================================================
# 9. SAVE OUTPUTS
# ============================================================================
print("\n9️⃣  Saving outputs...")

# Create clusters.json
clusters_output = {}
for cluster_id in range(n_clusters):
    cluster_indices = np.where(cluster_labels == cluster_id)[0]
    cluster_student_ids = [student_ids[idx] for idx in cluster_indices]
    career_label = cluster_career_map[cluster_id]
    clusters_output[career_label] = cluster_student_ids

with open(BASE / "clusters.json", "w") as f:
    json.dump(clusters_output, f, indent=2)
print(f"   ✓ Saved clusters.json")

# Save similar_students.json
with open(BASE / "similar_students.json", "w") as f:
    json.dump(similar_students, f, indent=2)
print(f"   ✓ Saved similar_students.json")

# Save cluster_profiles.json
with open(BASE / "cluster_profiles.json", "w") as f:
    json.dump(cluster_profiles, f, indent=2)
print(f"   ✓ Saved cluster_profiles.json")

# Save cluster assignments
cluster_assignments = {
    student_ids[i]: {
        "cluster_id": int(cluster_labels[i]),
        "cluster_label": cluster_career_map[cluster_labels[i]]
    }
    for i in range(len(student_ids))
}

with open(BASE / "cluster_assignments.json", "w") as f:
    json.dump(cluster_assignments, f, indent=2)
print(f"   ✓ Saved cluster_assignments.json")

# ============================================================================
# 10. SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("CLUSTERING COMPLETE")
print("=" * 70)
print(f"\n✅ Clustered {len(student_ids)} students into {n_clusters} groups")
print(f"✅ Quality Score (Silhouette): {silhouette:.3f}")
print(f"✅ Generated similarity network for all students")
print(f"\nCluster Distribution:")
for career, students in clusters_output.items():
    print(f"   {career}: {len(students)} students")
print("\n" + "=" * 70)
