import pandas as pd
from textblob import TextBlob  # TextBlob for sentiment analysis

# Load data
df = pd.read_csv('destination_data.csv', encoding='latin1')

# Sample sentiment analysis function using TextBlob
def analyze_sentiment(review):
    blob = TextBlob(review)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

def recommend_locations_with_review(place_name, duration, type_, budget, df):
    # Filter DataFrame based on user input
    filtered_df = df[(df['Place Name'] == place_name) & (df['Type'] == type_)]
    
    # Extract unique tourist locations, their reviews, and costs
    unique_locations = filtered_df['Tourist Location'].tolist()
    locations_reviews = filtered_df.set_index('Tourist Location')['Review'].to_dict()
    locations_budget = filtered_df.set_index('Tourist Location')['Budget'].to_dict()
    
    # Generate recommendation with review scores for each day
    remaining_budget = budget
    recommendations = []
    for i in range(duration):
        if remaining_budget <= 0:
            recommendations.append(("No more budget for additional locations", 0))
            continue
        
        if unique_locations:
            for location in unique_locations:
                if remaining_budget >= locations_budget[location]:
                    review = locations_reviews.get(location, '')
                    sentiment_score = analyze_sentiment(review)
                    recommendations.append((location, sentiment_score))
                    remaining_budget -= locations_budget[location]
                    unique_locations.remove(location)
                else:
                    continue
        else:
            recommendations.append(("No more locations available", 0))
    
    # Sort recommendations based on review scores in descending order
    recommendations.sort(key=lambda x: x[1], reverse=True)
    sorted_recommendations = [rec[0] for rec in recommendations]
    
    return sorted_recommendations, budget - remaining_budget

# Example usage
place_name = 'Agra, Uttar Pradesh'
duration = 4
type_ = 'Historical'
budget = 4000  # Example budget
recommendations, remaining_budget = recommend_locations_with_review(place_name, duration, type_, budget, df)
for i, recommendation in enumerate(recommendations, start=1):
    print(f"Day {i}): {recommendation}")
print(f"Total budget in this trip plan: {remaining_budget}")
