from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

def get_background_url(weather_description):
    """Determine background image URL based on weather description"""
    description = weather_description.lower()
    
    # Rain conditions
    if any(word in description for word in ['rain', 'drizzle', 'shower']):
        return "https://images.unsplash.com/photo-1519692933481-e162a57d6721?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
    
    # Cloudy conditions
    elif any(word in description for word in ['cloud', 'overcast', 'fog', 'mist']):
        return "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
    
    # Clear/Sunny conditions
    elif any(word in description for word in ['clear', 'sunny', 'sky']):
        return "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
    
    # Snow conditions
    elif any(word in description for word in ['snow', 'blizzard']):
        return "https://images.unsplash.com/photo-1547036967-23d11aacaee0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
    
    # Thunderstorm conditions
    elif any(word in description for word in ['thunder', 'storm']):
        return "https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
    
    # Default scenic fallback
    else:
        return "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"

@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    background_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"  # Default background
    
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            params = {
                "q": city,
                "appid": API_KEY,
                "units": "imperial"
            }
            response = requests.get(BASE_URL, params=params)
            print("API Response JSON:", response.json())
            
            if response.status_code == 200:
                weather_data = response.json()
                
                # Get weather description for background
                weather_description = weather_data.get("weather", [{}])[0].get("description", "")
                background_url = get_background_url(weather_description)
                
                # Extract weather info safely
                main_data = weather_data.get("main", {})
                temp = main_data.get("temp", 0)
                feels_like = main_data.get("feels_like", 0)
                humidity = main_data.get("humidity", 0)
                
                # Ensure static/ exists
                if not os.path.exists("static"):
                    os.makedirs("static")
                
                # Create weather chart
                labels = ["Temperature (°F)", "Feels Like (°F)", "Humidity (%)"]
                values = [temp, feels_like, humidity]
                colors = ["dodgerblue", "green", "gold"]
                
                plt.figure(figsize=(6, 4))
                plt.bar(labels, values, color=colors)
                plt.ylabel("Value")
                plt.tight_layout()
                chart_path = os.path.join("static", "chart.png")
                plt.savefig(chart_path)
                plt.close()
            else:
                try:
                    error_msg = response.json().get("message", "Something went wrong")
                except:
                    error_msg = "Something went wrong"
                weather_data = {"error": f"City '{city}' not found! ({error_msg})"}
    
    return render_template("index.html", weather_data=weather_data, background_url=background_url)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
