import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# App Configuration
st.set_page_config(page_title="Weather & Air Quality Analyzer", layout="wide")
st.title("🌍 Weather and Air Pollution Health Risk Analyzer")

# API Key
API_KEY = '7040ea904442a45d6950ba584410ce59'

# Ideal pollutant values (µg/m³)
ideal_values = {
    'pm2_5': 15, 'pm10': 50, 'no2': 40,
    'co': 4400, 'o3': 100, 'so2': 20, 'nh3': 25
}

# Health effects for pollutants
health_effects = {
    'pm2_5': 'Lung/eye irritation, cancer risk, asthma trigger',
    'pm10': 'Coughing, dryness, lung damage',
    'no2': 'Inflammation, respiratory infections, asthma',
    'co': 'Headaches, dizziness, cardiovascular issues',
    'o3': 'Chest pain, throat irritation, coughing',
    'so2': 'Redness, wheezing, respiratory risk',
    'nh3': 'Eye irritation, skin burns, lung damage'
}

# Full names for display
full_names = {
    'pm2_5': 'Particulate Matter ≤ 2.5µm (PM2.5)',
    'pm10': 'Particulate Matter ≤ 10µm (PM10)',
    'no2': 'Nitrogen Dioxide (NO₂)',
    'co': 'Carbon Monoxide (CO)',
    'o3': 'Ozone (O₃)',
    'so2': 'Sulfur Dioxide (SO₂)',
    'nh3': 'Ammonia (NH₃)'
}

# AQI Labels and Descriptions
aqi_levels = {
    1: "Good 😊", 
    2: "Fair 🙂", 
    3: "Moderate 😐",
    4: "Poor 🤷", 
    5: "Very Poor 😱"
}

aqi_health_info = {
    1: ["Good", "0–50", "Air quality is considered satisfactory.", 
        "No health problems. Ideal for everyone including sensitive groups."],
    2: ["Fair", "51–100", "Acceptable air quality.", 
        "Minor irritation possible in very sensitive individuals."],
    3: ["Moderate", "101–150", "May be unhealthy for sensitive groups.", 
        "Irritation, redness, and dryness in eyes/skin; possible respiratory infections."],
    4: ["Poor", "151–200", "Unhealthy for the general public.", 
        "Respiratory and cardiovascular issues likely."],
    5: ["Very Poor", "201–300+", "Very unhealthy air quality.", 
        "Severe health risks — avoid outdoor exposure."]
}

# Location Input
location = st.text_input("Enter a location (e.g., Delhi, India):")

# When user clicks "Get Report"
if st.button("Get Report"):
    if not location.strip():
        st.warning("⚠️ Please enter a valid location.")
    else:
        # Fetch latitude and longitude
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
        geo_res = requests.get(geo_url).json()

        if geo_res:
            lat = geo_res[0]['lat']
            lon = geo_res[0]['lon']
            st.success(f"📍 Location: {location} → Lat: {lat}, Lon: {lon}")

            # Weather Data
            weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
            weather_res = requests.get(weather_url).json()

            if weather_res.get("cod") == 200:
                st.header("🌦️ Current Weather")
                st.write(f"🌡️ Temperature: {weather_res['main']['temp']} °C")
                st.write(f"💧 Humidity: {weather_res['main']['humidity']} %")
                st.write(f"🌬️ Wind Speed: {weather_res['wind']['speed']} m/s")
                st.write(f"☁️ Condition: {weather_res['weather'][0]['description'].capitalize()}")

            # Air Quality Data
            air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
            air_res = requests.get(air_url).json()

            if "list" in air_res:
                st.header("🧪 Air Quality Index (AQI)")
                aqi = air_res['list'][0]['main']['aqi']
                st.write(f"**AQI Level:** {aqi} → {aqi_levels.get(aqi, 'Unknown')}")

                # AQI Category Table
                if aqi in aqi_health_info:
                    cat, rng, desc, health = aqi_health_info[aqi]
                    st.subheader("🦾 AQI Category Health Info")
                    st.markdown(f"""
                    <style>
                    .cat-table td, .cat-table th {{
                        border: 1px solid #999;
                        padding: 10px;
                        text-align: center;
                    }}
                    .cat-table {{
                        border-collapse: collapse;
                        width: 100%;
                    }}
                    </style>
                    <table class="cat-table">
                        <tr>
                            <th>Category</th>
                            <th>AQI Range</th>
                            <th>Description</th>
                            <th>Health Effects</th>
                        </tr>
                        <tr>
                            <td>{cat}</td>
                            <td>{rng}</td>
                            <td>{desc}</td>
                            <td>{health}</td>
                        </tr>
                    </table>
                    """, unsafe_allow_html=True)

                # Pollutant Table
                components = air_res['list'][0]['components']
                rows = []
                for comp in ideal_values:
                    value = components.get(comp, 0)
                    status = health_effects[comp] if value > ideal_values[comp] else "Safe for most individuals"
                    rows.append([
                        full_names[comp],
                        f"{ideal_values[comp]} µg/m³",
                        f"{value} µg/m³",
                        status
                    ])
                df = pd.DataFrame(rows, columns=[
                    "Air Quality Component",
                    "Best (Ideal) Value",
                    "Real-Time Value",
                    "Health Impact"
                ])
                st.header("📊 Health Risk Analysis Table")
                st.dataframe(df.style.set_properties(**{'text-align': 'left'}), use_container_width=True)

                # Visualization
                st.markdown("### 📉 Real-Time Pollutant Concentration Graph")
                chart_df = pd.DataFrame({
                    'Pollutant': [full_names[comp] for comp in ideal_values.keys()],
                    'Concentration (µg/m³)': [components.get(comp, 0) for comp in ideal_values.keys()]
                })
                fig = px.bar(
                    chart_df,
                    x='Pollutant',
                    y='Concentration (µg/m³)',
                    title='Air Pollutant Levels in Real-Time',
                    color='Concentration (µg/m³)',
                    color_continuous_scale='RdYlGn_r',
                    height=400
                )
                fig.update_layout(xaxis_title="Pollutant", yaxis_title="µg/m³")
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("❌ Location not found. Try again.")
