import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import time
import requests
from PIL import Image
import io
import base64
import random
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="EcoSmart Waste Management",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Keys Configuration
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"  # Replace with your actual OpenWeather API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual Gemini API key

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Custom CSS with enhanced light green and blue theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-green: #4CAF50;
        --light-green: #E8F5E9;
        --accent-blue: #2196F3;
        --light-blue: #E3F2FD;
        --text-dark: #1E2B3C;
        --text-light: #FFFFFF;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, var(--light-green) 0%, var(--light-blue) 100%);
    }
    
    /* Header styles */
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, var(--primary-green), var(--accent-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-in;
    }
    
    /* Section headers */
    .section-header {
        color: var(--text-dark);
        border-bottom: 4px solid var(--accent-blue);
        padding-bottom: 0.5rem;
        margin-bottom: 2rem;
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        border-left: 6px solid var(--primary-green);
        transition: transform 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    /* Alert boxes */
    .alert-box {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border: 1px solid #FFB74D;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        animation: slideIn 0.5s ease;
    }
    
    /* Custom button styles */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-green), var(--accent-blue));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(33, 150, 243, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, white, var(--light-green));
    }
    
    /* Chat messages */
    .stChatMessage {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        animation: popIn 0.3s ease;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes popIn {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-green), var(--accent-blue));
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-dark);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue) !important;
        border-bottom-color: var(--accent-blue) !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Success/Info/Warning/Error boxes */
    .stSuccess {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border: none;
        border-radius: 10px;
        color: #2E7D32;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        border: none;
        border-radius: 10px;
        color: #1565C0;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border: none;
        border-radius: 10px;
        color: #E65100;
    }
    
    .stError {
        background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
        border: none;
        border-radius: 10px;
        color: #C62828;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--text-dark);
        background: white;
        border-radius: 10px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class WasteManagementApp:
    def __init__(self):
        self.bin_data = self.generate_bin_data()
        self.waste_data = self.generate_waste_data()
        self.weather_data = self.get_weather_data()
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
    def generate_bin_data(self):
        """Generate enhanced sample bin data"""
        locations = [
            (40.7128, -74.0060, "Financial District"),
            (40.7589, -73.9851, "Times Square"),
            (40.7505, -73.9934, "Empire State Building"),
            (40.7282, -73.9942, "Washington Square Park"),
            (40.7421, -74.0053, "Chelsea Market"),
            (40.7614, -73.9776, "Rockefeller Center"),
            (40.7359, -74.0026, "Greenwich Village"),
            (40.7465, -73.9818, "Madison Square Park"),
            (40.7549, -73.9840, "Bryant Park")
        ]
        
        data = []
        for i, (lat, lon, location_name) in enumerate(locations):
            fill_level = np.random.randint(0, 100)
            status = "green" if fill_level < 30 else "yellow" if fill_level < 80 else "red"
            last_collected = datetime.now() - timedelta(days=np.random.randint(1, 7))
            
            # Generate realistic fill patterns
            fill_history = [max(0, fill_level + np.random.randint(-10, 10)) for _ in range(7)]
            
            data.append({
                "id": f"BIN_{i+1:03d}",
                "latitude": lat,
                "longitude": lon,
                "location_name": location_name,
                "fill_level": fill_level,
                "status": status,
                "last_collected": last_collected,
                "address": f"{i+100} {location_name} St, New York",
                "capacity": np.random.randint(100, 200),
                "fill_history": fill_history,
                "temperature": np.random.randint(15, 30),
                "humidity": np.random.randint(40, 80),
                "collection_count": np.random.randint(10, 50)
            })
        
        return pd.DataFrame(data)
    
    def generate_waste_data(self):
        """Generate enhanced waste classification data"""
        return pd.DataFrame({
            'material': ['Plastic Bottle', 'Glass Jar', 'Newspaper', 'Cardboard Box',
                        'Banana Peel', 'Aluminum Can', 'Old Phone', 'Used Battery',
                        'Plastic Bag', 'Wine Bottle', 'Egg Carton', 'Yogurt Container'],
            'category': ['Recyclable', 'Recyclable', 'Recyclable', 'Recyclable',
                        'Biodegradable', 'Recyclable', 'E-Waste', 'Hazardous',
                        'Recyclable', 'Recyclable', 'Recyclable', 'Recyclable'],
            'subcategory': ['Plastic', 'Glass', 'Paper', 'Cardboard',
                           'Organic', 'Metal', 'Electronics', 'Chemical',
                           'Plastic', 'Glass', 'Paper', 'Plastic'],
            'recycling_method': ['Rinse and sort by type', 'Rinse and separate by color',
                                'Keep dry and clean', 'Flatten and bundle',
                                'Compost or anaerobic digestion', 'Crush and separate',
                                'Take to e-waste facility', 'Hazardous waste drop-off',
                                'Recycle at soft plastic collection', 'Return for deposit',
                                'Compost or recycle', 'Rinse and recycle'],
            'co2_saved_kg': [2.5, 1.8, 1.2, 2.0, 0.5, 3.0, 15.0, 5.0, 0.8, 1.5, 0.9, 1.2],
            'energy_saved_kwh': [3.0, 2.2, 1.5, 2.5, 0.3, 4.0, 20.0, 0, 1.0, 2.0, 1.2, 1.5]
        })
    
    def get_weather_data(self):
        """Fetch real weather data using OpenWeather API"""
        try:
            # New York coordinates
            lat = 40.7128
            lon = -74.0060
            
            # Make API call to OpenWeather
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get 5-day forecast
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
                forecast_response = requests.get(forecast_url)
                
                forecast_data = []
                if forecast_response.status_code == 200:
                    forecast_json = forecast_response.json()
                    # Get unique days from forecast
                    seen_days = set()
                    for item in forecast_json['list']:
                        day = datetime.fromtimestamp(item['dt']).strftime('%A')[:3]
                        if day not in seen_days and len(forecast_data) < 5:
                            seen_days.add(day)
                            forecast_data.append({
                                "day": day,
                                "temp": round(item['main']['temp']),
                                "condition": item['weather'][0]['main']
                            })
                
                return {
                    "temperature": round(data['main']['temp']),
                    "feels_like": round(data['main']['feels_like']),
                    "humidity": data['main']['humidity'],
                    "pressure": data['main']['pressure'],
                    "wind_speed": round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
                    "wind_direction": self.degrees_to_direction(data['wind']['deg']),
                    "clouds": data['clouds']['all'],
                    "description": data['weather'][0]['description'],
                    "icon": data['weather'][0]['icon'],
                    "forecast": forecast_data if forecast_data else self.generate_mock_forecast()
                }
            else:
                # Fallback to mock data if API fails
                return self.generate_mock_weather_data()
                
        except Exception as e:
            st.warning(f"Using mock weather data due to API error: {str(e)}")
            return self.generate_mock_weather_data()
    
    def degrees_to_direction(self, degrees):
        """Convert wind degrees to cardinal direction"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        ix = round(degrees / (360. / len(directions)))
        return directions[ix % len(directions)]
    
    def generate_mock_weather_data(self):
        """Generate mock weather data as fallback"""
        return {
            "temperature": 22,
            "feels_like": 23,
            "humidity": 65,
            "pressure": 1012,
            "wind_speed": 15,
            "wind_direction": "NW",
            "clouds": 20,
            "description": "scattered clouds",
            "icon": "02d",
            "forecast": self.generate_mock_forecast()
        }
    
    def generate_mock_forecast(self):
        """Generate mock forecast data"""
        conditions = ["Sunny", "Cloudy", "Rain", "Cloudy", "Sunny"]
        temps = [23, 21, 19, 20, 22]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        
        return [
            {"day": days[i], "temp": temps[i], "condition": conditions[i]}
            for i in range(5)
        ]
    
    def get_gemini_response(self, prompt, context=""):
        """Get AI-generated response from Gemini"""
        try:
            # Create a contextual prompt
            full_prompt = f"""You are an EcoSmart Waste Management AI Assistant. 
            Context about current situation: {context}
            
            User query: {prompt}
            
            Provide a helpful, concise response about waste management, recycling, or environmental sustainability.
            Include specific tips and actionable advice when relevant.
            """
            
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return f"I'm having trouble connecting to my AI services. Here's a helpful tip: {self.get_fallback_response(prompt)}"
    
    def get_fallback_response(self, prompt):
        """Fallback responses if Gemini API fails"""
        prompt_lower = prompt.lower()
        
        if "recycle plastic" in prompt_lower:
            return "Check the recycling number (1-7), rinse containers, remove caps, and flatten bottles before recycling."
        elif "bin" in prompt_lower and "full" in prompt_lower:
            return "Monitor fill levels in your dashboard. Schedule collection when bins reach 80% capacity."
        elif "weather" in prompt_lower:
            return "Weather affects collection efficiency. Check the weather analysis section for detailed impacts."
        elif "profit" in prompt_lower:
            return "Explore waste-to-profit opportunities like composting, recycling, or upcycling in the Waste-to-Profit section."
        else:
            return "I can help with waste classification, bin monitoring, recycling tips, and profit opportunities. Please be more specific!"
    
    def sidebar_navigation(self):
        """Enhanced sidebar navigation"""
        with st.sidebar:
            # Logo and title
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image("https://cdn-icons-png.flaticon.com/512/3097/3097976.png", width=60)
            with col2:
                st.markdown("## EcoSmart")
            
            st.markdown("---")
            
            # User profile
            st.markdown("### 👤 User Profile")
            st.markdown("**Waste Manager**")
            st.markdown("New York City")
            st.progress(0.75, text="Daily Target: 75%")
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 📱 Navigation")
            
            sections = {
                "🏠 Dashboard Overview": "dashboard",
                "🗑️ Smart Bin Analysis": "bins",
                "🚚 Route Optimization": "route",
                "♻️ Waste Classification": "waste",
                "🌾 Agricultural Waste": "agriculture",
                "🌤️ Weather Analysis": "weather",
                "💧 Water Pollution": "water",
                "💰 Waste-to-Profit": "profit",
                "🤖 AI Assistant": "ai"
            }
            
            selection = st.radio("", list(sections.keys()), label_visibility="collapsed")
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("### 📊 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Bins", len(self.bin_data))
            with col2:
                full_bins = len(self.bin_data[self.bin_data['status'] == 'red'])
                st.metric("Full Bins", full_bins, delta="-2")
            
            # Notifications
            st.markdown("---")
            st.markdown("### 🔔 Notifications")
            st.info("3 bins need collection")
            st.warning("Weather alert: Rain expected")
            
            return selection
    
    def dashboard_overview(self):
        """Enhanced main dashboard overview"""
        # Header with animated emojis
        st.markdown('<h1 class="main-header">🌍 ♻️ EcoSmart Waste Management 🌱 💧</h1>', 
                   unsafe_allow_html=True)
        
        # Welcome message with timestamp
        current_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
        st.markdown(f"**Welcome back!** Last updated: {current_time}")
        
        # Key Metrics with enhanced styling
        st.markdown("### 📊 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total Bins", len(self.bin_data), "Active")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                full_bins = len(self.bin_data[self.bin_data['status'] == 'red'])
                st.metric("Bins Needing Collection", f"{full_bins}", 
                         delta="-" + str(max(0, full_bins - 3)))
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                avg_fill = self.bin_data['fill_level'].mean()
                st.metric("Avg. Fill Level", f"{avg_fill:.1f}%", 
                         delta=f"{avg_fill - 50:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                efficiency = 87 + np.random.randint(-2, 3)
                st.metric("Collection Efficiency", f"{efficiency}%", 
                         delta="3%" if efficiency > 85 else "-2%")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts and analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Bin Status Distribution")
            status_counts = self.bin_data['status'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=['Empty/Good', 'Half Full', 'Full'],
                values=status_counts.values,
                hole=.4,
                marker_colors=['#4CAF50', '#FFC107', '#F44336']
            )])
            
            fig.update_layout(
                showlegend=True,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1E2B3C')
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Fill Level Trends")
            
            # Create trend data
            trend_data = pd.DataFrame({
                'Time': pd.date_range(start='00:00', periods=24, freq='H'),
                'Average Fill': [30 + 20 * np.sin(i/12 * np.pi) + np.random.randint(-5, 5) 
                                for i in range(24)]
            })
            
            fig = px.line(trend_data, x='Time', y='Average Fill', 
                         title='24-Hour Fill Pattern')
            fig.update_traces(line_color='#4CAF50', line_width=3)
            fig.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1E2B3C')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activities and alerts
        st.markdown("### 📋 Recent Activities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("✅ **Bin BIN_001 collected** - 10 minutes ago")
            st.info("🔄 **Route optimization completed** - 25 minutes ago")
            
        with col2:
            st.warning("⚠️ **Bin BIN_007 at 95%** - Needs attention")
            st.info("🌤️ **Weather update** - Light rain expected")
            
        with col3:
            st.error("🚨 **Overflow detected** - Bin BIN_004")
            st.success("📊 **Daily report generated** - View now")
    
    def smart_bin_analysis(self):
        """Enhanced smart bin monitoring section"""
        st.markdown('<h2 class="section-header">🗑️ Smart Bin Monitoring & Analytics</h2>', 
                   unsafe_allow_html=True)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=["Green", "Yellow", "Red"],
                default=["Green", "Yellow", "Red"]
            )
        
        with col2:
            location_filter = st.selectbox(
                "Filter by Location",
                options=["All Locations"] + list(self.bin_data['location_name'].unique())
            )
        
        with col3:
            fill_threshold = st.slider("Fill Level Threshold", 0, 100, 50)
        
        # Apply filters
        filtered_data = self.bin_data.copy()
        
        if status_filter:
            filtered_data = filtered_data[filtered_data['status'].str.capitalize().isin(status_filter)]
        
        if location_filter != "All Locations":
            filtered_data = filtered_data[filtered_data['location_name'] == location_filter]
        
        filtered_data = filtered_data[filtered_data['fill_level'] >= fill_threshold]
        
        # Map and data
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🗺️ Live Bin Map")
            
            # Create base map
            m = folium.Map(
                location=[40.7128, -74.0060], 
                zoom_start=13,
                tiles='CartoDB positron'
            )
            
            # Add markers for each bin
            for _, bin in filtered_data.iterrows():
                # Determine color and icon
                if bin['status'] == 'green':
                    color = 'green'
                    icon = 'check'
                elif bin['status'] == 'yellow':
                    color = 'orange'
                    icon = 'info-sign'
                else:
                    color = 'red'
                    icon = 'exclamation-sign'
                
                # Create popup with detailed info
                popup_html = f"""
                <div style="font-family: Arial; min-width: 200px;">
                    <h4 style="color: #4CAF50; margin: 0;">{bin['id']}</h4>
                    <p style="margin: 5px 0;"><b>Location:</b> {bin['location_name']}</p>
                    <p style="margin: 5px 0;"><b>Fill Level:</b> {bin['fill_level']}%</p>
                    <p style="margin: 5px 0;"><b>Status:</b> 
                        <span style="color: {'green' if bin['status'] == 'green' else 'orange' if bin['status'] == 'yellow' else 'red'};">
                            {bin['status'].upper()}
                        </span>
                    </p>
                    <p style="margin: 5px 0;"><b>Last Collected:</b> {bin['last_collected'].strftime('%Y-%m-%d')}</p>
                    <p style="margin: 5px 0;"><b>Temperature:</b> {bin['temperature']}°C</p>
                    <p style="margin: 5px 0;"><b>Humidity:</b> {bin['humidity']}%</p>
                </div>
                """
                
                folium.Marker(
                    [bin['latitude'], bin['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{bin['id']} - {bin['fill_level']}%",
                    icon=folium.Icon(color=color, icon=icon)
                ).add_to(m)
            
            # Display map
            folium_static(m, width=800, height=500)
        
        with col2:
            st.markdown("### 📊 Bin Analytics")
            
            # Summary statistics
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Filtered Bins", len(filtered_data))
            st.metric("Average Fill", f"{filtered_data['fill_level'].mean():.1f}%")
            st.metric("Total Capacity", f"{filtered_data['capacity'].sum()} kg")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Status breakdown
            status_counts = filtered_data['status'].value_counts()
            fig = go.Figure(data=[go.Bar(
                x=['Good', 'Half', 'Full'],
                y=[status_counts.get('green', 0), 
                   status_counts.get('yellow', 0), 
                   status_counts.get('red', 0)],
                marker_color=['#4CAF50', '#FFC107', '#F44336']
            )])
            fig.update_layout(
                title="Status Breakdown",
                height=200,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            if st.button("Generate Report", use_container_width=True):
                st.success("Report generated successfully!")
            if st.button("Export Data", use_container_width=True):
                csv = filtered_data.to_csv(index=False)
                st.download_button("Download CSV", csv, "bin_data.csv", "text/csv")
        
        # Detailed data table
        st.markdown("### 📋 Detailed Bin Information")
        st.dataframe(
            filtered_data[['id', 'location_name', 'fill_level', 'status', 
                          'last_collected', 'temperature', 'humidity']],
            use_container_width=True,
            hide_index=True
        )
        
        # Predictive analytics
        st.markdown("### 🔮 Predictive Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            days = st.slider("Prediction Horizon (days)", 1, 7, 3)
            
            if st.button("Generate Prediction", use_container_width=True):
                with st.spinner("Analyzing historical patterns..."):
                    time.sleep(2)
                    
                    # Generate mock prediction
                    future_fill = []
                    for i in range(days):
                        daily_fill = min(100, 50 + 15 * i + np.random.randint(-10, 10))
                        future_fill.append(daily_fill)
                    
                    pred_data = pd.DataFrame({
                        'Day': range(1, days + 1),
                        'Predicted Fill %': future_fill
                    })
                    
                    fig = px.line(pred_data, x='Day', y='Predicted Fill %',
                                 markers=True)
                    fig.update_traces(line_color='#4CAF50', line_width=3)
                    fig.update_layout(
                        title=f"{days}-Day Fill Prediction",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.success(f"Prediction complete: {np.random.randint(3, 8)} bins will reach capacity")
        
        with col2:
            st.markdown("### 📈 Historical Trends")
            
            # Display fill history for selected bin
            selected_bin = st.selectbox("Select Bin for History", filtered_data['id'].tolist())
            
            if selected_bin:
                bin_history = filtered_data[filtered_data['id'] == selected_bin].iloc[0]['fill_history']
                
                hist_data = pd.DataFrame({
                    'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'Fill Level': bin_history
                })
                
                fig = px.bar(hist_data, x='Day', y='Fill Level',
                            title=f"7-Day History - {selected_bin}",
                            color='Fill Level',
                            color_continuous_scale=['green', 'yellow', 'red'])
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def route_optimization(self):
        """Enhanced route optimization section"""
        st.markdown('<h2 class="section-header">🚚 Smart Route Optimization</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🗺️ Optimized Collection Route")
            
            # Get bins that need collection (red and yellow)
            collection_bins = self.bin_data[self.bin_data['status'].isin(['red', 'yellow'])].copy()
            
            if len(collection_bins) > 0:
                # Create map
                m = folium.Map(location=[40.7128, -74.0060], zoom_start=13,
                              tiles='CartoDB positron')
                
                # Generate optimal route (simplified TSP)
                route_points = []
                current_pos = [40.7128, -74.0060]  # Start from depot
                
                # Sort by priority (red first) and distance
                priority_bins = collection_bins.sort_values(
                    by=['status', 'fill_level'], 
                    ascending=[True, False]
                )
                
                for idx, (_, bin) in enumerate(priority_bins.iterrows()):
                    point = [bin['latitude'], bin['longitude']]
                    route_points.append(point)
                    
                    # Marker color based on status
                    color = 'red' if bin['status'] == 'red' else 'orange'
                    
                    # Create popup
                    popup_html = f"""
                    <div style="font-family: Arial;">
                        <h4>Stop {idx + 1}: {bin['id']}</h4>
                        <p><b>Status:</b> {bin['status'].upper()}</p>
                        <p><b>Fill Level:</b> {bin['fill_level']}%</p>
                        <p><b>Location:</b> {bin['location_name']}</p>
                    </div>
                    """
                    
                    folium.Marker(
                        point,
                        popup=folium.Popup(popup_html, max_width=200),
                        tooltip=f"Stop {idx + 1}: {bin['fill_level']}%",
                        icon=folium.Icon(color=color, icon='truck' if idx == 0 else 'info-sign')
                    ).add_to(m)
                
                # Add route line
                if len(route_points) > 1:
                    folium.PolyLine(
                        route_points,
                        color='#2196F3',
                        weight=5,
                        opacity=0.8,
                        dash_array='5'
                    ).add_to(m)
                    
                    # Add distance markers
                    for i in range(len(route_points) - 1):
                        mid_point = [
                            (route_points[i][0] + route_points[i+1][0])/2,
                            (route_points[i][1] + route_points[i+1][1])/2
                        ]
                        distance = np.random.randint(1, 5)  # Mock distance
                        folium.Marker(
                            mid_point,
                            icon=folium.DivIcon(
                                html=f'<div style="background: white; padding: 2px 5px; border-radius: 10px; border: 2px solid #2196F3;">{distance}km</div>'
                            )
                        ).add_to(m)
                
                # Add depot marker
                folium.Marker(
                    [40.7128, -74.0060],
                    popup="Depot",
                    tooltip="Start/End Point",
                    icon=folium.Icon(color='green', icon='home')
                ).add_to(m)
                
                folium_static(m, width=800, height=500)
            else:
                st.info("No bins currently need collection. All bins are at optimal levels!")
        
        with col2:
            st.markdown("### 📊 Route Summary")
            
            # Route statistics
            num_stops = len(collection_bins)
            total_distance = num_stops * 3.2  # Mock calculation
            estimated_time = total_distance * 2.5  # Mock calculation
            
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Stops", num_stops)
            st.metric("Total Distance", f"{total_distance:.1f} km")
            st.metric("Estimated Time", f"{estimated_time:.1f} min")
            st.metric("Fuel Required", f"{(total_distance/5):.1f} L")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Savings
            st.markdown("### 💰 Estimated Savings")
            
            savings_data = {
                "Fuel Savings": f"${num_stops * 3:.2f}",
                "Time Savings": f"{num_stops * 5} min",
                "CO2 Reduction": f"{num_stops * 2.5} kg"
            }
            
            for label, value in savings_data.items():
                st.success(f"**{label}:** {value}")
            
            # Route optimization options
            st.markdown("### ⚙️ Optimization Options")
            
            optimization_goal = st.radio(
                "Optimize for:",
                ["Shortest Time", "Minimum Fuel", "Priority Bins First"]
            )
            
            if st.button("Re-optimize Route", use_container_width=True):
                with st.spinner("Calculating optimal route..."):
                    time.sleep(2)
                    st.success(f"Route optimized for {optimization_goal}!")
    
    def waste_classification(self):
        """Enhanced waste classification section"""
        st.markdown('<h2 class="section-header">♻️ AI Waste Classification & Recycling</h2>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📸 AI Classifier", 
            "📚 Recycling Guide", 
            "📊 Impact Calculator",
            "🎓 Learn & Earn"
        ])
        
        with tab1:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📤 Upload Waste Image")
                
                # Camera input option
                use_camera = st.checkbox("Use Camera")
                
                if use_camera:
                    img_file = st.camera_input("Take a photo of the waste")
                else:
                    img_file = st.file_uploader(
                        "Choose an image", 
                        type=['jpg', 'jpeg', 'png'],
                        help="Upload a clear image of the waste item"
                    )
                
                if img_file is not None:
                    # Display uploaded image
                    st.image(img_file, caption="Uploaded Image", use_column_width=True)
                    
                    if st.button("🔍 Classify Waste", use_container_width=True):
                        with st.spinner("Analyzing image with AI..."):
                            time.sleep(2)
                            
                            # Mock classification results
                            materials = [
                                "Plastic Bottle", "Glass Jar", "Aluminum Can", 
                                "Newspaper", "Cardboard Box", "Food Container"
                            ]
                            
                            selected_material = random.choice(materials)
                            material_info = self.waste_data[
                                self.waste_data['material'] == selected_material
                            ].iloc[0] if selected_material in self.waste_data['material'].values else None
                            
                            if material_info is None:
                                material_info = self.waste_data.iloc[0]
                            
                            # Display results with animations
                            st.balloons()
                            st.success("✅ Classification Complete!")
                            
                            # Results in columns
                            res_col1, res_col2, res_col3 = st.columns(3)
                            
                            with res_col1:
                                st.markdown("**Material Type**")
                                st.markdown(f"## {material_info['material']}")
                            
                            with res_col2:
                                st.markdown("**Category**")
                                color = {
                                    'Recyclable': '🟢',
                                    'Biodegradable': '🟡',
                                    'Hazardous': '🔴',
                                    'E-Waste': '🔵'
                                }.get(material_info['category'], '⚪')
                                st.markdown(f"## {color} {material_info['category']}")
                            
                            with res_col3:
                                st.markdown("**Confidence**")
                                st.markdown(f"## {random.randint(85, 99)}%")
                            
                            # Disposal instructions
                            st.markdown("### 📝 Disposal Instructions")
                            
                            if material_info['category'] == 'Recyclable':
                                st.info(f"♻️ **Recycling Method:** {material_info['recycling_method']}")
                                
                                # Additional tips
                                tips = [
                                    "✓ Rinse container to remove residue",
                                    "✓ Remove labels if possible",
                                    "✓ Crush to save space",
                                    "✓ Check local recycling guidelines"
                                ]
                                for tip in tips:
                                    st.markdown(tip)
                            
                            elif material_info['category'] == 'Biodegradable':
                                st.info(f"🌱 **Composting Method:** {material_info['recycling_method']}")
                                
                                # Composting tips
                                tips = [
                                    "✓ Add to compost bin",
                                    "✓ Mix with brown materials",
                                    "✓ Keep moist but not wet",
                                    "✓ Turn regularly"
                                ]
                                for tip in tips:
                                    st.markdown(tip)
                            
                            else:
                                st.warning(f"⚠️ **Special Handling:** {material_info['recycling_method']}")
                            
                            # Environmental impact
                            st.markdown("### 🌍 Environmental Impact")
                            
                            imp_col1, imp_col2 = st.columns(2)
                            with imp_col1:
                                st.metric("CO₂ Saved", f"{material_info['co2_saved_kg']} kg")
                            with imp_col2:
                                st.metric("Energy Saved", f"{material_info['energy_saved_kwh']} kWh")
            
            with col2:
                st.markdown("### 📊 Classification History")
                
                # Mock classification history
                history_data = pd.DataFrame({
                    'Time': pd.date_range(end=datetime.now(), periods=5, freq='H'),
                    'Item': ['Plastic Bottle', 'Glass Jar', 'Newspaper', 'Aluminum Can', 'Food Waste'],
                    'Category': ['Recyclable', 'Recyclable', 'Recyclable', 'Recyclable', 'Biodegradable'],
                    'Confidence': [94, 97, 91, 96, 88]
                })
                
                st.dataframe(history_data, use_container_width=True, hide_index=True)
                
                # Statistics
                st.markdown("### 📈 Statistics")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Total Items", "127", "12")
                with col_b:
                    st.metric("Accuracy Rate", "94%", "2%")
                
                # Tips of the day
                st.markdown("### 💡 Tip of the Day")
                tips = [
                    "Rinse containers before recycling to prevent contamination",
                    "Flatten cardboard boxes to save space",
                    "Remove plastic caps before recycling glass bottles",
                    "Keep electronics separate from regular waste"
                ]
                st.info(random.choice(tips))
        
        with tab2:
            st.markdown("### 📚 Comprehensive Recycling Guide")
            
            # Search
            search_term = st.text_input("🔍 Search materials", placeholder="e.g., plastic, glass, batteries")
            
            # Filter data
            filtered_guide = self.waste_data
            if search_term:
                filtered_guide = self.waste_data[
                    self.waste_data['material'].str.contains(search_term, case=False) |
                    self.waste_data['category'].str.contains(search_term, case=False) |
                    self.waste_data['subcategory'].str.contains(search_term, case=False)
                ]
            
            # Display as cards
            for _, item in filtered_guide.iterrows():
                with st.expander(f"**{item['material']}** - {item['category']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Category:** {item['category']}")
                        st.markdown(f"**Subcategory:** {item['subcategory']}")
                        st.markdown(f"**Recycling Method:** {item['recycling_method']}")
                        
                        # Status indicator
                        if item['category'] == 'Recyclable':
                            st.success("✅ Easily Recyclable")
                        elif item['category'] == 'Biodegradable':
                            st.info("🌱 Compostable")
                        elif item['category'] == 'Hazardous':
                            st.error("⚠️ Handle with Care")
                        else:
                            st.warning("🔄 Special Handling Required")
                    
                    with col2:
                        st.markdown("**Environmental Impact**")
                        st.metric("CO₂ Saved", f"{item['co2_saved_kg']} kg")
                        st.metric("Energy Saved", f"{item['energy_saved_kwh']} kWh")
        
        with tab3:
            st.markdown("### 📊 Recycling Impact Calculator")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Select Items to Recycle**")
                
                # Item selection
                selected_items = []
                total_co2 = 0
                total_energy = 0
                
                for _, item in self.waste_data.iterrows():
                    if st.checkbox(f"{item['material']}"):
                        selected_items.append(item['material'])
                        total_co2 += item['co2_saved_kg']
                        total_energy += item['energy_saved_kwh']
            
            with col2:
                st.markdown("**Impact Summary**")
                
                if selected_items:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Items Selected", len(selected_items))
                    st.metric("Total CO₂ Saved", f"{total_co2:.1f} kg")
                    st.metric("Total Energy Saved", f"{total_energy:.1f} kWh")
                    st.metric("Equivalent Trees", f"{int(total_co2/20)}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Visualization
                    fig = go.Figure(data=[
                        go.Bar(name='CO₂ Saved (kg)', x=['Impact'], y=[total_co2],
                              marker_color='#4CAF50'),
                        go.Bar(name='Energy Saved (kWh)', x=['Impact'], y=[total_energy],
                              marker_color='#2196F3')
                    ])
                    fig.update_layout(
                        barmode='group',
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Select items to see your recycling impact!")
        
        with tab4:
            st.markdown("### 🎓 Learn & Earn Program")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Available Courses**")
                
                courses = [
                    {"name": "Recycling Basics", "points": 50, "duration": "30 min"},
                    {"name": "Composting 101", "points": 75, "duration": "45 min"},
                    {"name": "E-Waste Management", "points": 100, "duration": "60 min"},
                    {"name": "Plastic Reduction", "points": 60, "duration": "40 min"}
                ]
                
                for course in courses:
                    if st.button(f"📚 {course['name']}", key=course['name']):
                        st.success(f"Enrolled! Complete to earn {course['points']} points")
            
            with col2:
                st.markdown("**Your Progress**")
                
                # Mock user progress
                st.progress(0.45, text="Overall Progress: 45%")
                st.metric("Points Earned", "235")
                st.metric("Next Reward", "500 points - $10 voucher")
                
                # Leaderboard
                st.markdown("**Community Leaderboard**")
                leaderboard = pd.DataFrame({
                    'Rank': ['1st', '2nd', '3rd', '4th', '5th'],
                    'User': ['GreenHero', 'EcoWarrior', 'RecyclePro', 'EarthFirst', 'WasteLess'],
                    'Points': [1250, 980, 845, 720, 650]
                })
                st.dataframe(leaderboard, use_container_width=True, hide_index=True)
    
    def agricultural_waste(self):
        """Enhanced agricultural waste management section"""
        st.markdown('<h2 class="section-header">🌾 Agricultural Waste Management</h2>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌱 Solutions", 
            "📚 Tutorials", 
            "💰 Profit Calculator",
            "🏆 Success Stories"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🧑‍🌾 Waste Type Solutions")
                
                waste_types = {
                    "Crop Residue": {
                        "icon": "🌽",
                        "solutions": [
                            "Composting for organic fertilizer",
                            "Biochar production",
                            "Animal bedding material",
                            "Mushroom cultivation substrate",
                            "Biogas generation"
                        ]
                    },
                    "Animal Waste": {
                        "icon": "🐄",
                        "solutions": [
                            "Biogas generation",
                            "Vermicomposting",
                            "Direct fertilizer application",
                            "Anaerobic digestion",
                            "Fish feed production"
                        ]
                    },
                    "Organic By-products": {
                        "icon": "🥬",
                        "solutions": [
                            "Animal feed production",
                            "Biofuel conversion",
                            "Industrial raw materials",
                            "Soil amendment products",
                            "Packaging materials"
                        ]
                    }
                }
                
                for waste_type, info in waste_types.items():
                    with st.expander(f"{info['icon']} {waste_type}"):
                        for solution in info['solutions']:
                            st.markdown(f"• {solution}")
            
            with col2:
                st.markdown("### 📊 Regional Impact")
                
                # Mock data
                regions = ["North", "South", "East", "West"]
                waste_volume = [450, 380, 520, 410]
                
                fig = px.bar(
                    x=regions,
                    y=waste_volume,
                    title="Agricultural Waste by Region (tons/month)",
                    color=waste_volume,
                    color_continuous_scale='Greens'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Quick stats
                st.markdown("### 📈 Key Metrics")
                st.metric("Total Waste", "1,760 tons/month", "-5%")
                st.metric("Recycled", "1,230 tons/month", "+12%")
                st.metric("Composted", "890 tons/month", "+8%")
        
        with tab2:
            st.markdown("### 📚 Step-by-Step Tutorials")
            
            tutorial = st.selectbox(
                "Select Tutorial",
                ["Composting Guide", "Biogas Setup", "Vermicomposting", "Biochar Production"]
            )
            
            if tutorial == "Composting Guide":
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Materials Needed:**")
                    st.markdown("• Crop residues (carbon-rich)")
                    st.markdown("• Green waste (nitrogen-rich)")
                    st.markdown("• Water")
                    st.markdown("• Compost bin or pile area")
                    st.markdown("• Garden fork or turner")
                
                with col2:
                    st.markdown("**Steps:**")
                    steps = [
                        "1. Choose a level, well-drained location",
                        "2. Layer brown and green materials (3:1 ratio)",
                        "3. Add water to maintain moisture",
                        "4. Turn pile every 2-3 weeks",
                        "5. Monitor temperature (130-150°F ideal)",
                        "6. Harvest in 3-6 months"
                    ]
                    for step in steps:
                        st.markdown(step)
                
                # Video placeholder
                st.video("https://www.youtube.com/watch?v=example_composting")
            
            elif tutorial == "Biogas Setup":
                st.markdown("**Biogas System Components:**")
                
                components = [
                    "• Digester tank (500-1000L capacity)",
                    "• Inlet pipe for waste feeding",
                    "• Gas outlet pipe",
                    "• Gas storage balloon",
                    "• Slurry outlet",
                    "• Safety valve"
                ]
                
                for component in components:
                    st.markdown(component)
                
                st.markdown("**Installation Steps:**")
                steps = [
                    "1. Dig pit and level base",
                    "2. Install digester tank",
                    "3. Connect inlet and outlet pipes",
                    "4. Install gas collection system",
                    "5. Test for leaks",
                    "6. Start with water and small amount of waste"
                ]
                
                for step in steps:
                    st.markdown(step)
        
        with tab3:
            st.markdown("### 💰 Profit Potential Calculator")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Input Your Farm Data**")
                
                farm_size = st.number_input("Farm Size (acres)", min_value=1, value=10)
                crop_type = st.selectbox("Primary Crop", ["Corn", "Wheat", "Rice", "Vegetables", "Mixed"])
                livestock = st.number_input("Livestock Count", min_value=0, value=50)
                
                if st.button("Calculate Profit Potential", use_container_width=True):
                    with st.spinner("Calculating..."):
                        time.sleep(1.5)
                        
                        # Mock calculations
                        waste_volume = farm_size * 50 + livestock * 10
                        compost_value = waste_volume * 0.6 * 50
                        biogas_value = livestock * 365 * 0.5
                        total_profit = compost_value + biogas_value
                        
                        st.session_state['profit_result'] = {
                            'waste_volume': waste_volume,
                            'compost_value': compost_value,
                            'biogas_value': biogas_value,
                            'total_profit': total_profit
                        }
            
            with col2:
                if 'profit_result' in st.session_state:
                    result = st.session_state['profit_result']
                    
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Annual Waste Volume", f"{result['waste_volume']:.0f} tons")
                    st.metric("Compost Value", f"${result['compost_value']:,.0f}")
                    st.metric("Biogas Value", f"${result['biogas_value']:,.0f}")
                    st.metric("Total Annual Profit", f"${result['total_profit']:,.0f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # ROI visualization
                    fig = go.Figure(data=[
                        go.Pie(
                            labels=['Compost', 'Biogas', 'Other'],
                            values=[result['compost_value'], result['biogas_value'], 
                                   result['total_profit'] * 0.1],
                            hole=.4,
                            marker_colors=['#4CAF50', '#2196F3', '#FFC107']
                        )
                    ])
                    fig.update_layout(
                        title="Revenue Breakdown",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.markdown("### 🏆 Success Stories")
            
            stories = [
                {
                    "farmer": "Green Valley Farms",
                    "location": "California",
                    "achievement": "Converted 500 tons of crop residue to organic fertilizer",
                    "profit": "$75,000 annual profit",
                    "impact": "Reduced chemical fertilizer use by 60%"
                },
                {
                    "farmer": "Sunrise Dairy",
                    "location": "Wisconsin",
                    "achievement": "Biogas system powering entire farm operation",
                    "profit": "$45,000 annual savings",
                    "impact": "Eliminated 200 tons of CO2 emissions"
                },
                {
                    "farmer": "Organic Harvest Co-op",
                    "location": "Oregon",
                    "achievement": "Vermicomposting operation serving 500+ gardens",
                    "profit": "$120,000 annual revenue",
                    "impact": "Created 12 local jobs"
                }
            ]
            
            for story in stories:
                with st.expander(f"**{story['farmer']}** - {story['location']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Achievement:** {story['achievement']}")
                        st.markdown(f"**Profit:** {story['profit']}")
                    
                    with col2:
                        st.markdown(f"**Impact:** {story['impact']}")
                        st.markdown(f"**Location:** {story['location']}")
                    
                    if st.button(f"Learn More about {story['farmer']}", key=story['farmer']):
                        st.info("Full case study available upon request!")
    
    def weather_analysis(self):
        """Enhanced weather analysis section"""
        st.markdown('<h2 class="section-header">🌤️ Weather Impact Analysis</h2>', 
                   unsafe_allow_html=True)
        
        # Current weather
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"### 🌡️ {self.weather_data['temperature']}°C")
            st.markdown(f"Feels like: {self.weather_data['feels_like']}°C")
            st.markdown(f"**{self.weather_data['description'].title()}**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"### 💧 Humidity")
            st.markdown(f"{self.weather_data['humidity']}%")
            st.markdown(f"Pressure: {self.weather_data['pressure']} hPa")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"### 💨 Wind")
            st.markdown(f"{self.weather_data['wind_speed']} km/h")
            st.markdown(f"Direction: {self.weather_data['wind_direction']}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Forecast
        st.markdown("### 📅 5-Day Forecast")
        
        forecast_cols = st.columns(5)
        for i, (col, forecast) in enumerate(zip(forecast_cols, self.weather_data['forecast'])):
            with col:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f"**{forecast['day']}**")
                st.markdown(f"## {forecast['temp']}°C")
                st.markdown(f"_{forecast['condition']}_")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Impact on waste management
        st.markdown("### 🗑️ Impact on Waste Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Weather Alerts**")
            
            if self.weather_data['description'] == 'rain':
                st.error("🚨 Heavy rain expected - Secure all bins!")
            elif self.weather_data['wind_speed'] > 20:
                st.warning("💨 Strong winds - Check bin lids")
            elif self.weather_data['temperature'] > 30:
                st.warning("🔥 Heat wave - Increase collection frequency")
            else:
                st.success("✅ Optimal conditions for waste management")
        
        with col2:
            st.markdown("**Recommendations**")
            
            recommendations = []
            if self.weather_data['description'] in ['rain', 'rainy']:
                recommendations = [
                    "Cover waste bins to prevent overflow",
                    "Postpone outdoor composting activities",
                    "Check drainage around waste sites",
                    "Use waterproof covers for recycling"
                ]
            elif self.weather_data['wind_speed'] > 20:
                recommendations = [
                    "Secure lightweight materials",
                    "Check bin lids are properly closed",
                    "Avoid open burning of waste",
                    "Postpone paper/cardboard collection"
                ]
            elif self.weather_data['temperature'] > 30:
                recommendations = [
                    "Increase organic waste collection frequency",
                    "Provide shade for composting areas",
                    "Hydrate collection staff frequently",
                    "Monitor for pest activity"
                ]
            else:
                recommendations = [
                    "Normal operations can continue",
                    "Good time for outdoor composting",
                    "Optimal for waste collection",
                    "Perfect for recycling activities"
                ]
            
            for rec in recommendations:
                st.markdown(f"• {rec}")
    
    def water_pollution(self):
        """Enhanced water pollution management section"""
        st.markdown('<h2 class="section-header">💧 Water Pollution Management</h2>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📊 Monitoring", "🛡️ Prevention", "🌊 Clean-up"])
        
        with tab1:
            st.markdown("### 📍 Water Quality Monitoring Stations")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Map of monitoring stations
                m = folium.Map(location=[40.7128, -74.0060], zoom_start=11,
                              tiles='CartoDB positron')
                
                stations = [
                    (40.7831, -73.9712, "Hudson River Station", 68, "Moderate"),
                    (40.7505, -73.9934, "East River Station", 45, "Poor"),
                    (40.7282, -74.0026, "Harlem River Station", 78, "Good"),
                    (40.7740, -73.9800, "Central Park Lake", 85, "Excellent"),
                    (40.7050, -74.0130, "Battery Park", 72, "Moderate")
                ]
                
                for lat, lon, name, index, quality in stations:
                    color = {
                        "Excellent": "green",
                        "Good": "blue",
                        "Moderate": "orange",
                        "Poor": "red"
                    }.get(quality, "gray")
                    
                    popup_html = f"""
                    <div style="font-family: Arial;">
                        <h4>{name}</h4>
                        <p><b>Quality Index:</b> {index}</p>
                        <p><b>Status:</b> {quality}</p>
                    </div>
                    """
                    
                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(popup_html, max_width=200),
                        tooltip=name,
                        icon=folium.Icon(color=color, icon='tint')
                    ).add_to(m)
                
                folium_static(m, width=600, height=400)
            
            with col2:
                st.markdown("**Water Quality Summary**")
                
                # Quality metrics
                metrics = {
                    "Total Stations": "5",
                    "Excellent": "1",
                    "Good": "1",
                    "Moderate": "2",
                    "Poor": "1"
                }
                
                for key, value in metrics.items():
                    st.metric(key, value)
                
                # Real-time alerts
                st.markdown("**⚠️ Alerts**")
                st.warning("East River - Pollution spike detected")
                st.info("Harlem River - Improving trend")
            
            # Pollution trends
            st.markdown("### 📈 Pollution Trends")
            
            # Generate mock trend data
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            pollution_data = pd.DataFrame({
                'Date': dates,
                'Hudson River': [65 + 10*np.sin(i/5) + np.random.randint(-5, 5) for i in range(30)],
                'East River': [45 + 15*np.sin(i/4) + np.random.randint(-8, 8) for i in range(30)],
                'Harlem River': [78 + 5*np.sin(i/6) + np.random.randint(-3, 3) for i in range(30)]
            })
            
            fig = px.line(pollution_data, x='Date', y=['Hudson River', 'East River', 'Harlem River'],
                         title="30-Day Water Quality Trends")
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend_title="Location"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("### 🛡️ Pollution Prevention Strategies")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Industrial Prevention**")
                strategies = [
                    "✅ Closed-loop water systems",
                    "✅ Effluent treatment monitoring",
                    "✅ Biodegradable chemical use",
                    "✅ Employee training programs",
                    "✅ Spill prevention plans",
                    "✅ Regular equipment maintenance"
                ]
                
                for strategy in strategies:
                    st.markdown(strategy)
            
            with col2:
                st.markdown("**Community Prevention**")
                strategies = [
                    "✅ Proper household chemical disposal",
                    "✅ Reduce plastic usage",
                    "✅ Rain garden installation",
                    "✅ Green infrastructure",
                    "✅ Public awareness campaigns",
                    "✅ Volunteer monitoring programs"
                ]
                
                for strategy in strategies:
                    st.markdown(strategy)
            
            # Prevention impact
            st.markdown("### 📊 Prevention Impact Calculator")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                households = st.number_input("Participating Households", min_value=0, value=1000, step=100)
            with col2:
                businesses = st.number_input("Participating Businesses", min_value=0, value=50, step=10)
            with col3:
                st.markdown("**Calculate Impact**")
                if st.button("Calculate"):
                    with st.spinner("Calculating..."):
                        time.sleep(1)
                        
                        plastic_reduced = households * 5 + businesses * 50
                        chemical_reduced = households * 0.5 + businesses * 10
                        water_saved = households * 100 + businesses * 1000
                        
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("Plastic Reduced", f"{plastic_reduced} kg/month")
                        col_b.metric("Chemical Reduced", f"{chemical_reduced} L/month")
                        col_c.metric("Water Saved", f"{water_saved} L/month")
        
        with tab3:
            st.markdown("### 🌊 Clean-up Initiatives")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Upcoming Clean-up Events**")
                
                events = [
                    {"date": "2024-01-20", "location": "Hudson River Park", "volunteers": 45, "status": "Open"},
                    {"date": "2024-01-22", "location": "East River Esplanade", "volunteers": 30, "status": "Open"},
                    {"date": "2024-01-25", "location": "Gowanus Canal", "volunteers": 60, "status": "Full"},
                    {"date": "2024-01-27", "location": "Bronx River", "volunteers": 25, "status": "Open"}
                ]
                
                for event in events:
                    with st.expander(f"{event['date']} - {event['location']}"):
                        st.markdown(f"**Volunteers Needed:** {event['volunteers']}")
                        st.markdown(f"**Status:** {event['status']}")
                        
                        if event['status'] == 'Open':
                            if st.button(f"Join this clean-up", key=event['location']):
                                st.success("You've been registered! Check your email for details.")
            
            with col2:
                st.markdown("**Clean-up Impact Tracker**")
                
                # Mock impact data
                total_volunteers = 1247
                total_waste = 3.8
                total_distance = 45
                
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Total Volunteers", f"{total_volunteers:,}")
                st.metric("Waste Collected", f"{total_waste} tons")
                st.metric("Shoreline Cleaned", f"{total_distance} km")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Progress chart
                monthly_data = pd.DataFrame({
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'Volunteers': [120, 145, 168, 190, 215, 240],
                    'Waste (tons)': [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
                })
                
                fig = px.bar(monthly_data, x='Month', y='Volunteers',
                            title="Monthly Volunteer Participation",
                            color='Volunteers',
                            color_continuous_scale='Blues')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def waste_to_profit(self):
        """Enhanced waste-to-profit section"""
        st.markdown('<h2 class="section-header">💰 Waste-to-Profit Opportunities</h2>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "💡 Business Ideas", 
            "📊 ROI Calculator", 
            "🏢 Case Studies",
            "📚 Resources"
        ])
        
        with tab1:
            st.markdown("### 💡 Profitable Waste-Based Business Ideas")
            
            # Business categories
            categories = ["All", "Recycling", "Upcycling", "Composting", "Energy", "Construction"]
            selected_category = st.segmented_control("Filter by Category", categories, default="All")
            
            businesses = [
                {
                    "name": "Plastic Upcycling Workshop",
                    "category": "Upcycling",
                    "materials": "Plastic waste",
                    "products": "Furniture, decor items",
                    "investment": "$5,000-10,000",
                    "profit": "$2,000-5,000/month",
                    "difficulty": "Medium",
                    "icon": "🪑"
                },
                {
                    "name": "Organic Fertilizer Production",
                    "category": "Composting",
                    "materials": "Agricultural waste, food scraps",
                    "products": "Compost, liquid fertilizer",
                    "investment": "$3,000-8,000",
                    "profit": "$1,500-4,000/month",
                    "difficulty": "Easy",
                    "icon": "🌱"
                },
                {
                    "name": "Eco-Brick Manufacturing",
                    "category": "Construction",
                    "materials": "Plastic bottles, dry waste",
                    "products": "Construction bricks",
                    "investment": "$10,000-20,000",
                    "profit": "$4,000-8,000/month",
                    "difficulty": "Medium",
                    "icon": "🧱"
                },
                {
                    "name": "Biogas Production",
                    "category": "Energy",
                    "materials": "Organic waste, manure",
                    "products": "Biogas, fertilizer",
                    "investment": "$15,000-30,000",
                    "profit": "$3,000-6,000/month",
                    "difficulty": "Hard",
                    "icon": "⚡"
                },
                {
                    "name": "E-Waste Recycling",
                    "category": "Recycling",
                    "materials": "Electronics, batteries",
                    "products": "Precious metals, components",
                    "investment": "$20,000-50,000",
                    "profit": "$8,000-15,000/month",
                    "difficulty": "Hard",
                    "icon": "💻"
                },
                {
                    "name": "Glass Crushing Business",
                    "category": "Recycling",
                    "materials": "Glass bottles, jars",
                    "products": "Crushed glass, sand",
                    "investment": "$8,000-15,000",
                    "profit": "$2,500-5,000/month",
                    "difficulty": "Easy",
                    "icon": "🥃"
                }
            ]
            
            # Filter businesses
            filtered_businesses = businesses
            if selected_category != "All":
                filtered_businesses = [b for b in businesses if b['category'] == selected_category]
            
            # Display as cards
            for business in filtered_businesses:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown(f"<h1 style='text-align: center; font-size: 4rem;'>{business['icon']}</h1>", 
                                  unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"### {business['name']}")
                        st.markdown(f"**Category:** {business['category']}")
                        st.markdown(f"**Materials:** {business['materials']}")
                        st.markdown(f"**Products:** {business['products']}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.markdown(f"**Investment**\n\n{business['investment']}")
                        with col_b:
                            st.markdown(f"**Profit**\n\n{business['profit']}")
                        with col_c:
                            st.markdown(f"**Difficulty**\n\n{business['difficulty']}")
                    
                    st.markdown("---")
        
        with tab2:
            st.markdown("### 📊 ROI Calculator")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Business Parameters**")
                
                business_type = st.selectbox(
                    "Business Type",
                    ["Recycling", "Composting", "Biogas", "Upcycling", "E-Waste"]
                )
                
                initial_investment = st.number_input("Initial Investment ($)", 
                                                     min_value=1000, value=10000, step=1000)
                monthly_operating_cost = st.number_input("Monthly Operating Cost ($)", 
                                                        min_value=100, value=2000, step=100)
                waste_processed = st.number_input("Waste Processed (tons/month)", 
                                                  min_value=0.1, value=5.0, step=0.5)
                revenue_per_ton = st.number_input("Revenue per Ton ($)", 
                                                  min_value=10, value=200, step=10)
                
                if st.button("Calculate ROI", use_container_width=True):
                    with st.spinner("Calculating returns..."):
                        time.sleep(1.5)
                        
                        monthly_revenue = waste_processed * revenue_per_ton
                        monthly_profit = monthly_revenue - monthly_operating_cost
                        annual_profit = monthly_profit * 12
                        roi = (annual_profit / initial_investment) * 100
                        payback_period = initial_investment / monthly_profit if monthly_profit > 0 else float('inf')
                        
                        # Store in session state
                        st.session_state['roi_results'] = {
                            'monthly_revenue': monthly_revenue,
                            'monthly_profit': monthly_profit,
                            'annual_profit': annual_profit,
                            'roi': roi,
                            'payback_period': payback_period
                        }
            
            with col2:
                if 'roi_results' in st.session_state:
                    results = st.session_state['roi_results']
                    
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Monthly Revenue", f"${results['monthly_revenue']:,.2f}")
                    st.metric("Monthly Profit", f"${results['monthly_profit']:,.2f}")
                    st.metric("Annual Profit", f"${results['annual_profit']:,.2f}")
                    st.metric("ROI", f"{results['roi']:.1f}%")
                    st.metric("Payback Period", f"{results['payback_period']:.1f} months")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Profit visualization
                    fig = go.Figure(data=[
                        go.Bar(name='Revenue', x=['Monthly'], y=[results['monthly_revenue']],
                              marker_color='#4CAF50'),
                        go.Bar(name='Cost', x=['Monthly'], y=[monthly_operating_cost],
                              marker_color='#F44336'),
                        go.Bar(name='Profit', x=['Monthly'], y=[results['monthly_profit']],
                              marker_color='#2196F3')
                    ])
                    fig.update_layout(
                        title="Monthly Financial Breakdown",
                        barmode='group',
                        height=300,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.markdown("### 🏢 Success Case Studies")
            
            case_studies = [
                {
                    "company": "GreenCycle Solutions",
                    "location": "Portland, OR",
                    "business": "Plastic Recycling",
                    "investment": "$50,000",
                    "annual_revenue": "$180,000",
                    "year": "2022",
                    "highlights": [
                        "Processed 500 tons of plastic in first year",
                        "Created 8 local jobs",
                        "Diverted 30% of city's plastic waste"
                    ]
                },
                {
                    "company": "EcoFertilizer Co.",
                    "location": "Fresno, CA",
                    "business": "Agricultural Waste Composting",
                    "investment": "$35,000",
                    "annual_revenue": "$120,000",
                    "year": "2023",
                    "highlights": [
                        "Partnership with 50 local farms",
                        "Produces 1000 tons of compost annually",
                        "Reduced chemical fertilizer use by 40%"
                    ]
                },
                {
                    "company": "BioGas Innovations",
                    "location": "Madison, WI",
                    "business": "Biogas Generation",
                    "investment": "$150,000",
                    "annual_revenue": "$450,000",
                    "year": "2021",
                    "highlights": [
                        "Powers 500 homes with renewable energy",
                        "Processes 10,000 tons of organic waste",
                        "Received Green Energy Award 2023"
                    ]
                }
            ]
            
            for study in case_studies:
                with st.expander(f"**{study['company']}** - {study['location']} ({study['year']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Business Type:** {study['business']}")
                        st.markdown(f"**Initial Investment:** {study['investment']}")
                        st.markdown(f"**Annual Revenue:** {study['annual_revenue']}")
                    
                    with col2:
                        st.markdown("**Key Highlights:**")
                        for highlight in study['highlights']:
                            st.markdown(f"✓ {highlight}")
                    
                    if st.button(f"View Full Case Study", key=study['company']):
                        st.info("Full case study PDF will be sent to your email!")
        
        with tab4:
            st.markdown("### 📚 Resources & Templates")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📄 Business Plan Templates**")
                
                templates = [
                    "Recycling Business Plan.docx",
                    "Composting Operation Proposal.pdf",
                    "Biogas Project Feasibility Study.xlsx",
                    "Upcycling Workshop Business Model.pptx",
                    "E-Waste Recycling Permit Application.docx"
                ]
                
                for template in templates:
                    if st.button(f"📥 Download {template}", key=template):
                        st.success(f"Downloading {template}...")
                
                st.markdown("**📊 Financial Templates**")
                
                financial_templates = [
                    "Profit & Loss Statement.xlsx",
                    "Cash Flow Projection.xlsx",
                    "Break-Even Calculator.xlsx",
                    "Investor Pitch Deck.pptx"
                ]
                
                for template in financial_templates:
                    if st.button(f"📥 Download {template}", key=template):
                        st.success(f"Downloading {template}...")
            
            with col2:
                st.markdown("**🎓 Training Materials**")
                
                trainings = [
                    "Waste Sorting Guide",
                    "Safety Protocols Handbook",
                    "Equipment Maintenance Manual",
                    "Employee Training Videos",
                    "Compliance Checklist"
                ]
                
                for training in trainings:
                    if st.button(f"📚 Access {training}", key=training):
                        st.success(f"Access granted to {training}!")
                
                st.markdown("**🤝 Funding Opportunities**")
                
                funding = [
                    "Green Business Grants - Up to $50,000",
                    "Environmental Innovation Fund - $25,000-$100,000",
                    "Small Business Eco-Loans - 2% interest",
                    "Crowdfunding Guide for Waste Ventures"
                ]
                
                for opportunity in funding:
                    st.markdown(f"• {opportunity}")
                    if st.button(f"Apply Now", key=opportunity[:10]):
                        st.info("Application form will open in new window")
    
    def ai_assistant(self):
        """Enhanced AI Assistant chat interface with Gemini integration"""
        st.markdown('<h2 class="section-header">🤖 EcoSmart AI Assistant</h2>', 
                   unsafe_allow_html=True)
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your EcoSmart AI Assistant powered by Google Gemini. How can I help you with waste management today?"}
            ]
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Quick action buttons
        st.markdown("### 💡 Quick Questions")
        col1, col2, col3, col4 = st.columns(4)
        
        quick_questions = {
            "How to recycle plastic?": "What's the best way to recycle plastic bottles and containers?",
            "Bin fill prediction": "Can you help me predict when my waste bins will be full based on current fill rates?",
            "Weather impact": "How does current weather affect waste collection efficiency?",
            "Profit ideas": "What are some profitable waste-to-business ideas I can start?"
        }
        
        with col1:
            if st.button("♻️ Plastic Recycling"):
                st.session_state.messages.append({"role": "user", "content": quick_questions["How to recycle plastic?"]})
                self.generate_ai_response(quick_questions["How to recycle plastic?"])
        
        with col2:
            if st.button("📊 Bin Prediction"):
                st.session_state.messages.append({"role": "user", "content": quick_questions["Bin fill prediction"]})
                self.generate_ai_response(quick_questions["Bin fill prediction"])
        
        with col3:
            if st.button("🌤️ Weather Impact"):
                st.session_state.messages.append({"role": "user", "content": quick_questions["Weather impact"]})
                self.generate_ai_response(quick_questions["Weather impact"])
        
        with col4:
            if st.button("💰 Profit Ideas"):
                st.session_state.messages.append({"role": "user", "content": quick_questions["Profit ideas"]})
                self.generate_ai_response(quick_questions["Profit ideas"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about waste management..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate AI response
            self.generate_ai_response(prompt)
        
        # Clear chat button
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your EcoSmart AI Assistant powered by Google Gemini. How can I help you with waste management today?"}
            ]
            st.rerun()
    
    def generate_ai_response(self, prompt):
        """Generate AI response using Gemini API"""
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Create context about current app state
                context = f"""
                Current weather: {self.weather_data['temperature']}°C, {self.weather_data['description']}
                Active bins: {len(self.bin_data)}
                Bins needing collection: {len(self.bin_data[self.bin_data['status'] == 'red'])}
                Average fill level: {self.bin_data['fill_level'].mean():.1f}%
                """
                
                # Get response from Gemini
                response = self.get_gemini_response(prompt, context)
                
                # Add response to session state and display
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.markdown(response)
    
    def run(self):
        """Main application runner"""
        selection = self.sidebar_navigation()
        
        if "Dashboard" in selection:
            self.dashboard_overview()
        elif "Smart Bin" in selection:
            self.smart_bin_analysis()
        elif "Route" in selection:
            self.route_optimization()
        elif "Waste Classification" in selection:
            self.waste_classification()
        elif "Agricultural" in selection:
            self.agricultural_waste()
        elif "Weather" in selection:
            self.weather_analysis()
        elif "Water" in selection:
            self.water_pollution()
        elif "Profit" in selection:
            self.waste_to_profit()
        elif "AI" in selection:
            self.ai_assistant()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div class="footer">
            <p>🌍 EcoSmart Waste Management System | Making waste management smarter, greener, and more profitable</p>
            <p>© 2024 EcoSmart Solutions | Version 2.0 | Powered by Google Gemini AI | <a href="#">Privacy Policy</a> | <a href="#">Terms of Use</a></p>
        </div>
        """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    app = WasteManagementApp()
    app.run()