"""
CFPB Financial Well-Being Scale Scoring
Based on the official CFPB scoring methodology
"""

# CFPB Score Conversion Table
# Format: {total_response_value: {age_group: {admin_type: score}}}
# age_group: '18-61' or '62+'
# admin_type: 'self' or 'assisted'
CFPB_SCORE_TABLE = {
    0: {'18-61': {'self': 14, 'assisted': 16}, '62+': {'self': 14, 'assisted': 18}},
    1: {'18-61': {'self': 19, 'assisted': 21}, '62+': {'self': 20, 'assisted': 23}},
    2: {'18-61': {'self': 22, 'assisted': 24}, '62+': {'self': 24, 'assisted': 26}},
    3: {'18-61': {'self': 25, 'assisted': 27}, '62+': {'self': 26, 'assisted': 28}},
    4: {'18-61': {'self': 27, 'assisted': 29}, '62+': {'self': 29, 'assisted': 30}},
    5: {'18-61': {'self': 29, 'assisted': 31}, '62+': {'self': 31, 'assisted': 32}},
    6: {'18-61': {'self': 31, 'assisted': 33}, '62+': {'self': 33, 'assisted': 33}},
    7: {'18-61': {'self': 32, 'assisted': 34}, '62+': {'self': 35, 'assisted': 35}},
    8: {'18-61': {'self': 34, 'assisted': 36}, '62+': {'self': 36, 'assisted': 36}},
    9: {'18-61': {'self': 35, 'assisted': 38}, '62+': {'self': 38, 'assisted': 38}},
    10: {'18-61': {'self': 37, 'assisted': 39}, '62+': {'self': 39, 'assisted': 39}},
    11: {'18-61': {'self': 38, 'assisted': 40}, '62+': {'self': 41, 'assisted': 40}},
    12: {'18-61': {'self': 40, 'assisted': 42}, '62+': {'self': 42, 'assisted': 41}},
    13: {'18-61': {'self': 41, 'assisted': 43}, '62+': {'self': 44, 'assisted': 43}},
    14: {'18-61': {'self': 42, 'assisted': 44}, '62+': {'self': 45, 'assisted': 44}},
    15: {'18-61': {'self': 44, 'assisted': 45}, '62+': {'self': 46, 'assisted': 45}},
    16: {'18-61': {'self': 45, 'assisted': 47}, '62+': {'self': 48, 'assisted': 46}},
    17: {'18-61': {'self': 46, 'assisted': 48}, '62+': {'self': 49, 'assisted': 47}},
    18: {'18-61': {'self': 47, 'assisted': 49}, '62+': {'self': 50, 'assisted': 48}},
    19: {'18-61': {'self': 49, 'assisted': 50}, '62+': {'self': 52, 'assisted': 49}},
    20: {'18-61': {'self': 50, 'assisted': 52}, '62+': {'self': 53, 'assisted': 50}},
    21: {'18-61': {'self': 51, 'assisted': 53}, '62+': {'self': 54, 'assisted': 52}},
    22: {'18-61': {'self': 52, 'assisted': 54}, '62+': {'self': 56, 'assisted': 53}},
    23: {'18-61': {'self': 54, 'assisted': 55}, '62+': {'self': 57, 'assisted': 54}},
    24: {'18-61': {'self': 55, 'assisted': 57}, '62+': {'self': 58, 'assisted': 55}},
    25: {'18-61': {'self': 56, 'assisted': 58}, '62+': {'self': 60, 'assisted': 56}},
    26: {'18-61': {'self': 58, 'assisted': 59}, '62+': {'self': 61, 'assisted': 57}},
    27: {'18-61': {'self': 59, 'assisted': 60}, '62+': {'self': 63, 'assisted': 58}},
    28: {'18-61': {'self': 60, 'assisted': 62}, '62+': {'self': 64, 'assisted': 60}},
    29: {'18-61': {'self': 62, 'assisted': 63}, '62+': {'self': 66, 'assisted': 61}},
    30: {'18-61': {'self': 63, 'assisted': 65}, '62+': {'self': 67, 'assisted': 62}},
    31: {'18-61': {'self': 65, 'assisted': 66}, '62+': {'self': 69, 'assisted': 64}},
    32: {'18-61': {'self': 66, 'assisted': 68}, '62+': {'self': 71, 'assisted': 65}},
    33: {'18-61': {'self': 68, 'assisted': 70}, '62+': {'self': 73, 'assisted': 67}},
    34: {'18-61': {'self': 69, 'assisted': 71}, '62+': {'self': 75, 'assisted': 68}},
    35: {'18-61': {'self': 71, 'assisted': 73}, '62+': {'self': 77, 'assisted': 70}},
    36: {'18-61': {'self': 73, 'assisted': 76}, '62+': {'self': 79, 'assisted': 72}},
    37: {'18-61': {'self': 75, 'assisted': 78}, '62+': {'self': 82, 'assisted': 75}},
    38: {'18-61': {'self': 78, 'assisted': 81}, '62+': {'self': 84, 'assisted': 77}},
    39: {'18-61': {'self': 81, 'assisted': 85}, '62+': {'self': 88, 'assisted': 81}},
    40: {'18-61': {'self': 86, 'assisted': 91}, '62+': {'self': 95, 'assisted': 87}},
}

