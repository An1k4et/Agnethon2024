# recommendation_system.py

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def placename_filtering(final_data, selected_placename):
    # Filter destinations based on the selected placename
    filtered_destinations = final_data[final_data['placename'] == selected_placename]
    return filtered_destinations

def type_based_filtering(final_data, selected_type=None):
    # Filter destinations based on the selected type (if provided)
    if selected_type:
        filtered_destinations = final_data[final_data['type'] == selected_type]
    else:
        filtered_destinations = final_data.copy()  # No type filter

    return filtered_destinations

def popularity_based_filtering(final_data, popularity_level=None):
    # Filter destinations based on the specified popularity level (if provided)
    if popularity_level:
        if popularity_level == 'High':
            filtered_destinations = final_data[final_data['popularity'] >= final_data['popularity'].quantile(0.75)]
        elif popularity_level == 'Medium':
            filtered_destinations = final_data[(final_data['popularity'] >= final_data['popularity'].quantile(0.25)) & 
                                               (final_data['popularity'] < final_data['popularity'].quantile(0.75))]
        else:
            filtered_destinations = final_data[final_data['popularity'] < final_data['popularity'].quantile(0.25)]
    else:
        filtered_destinations = final_data.copy()  # No popularity filter

    return filtered_destinations

def rating_based_filtering(final_data, min_rating=None):
    # Filter destinations based on the minimum rating (if provided)
    if min_rating is not None:
        filtered_destinations = final_data[final_data['average_rating'] >= min_rating]
    else:
        filtered_destinations = final_data.copy()  # No rating filter

    return filtered_destinations

def tourist_location_recommendation(final_data, selected_tourist_location=None):
    # Provide a list of tourist locations for the user to choose from
    tourist_locations = final_data[['destination_id', 'destination_name', 'type', 'popularity', 'average_rating']]
    tourist_locations = tourist_locations.drop_duplicates(subset='destination_id')  # Remove duplicates
    
    # Filter based on the selected tourist location (if provided)
    if selected_tourist_location:
        filtered_tourist_locations = tourist_locations[tourist_locations['destination_name'] == selected_tourist_location]
    else:
        filtered_tourist_locations = tourist_locations.copy()  # No tourist location filter

    return filtered_tourist_locations
