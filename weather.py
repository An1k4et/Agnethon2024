from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Weather API's API key
api_key = "f3f27cbb62574fe3a69121921230112"

def get_weather(city):
    base_url = "https://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': city,
        'aqi': 'no',
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    print(data)  # Print the raw API response for debugging

    # Check if 'error' key is present in the response
    if 'error' in data:
        return None  # Return None or handle the error in your application

    # Check if 'location' and 'current' keys are present in the response
    if 'location' not in data or 'current' not in data:
        return None  # Return None or handle the error in your application

    # Extracting relevant weather information
    location = data['location']
    current_weather = data['current']

    return {
        'name': location.get('name', ''),
        'region': location.get('region', ''),
        'country': location.get('country', ''),
        'localtime': location.get('localtime', ''),
        'temperature': current_weather.get('temp_c', 0),
        'condition': current_weather.get('condition', {}).get('text', ''),
        'wind_speed': current_weather.get('wind_kph', 0),
        'humidity': current_weather.get('humidity', 0),
        'icon_url': f"https:{current_weather.get('condition', {}).get('icon', '')}",
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input from the form
        city = request.form['city']

        # Fetch weather information
        weather_info = get_weather(city)

        # Render the template with weather information
        return render_template('index.html', weather_info=weather_info)

    # Render the initial template
    return render_template('index.html', weather_info=None)

if __name__ == '__main__':
    app.run(debug=True)
