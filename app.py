from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import pandas as pd
from textblob import TextBlob  # TextBlob for sentiment analysis
from datetime import datetime

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)

df = pd.read_csv('dataset_rec.csv', encoding='latin1')
# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tourmate'

mysql = MySQL(app)

# Function to add user to the database
def add_user_to_database(name, email, password, user_type):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)", (name, email, password, user_type))
    mysql.connection.commit()
    cursor.close()

# Route for handling the form submission
@app.route('/signup', methods=['POST'])
def process_signup_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_type = request.form['type']

        if password != confirm_password:
            return 'Passwords do not match'

        add_user_to_database(name, email, password, user_type)

        return redirect('/login')  

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error=None)  # Pass None as the error initially
    
    elif request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            username = request.form['email']
            password = request.form['password']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            try:
                cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (username, password,))
                user = cursor.fetchone()

                if user:
                    session['user_id'] = user['id']  # Store user ID in session
                    session['logged_in'] = True
                    print("User ID:", user['id'])
                    return redirect('/') 
                else:
                    return render_template('login.html', error='Invalid username/password')
            except Exception as e:
                return render_template('login.html', error='An error occurred: {}'.format(str(e)))
            finally:
                cursor.close()
        else:
            return render_template('login.html', error='Missing email or password in form data')

@app.route('/logout')
def logout():
    # Clear the session when the user logs out
    session.clear()
    return redirect('/')

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
    locations_popularity = filtered_df.set_index('Tourist Location')['Popularity'].to_dict()
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
                    popularity = locations_popularity.get(location, '')
                    trip_type = locations_type[location]
                    recommendation = {"location": f"{location}", "type": f"{trip_type}", "popularity": popularity, "review": review, "budget": locations_budget[location]}
                    recommendations.append(recommendation)
                    remaining_budget -= locations_budget[location]
                    unique_locations.remove(location)
                    break
                else:
                    continue
        else:
            recommendations.append({"location": "No more locations available", "popularity": 0, "review": ""})
    
    # Sort recommendations based on popularity in descending order
    recommendations.sort(key=lambda x: x["popularity"], reverse=True)
    
    return recommendations, budget - remaining_budget

# Function to save trip details for a specific user to the database
def save_trip_details(user_id, place_name, start_date, end_date, trip_type, budget):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO trips (user_id, place_name, start_date, end_date, trip_type, budget) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, place_name, start_date, end_date, trip_type, budget))
    mysql.connection.commit()
    cursor.close()

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        # Get form data
        place_name = request.form['place_name']
        start_date = request.form['startDate']
        end_date = request.form['endDate']
        
        # Define the trip_type and budget variables
        trip_type = request.form['tripType']
        budget = float(request.form['budget'])
        
        # Get user ID from session
        user_id = session.get('user_id')
        
        # Check if user is logged in
        if user_id:
            # Save trip details for the specific user
            save_trip_details(user_id, place_name, start_date, end_date, trip_type, budget)
            
            # Call recommendation function
            recommendations, remaining_budget = recommend_locations_with_review(place_name, start_date, end_date, trip_type, budget, df)
            
            # Render template with recommendations
            return render_template('recommendations.html', recommendations=recommendations, remaining_budget=remaining_budget)
        else:
            # Redirect to login if user is not logged in
            return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
