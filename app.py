
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

@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None

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

    return render_template("index.html", weather_data=weather_data)

if __name__ == "__main__":
    app.run(debug=True)