def calculate_cfpb_score(responses: dict, age: int, self_administered: bool = True) -> dict:
    """
    Calculate CFPB Financial Well-Being Score
    
    Args:
        responses: Dictionary with question numbers (1-10) as keys and response values (0-4) as values
        age: User's age
        self_administered: Whether questionnaire was self-administered (default: True)
    
    Returns:
        Dictionary with total_response_value and final_score
    """
    # Part 1: Questions 1-6 (How well does this describe you?)
    # Questions 1, 2, 4: Positive (4=Completely, 0=Not at all)
    # Questions 3, 5, 6: Negative (reversed: 0=Completely, 4=Not at all)
    
    # Part 2: Questions 7-10 (How often does this apply?)
    # Question 8: Positive (4=Always, 0=Never)
    # Questions 7, 9, 10: Negative (reversed: 0=Always, 4=Never)
    
    total_response_value = 0
    
    # Part 1 scoring
    for q in [1, 2, 4]:  # Positive questions
        if q in responses:
            total_response_value += responses[q]
    
    for q in [3, 5, 6]:  # Negative questions (reversed)
        if q in responses:
            # Reverse: if they said "Completely" (4), that's bad (0 points)
            # If they said "Not at all" (0), that's good (4 points)
            total_response_value += (4 - responses[q])
    
    # Part 2 scoring
    if 8 in responses:  # Positive question
        total_response_value += responses[8]
    
    for q in [7, 9, 10]:  # Negative questions (reversed)
        if q in responses:
            total_response_value += (4 - responses[q])
    
    # Clamp to valid range
    total_response_value = max(0, min(40, total_response_value))
    
    # Determine age group
    age_group = '62+' if age >= 62 else '18-61'
    
    # Determine administration type
    admin_type = 'self' if self_administered else 'assisted'
    
    # Look up final score
    if total_response_value in CFPB_SCORE_TABLE:
        final_score = CFPB_SCORE_TABLE[total_response_value][age_group][admin_type]
    else:
        # Interpolate for values not in table (shouldn't happen, but safety)
        final_score = 50  # Default middle score
    
    return {
        'total_response_value': total_response_value,
        'final_score': final_score,
        'age_group': age_group,
        'admin_type': admin_type
    }

def get_cfpb_rating(score: float) -> str:
    """Get rating based on CFPB score (0-100 scale)"""
    if score >= 80:
        return "Excellent"
    elif score >= 70:
        return "Very Good"
    elif score >= 60:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Improvement"

