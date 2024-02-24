
# app.py

from flask import Flask, render_template, request
import data_processing
import recommendation_system

app = Flask(__name__)

# Load data
destination_data, user_info_data, user_ratings_data = data_processing.load_data()

# Merge and process data
final_data = data_processing.merge_data(destination_data, user_info_data, user_ratings_data)
final_data = data_processing.feature_engineering(final_data)

# Build recommendation system
user_recommendations = recommendation_system.user_item_collaborative_filtering(final_data)
content_based_recommendations = recommendation_system.content_based_filtering(final_data)
hybrid_recommendations = recommendation_system.hybrid_model(user_recommendations, content_based_recommendations)

# Flask routes and other app logic...
