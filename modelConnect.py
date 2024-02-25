from flask import Flask, render_template, request, jsonify
import pandas as pd
from textblob import TextBlob  # TextBlob for sentiment analysis

app = Flask(__name__, static_url_path='/static')


@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    # Handle form data submitted via POST request
    data = request.form

    destination = request.form.get('destination')
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')
    trip_type = request.form.get('tripType')
    budget = request.form.get('budget')
    print(destination)
    # Process the data as needed

    # Return a response (for example, a JSON response)
    return jsonify({'message': 'Form data received successfully!'})

# Load data
df = pd.read_csv('static\js\destinations.csv', encoding='latin1')

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
                else:
                    continue
        else:
            recommendations.append(("No more locations available", 0))
    
    # Sort recommendations based on review scores in descending order
    recommendations.sort(key=lambda x: x[1], reverse=True)
    sorted_recommendations = [rec[0] for rec in recommendations]
    
    return sorted_recommendations, budget - remaining_budget



if __name__ == "__main__":
    app.run(debug=True)
