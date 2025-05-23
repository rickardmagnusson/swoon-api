import pandas as pd
import ast
import os
from datetime import datetime
from flask import Flask, request, jsonify
app = Flask(__name__)

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

@app.route('/match', methods=['POST'])
def match():
    user_data = request.json

    required_fields = ['gender', 'sexual_orientation']
    for field in required_fields:
        if field not in user_data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    target_gender = user_data['gender']
    target_orientation = user_data['sexual_orientation']

    print(f"Incoming user: gender={target_gender}, interested in={target_orientation}")

    if target_orientation == 'interested in women':
        desired_gender = 'woman'
    elif target_orientation == 'interested in men':
        desired_gender = 'man'
    else:
        print("Unknown orientation, returning empty list.")
        return jsonify([])

    filtered_df = df[
        (df['gender'] == desired_gender) &
        (df['sexual_orientation'] == f'interested in {target_gender}')
    ].copy()

    print(f"Filtered candidates: {len(filtered_df)}")
    print(filtered_df[['name', 'gender', 'sexual_orientation']].to_string())

    if filtered_df.empty:
        print("No matches found after gender/orientation filter.")
        return jsonify([])

    scores = filtered_df.apply(lambda row: advanced_score_match(row, user_data), axis=1).astype(int)
    filtered_df['match_score'] = scores
    top_matches = filtered_df.sort_values(by='match_score', ascending=False).head(3)

    results = top_matches[['name', 'match_score']].to_dict(orient='records')
    print("Top matches returned:", results)
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
