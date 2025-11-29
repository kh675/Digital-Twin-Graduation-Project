"""
Verification script for Skill Gap Analysis results.
Validates profiles, similarity scores, and skill consistency.
"""

import os
import sys
import json
import numpy as np
from datetime import datetime

# Configure UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def print_test(text, passed):
    """Print test result"""
    status = "[PASS]" if passed else "[FAIL]"
    symbol = "OK" if passed else "X"
    print(f"{status} {text} ... {symbol}")


def load_profiles():
    """Load generated profiles"""
    print_header("LOADING PROFILES")
    
    profiles_path = 'skill_gap_profiles/student_profiles.json'
    
    if not os.path.exists(profiles_path):
        print(f"[ERROR] Profiles file not found: {profiles_path}")
        print("Please run 'python skill_gap_analysis.py' first!")
        sys.exit(1)
    
    with open(profiles_path, 'r', encoding='utf-8') as f:
        profiles = json.load(f)
    
    print(f"[*] Loaded {len(profiles)} student profiles")
    return profiles


def verify_profile_completeness(profiles):
    """Verify all profiles are complete"""
    print_header("TEST 1: PROFILE COMPLETENESS")
    
    required_fields = [
        'student_id', 'student_name', 'department', 'gpa',
        'current_skills', 'best_job_matches', 'skill_gaps',
        'recommendations'
    ]
    
    all_complete = True
    
    for i, profile in enumerate(profiles):
        for field in required_fields:
            if field not in profile:
                print(f"[FAIL] Profile {i} missing field: {field}")
                all_complete = False
    
    print_test(f"All {len(profiles)} profiles have required fields", all_complete)
    
    # Check job matches
    has_matches = all(len(p['best_job_matches']) > 0 for p in profiles)
    print_test("All profiles have job matches", has_matches)
    
    # Check skill gaps
    has_gaps = all('missing_skills' in p['skill_gaps'] for p in profiles)
    print_test("All profiles have skill gap analysis", has_gaps)
    
    return all_complete and has_matches and has_gaps


def verify_similarity_scores(profiles):
    """Verify similarity scores are valid"""
    print_header("TEST 2: SIMILARITY SCORE VALIDATION")
    
    all_valid = True
    min_score = 1.0
    max_score = 0.0
    all_scores = []
    
    for profile in profiles:
        for match in profile['best_job_matches']:
            score = match['similarity_score']
            all_scores.append(score)
            
            if score < 0 or score > 1:
                print(f"[FAIL] Invalid score for {profile['student_id']}: {score}")
                all_valid = False
            
            min_score = min(min_score, score)
            max_score = max(max_score, score)
    
    print_test("All similarity scores in [0, 1] range", all_valid)
    print(f"    - Min score: {min_score:.4f}")
    print(f"    - Max score: {max_score:.4f}")
    print(f"    - Mean score: {np.mean(all_scores):.4f}")
    print(f"    - Std dev: {np.std(all_scores):.4f}")
    
    # Check match percentages
    percentages_valid = all(
        0 <= match['match_percentage'] <= 100
        for profile in profiles
        for match in profile['best_job_matches']
    )
    print_test("All match percentages in [0, 100] range", percentages_valid)
    
    return all_valid and percentages_valid


def verify_skill_consistency(profiles):
    """Verify skill lists are consistent"""
    print_header("TEST 3: SKILL CONSISTENCY")
    
    no_duplicates = True
    all_lowercase = True
    
    for profile in profiles:
        # Check current skills
        skills = profile['current_skills']
        if len(skills) != len(set(skills)):
            print(f"[FAIL] Duplicate skills in {profile['student_id']}")
            no_duplicates = False
        
        # Check lowercase
        if any(s != s.lower() for s in skills):
            print(f"[FAIL] Non-lowercase skills in {profile['student_id']}")
            all_lowercase = False
        
        # Check skill gaps
        missing = profile['skill_gaps']['missing_skills']
        matching = profile['skill_gaps']['matching_skills']
        
        if len(missing) != len(set(missing)):
            print(f"[FAIL] Duplicate missing skills in {profile['student_id']}")
            no_duplicates = False
        
        if len(matching) != len(set(matching)):
            print(f"[FAIL] Duplicate matching skills in {profile['student_id']}")
            no_duplicates = False
    
    print_test("No duplicate skills in any list", no_duplicates)
    print_test("All skills are lowercase", all_lowercase)
    
    return no_duplicates and all_lowercase


