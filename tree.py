from flask import Flask, render_template, request
import pandas as pd
from textblob import TextBlob  # TextBlob for sentiment analysis
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

# Load data
df = pd.read_csv('dataset_rec.csv', encoding='latin1')

# Sample sentiment analysis function using TextBlob
def analyze_sentiment(review):
    blob = TextBlob(review)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

def preprocess_place_name(place_name):
    # Extract only the first part before ","
    return place_name.split(',')[0].strip()

def recommend_locations_with_review(place_name, start_date, end_date, type_, budget, df):
    # Preprocess the place_name
    place_name = preprocess_place_name(place_name)

    # Calculate duration in days
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    duration = (end_date - start_date).days
    
    # Filter DataFrame based on user input
    filtered_df = df[(df['Place Name'] == place_name) & (df['Type'] == type_)]
    # print("Filtered DataFrame:")
    # print(filtered_df)
    
    # Print unique values in the "Place Name" column for debugging
    # print(df['Place Name'].unique())
    
    # Extract unique tourist locations, their reviews, and costs
    unique_locations = filtered_df['Tourist Location'].tolist()
    locations_reviews = filtered_df.set_index('Tourist Location')['Review'].to_dict()
    locations_budget = filtered_df.set_index('Tourist Location')['Budget'].to_dict()
    locations_type = filtered_df.set_index('Tourist Location')['Type'].to_dict()
    
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
                    trip_type = locations_type[location]
                    recommendation = f"{location} ({trip_type})"
                    recommendations.append((recommendation, sentiment_score))
                    remaining_budget -= locations_budget[location]
                    unique_locations.remove(location)
                    break
                else:
                    continue
        else:
            recommendations.append(("No more locations available", 0))
    
    # Sort recommendations based on review scores in descending order
    recommendations.sort(key=lambda x: x[1], reverse=True)
    sorted_recommendations = [rec[0] for rec in recommendations]
    
    return sorted_recommendations, budget - remaining_budget

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        # Get form data
        place_name = request.form['place_name']
        start_date = request.form['startDate']
        end_date = request.form['endDate']
        # print("Destination form:", place_name)  
        
        # Debugging: Print the DataFrame to inspect the data
        # print("DataFrame head:")
        # print(df.head())
        
        # Define the trip_type and budget variables
        trip_type = request.form['tripType']
        budget = float(request.form['budget'])
        
        # Call recommendation function
        recommendations, remaining_budget = recommend_locations_with_review(place_name, start_date, end_date, trip_type, budget, df)
        # print("Recommendations:", recommendations)
        # print("Remaining budget:", remaining_budget)
        
        # Render template with recommendations
        return render_template('recommendations.html', recommendations=recommendations, remaining_budget=remaining_budget)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
