import pandas as pd
import ast
import os
from datetime import datetime

# Load your database
df = pd.read_csv('Database.csv')

# Parse string fields into actual lists
def parse_and_clean_list(cell):
    try:
        parsed = ast.literal_eval(cell)
        if isinstance(parsed, list):
            return [item.strip() for item in parsed]
        return []
    except:
        return []

list_columns = ['traits', 'must_haves', 'deal_breakers', 'desired_qualities', 'life_values', 'love_languages']
for col in list_columns:
    df[col] = df[col].apply(parse_and_clean_list)

# Define the scoring function
def advanced_score_match(row, user_data):
    def get_set_score(user_list, match_list, full_weight=10, partial_weight=5, min_match=3):
        matches = len(set(user_list) & set(match_list))
        if matches >= min_match:
            return full_weight
        elif matches > 0:
            return partial_weight
        return -3

    score = 0
    score += 10 if row['relationship_goal'].strip().lower() == user_data['relationship_goal'].strip().lower() else 0
    trait_diff = len(set(row['traits']) - set(user_data['traits']))
    score += 10 if trait_diff >= 2 else 5 if trait_diff == 1 else 0
    score += get_set_score(user_data['must_haves'], row['must_haves'], 15, 7)
    score -= 20 * len(set(row['deal_breakers']) & set(user_data['deal_breakers']))
    score += get_set_score(user_data['desired_qualities'], row['desired_qualities'], 10, 5)
    score += get_set_score(user_data['life_values'], row['life_values'], 10, 5)
    score += 10 if row['conflict_resolution'].strip().lower() == user_data['conflict_resolution'].strip().lower() else -5
    score += get_set_score(user_data['love_languages'], row['love_languages'], 12, 6)
    score += 8 if row['weekend_preference'].strip().lower() == user_data['weekend_preference'].strip().lower() else -3
    score += 8 if row['planning_style'].strip().lower() != user_data['planning_style'].strip().lower() else 0
    score += 8 if row['activity_level'].strip().lower() == user_data['activity_level'].strip().lower() else -2
    return score

# Example user data (replace with actual input)
user_profile = {
    "relationship_goal": "long-term",
    "traits": ["Witty", "Quick", "Good-looking"],
    "must_haves": ["Honesty", "Down-to-earth"],
    "deal_breakers": ["Neuroticism", "Bad hygiene"],
    "desired_qualities": ["Respect for space", "Open communication"],
    "life_values": ["Personal space", "Trust", "Independence"],
    "conflict_resolution": "Deal with it head-on",
    "love_languages": ["Words of affirmation", "Receiving gifts"],
    "weekend_preference": "Go out—camping and outdoors",
    "planning_style": "Balanced",
    "activity_level": "Pretty active"
}

# Score and sort
df['match_score'] = df.apply(lambda row: advanced_score_match(row, user_profile), axis=1)
df_sorted = df.sort_values(by='match_score', ascending=False)
print(df_sorted[['name', 'match_score']].head(10))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # default for local testing
    app.run(host='0.0.0.0', port=port)