def verify_top_matches_quality(profiles):
    """Verify job matches are ranked correctly"""
    print_header("TEST 4: TOP MATCHES QUALITY")
    
    correctly_ranked = True
    
    for profile in profiles:
        matches = profile['best_job_matches']
        
        # Check if sorted by similarity score (descending)
        scores = [m['similarity_score'] for m in matches]
        if scores != sorted(scores, reverse=True):
            print(f"[FAIL] Matches not sorted for {profile['student_id']}")
            correctly_ranked = False
    
    print_test("All job matches correctly ranked by similarity", correctly_ranked)
    
    # Check average number of matches
    avg_matches = np.mean([len(p['best_job_matches']) for p in profiles])
    print(f"    - Average matches per student: {avg_matches:.1f}")
    
    return correctly_ranked


def display_sample_profiles(profiles, num_samples=5):
    """Display sample profiles for manual review"""
    print_header(f"TEST 5: SAMPLE PROFILE REVIEW ({num_samples} STUDENTS)")
    
    # Select random samples
    sample_indices = np.random.choice(len(profiles), num_samples, replace=False)
    
    for idx in sample_indices:
        profile = profiles[idx]
        
        print(f"\n{'─'*70}")
        print(f"Student: {profile['student_name']} ({profile['student_id']})")
        print(f"Department: {profile['department']} | GPA: {profile['gpa']}")
        print(f"Current Skills ({len(profile['current_skills'])}): {', '.join(profile['current_skills'][:5])}...")
        
        print(f"\nTop 3 Job Matches:")
        for i, match in enumerate(profile['best_job_matches'][:3], 1):
            print(f"  {i}. {match['job_title']} at {match['company']}")
            print(f"     Match: {match['match_percentage']:.1f}% | Level: {match['job_level']}")
        
        print(f"\nSkill Gap Analysis:")
        print(f"  - Missing Skills ({len(profile['skill_gaps']['missing_skills'])}): {', '.join(profile['skill_gaps']['missing_skills'][:5])}...")
        print(f"  - Matching Skills ({len(profile['skill_gaps']['matching_skills'])}): {', '.join(profile['skill_gaps']['matching_skills'][:5])}...")
        
        print(f"\nTop Priority Skills:")
        for skill_info in profile['skill_gaps']['priority_skills'][:3]:
            print(f"  - {skill_info['skill']}: Priority {skill_info['priority_score']}/10 (in {skill_info['appears_in_jobs']} jobs)")
        
        print(f"\nRecommendations:")
        print(f"  - Immediate Focus: {', '.join(profile['recommendations']['immediate_focus'])}")
        print(f"  - Career Paths: {', '.join(profile['recommendations']['career_paths'])}")
    
    print(f"\n{'─'*70}")
    return True


def generate_verification_report(profiles, test_results):
    """Generate verification summary report"""
    print_header("VERIFICATION SUMMARY")
    
    all_passed = all(test_results.values())
    
    print(f"Total Profiles Verified: {len(profiles)}")
    print(f"Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print("Test Results:")
    for test_name, passed in test_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}")
    
    print(f"\nOverall Status: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    # Statistics
    print(f"\nProfile Statistics:")
    print(f"  - Avg skills per student: {np.mean([len(p['current_skills']) for p in profiles]):.1f}")
    print(f"  - Avg missing skills: {np.mean([len(p['skill_gaps']['missing_skills']) for p in profiles]):.1f}")
    print(f"  - Avg matching skills: {np.mean([len(p['skill_gaps']['matching_skills']) for p in profiles]):.1f}")
    print(f"  - Avg match percentage: {np.mean([m['match_percentage'] for p in profiles for m in p['best_job_matches']]):.1f}%")
    
    # Department breakdown
    dept_counts = {}
    for profile in profiles:
        dept = profile['department']
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    print(f"\nDepartment Distribution:")
    for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {dept}: {count} students")
    
    return all_passed


def main():
    """Main verification function"""
    print_header("SKILL GAP ANALYSIS VERIFICATION")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Load profiles
        profiles = load_profiles()
        
        # Run verification tests
        test_results = {
            'Profile Completeness': verify_profile_completeness(profiles),
            'Similarity Score Validation': verify_similarity_scores(profiles),
            'Skill Consistency': verify_skill_consistency(profiles),
            'Top Matches Quality': verify_top_matches_quality(profiles),
            'Sample Profile Review': display_sample_profiles(profiles)
        }
        
        # Generate report
        all_passed = generate_verification_report(profiles, test_results)
        
        print_header("VERIFICATION COMPLETE!")
        
        if all_passed:
            print("[SUCCESS] All verification tests passed!")
            print("\nYou can now:")
            print("  1. Review profiles in 'skill_gap_profiles/' directory")
            print("  2. Proceed to Step 3: Recommendation Engine")
        else:
            print("[WARNING] Some tests failed. Please review the results above.")
        
        print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
