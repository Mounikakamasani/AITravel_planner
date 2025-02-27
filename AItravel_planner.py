import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime
API_KEY = "API_KEY" 
genai.configure(api_key=API_KEY)

def fetch_travel_options(source, destination, date):
    """
    Retrieves travel options using Gemini AI and returns them in JSON format.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    prompt = f"""
    You are an AI travel assistant. Provide travel options from {source} to {destination} on {date}.
    Return ONLY structured JSON in this format:
    {{
        "flights": [{{"airline": "Airline Name", "departure": "Time", "arrival": "Time", "duration": "Time", "cost": Amount}}],
        "trains": [{{"name": "Train Name", "departure": "Time", "arrival": "Time", "duration": "Time", "cost": Amount}}],
        "buses": [{{"operator": "Bus Operator", "departure": "Time", "arrival": "Time", "duration": "Time", "cost": Amount}}],
        "cabs": [{{"cost": Amount, "duration": "Time"}}]
    }}
    """
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip() if hasattr(response, 'text') else ""
        
        json_start = response_text.find("{")
        json_end = response_text.rfind("}")
        
        if json_start != -1 and json_end != -1:
            travel_data = json.loads(response_text[json_start:json_end+1])
            return travel_data
        else:
            return {"error": "Invalid response format from AI."}
    except json.JSONDecodeError:
        return {"error": "Error decoding JSON response."}
    except Exception as e:
        return {"error": str(e)}

def summarize_travel_options(travel_data):
    """
    Provides a summary of the best travel options available.
    """
    summary = "### 🔹 Best Travel Options:\n"
    options = []
    
    for category in ["flights", "trains", "buses", "cabs"]:
        if category in travel_data:
            options.extend([(category.capitalize(), option["cost"]) for option in travel_data[category]])
    
    if options:
        best_option = min(options, key=lambda x: x[1])
        summary += f"✔ Cheapest: {best_option[0]} at ₹{best_option[1]}\n"
    
    if "flights" in travel_data:
        summary += "⚡ Fastest: Flight (typically 1-2 hours).\n"
    
    return summary
st.title("🌍 AI Travel Assistant")
st.write("Plan your journey with AI-powered recommendations.")

source = st.text_input("Enter Departure City")
destination = st.text_input("Enter Destination City")
date = st.date_input("Select Travel Date", min_value=datetime.today())

if st.button("Find Travel Options", use_container_width=True):
    if source and destination:
        travel_options = fetch_travel_options(source, destination, date.strftime("%Y-%m-%d"))
        
        if "error" in travel_options:
            st.error(travel_options["error"])
        else:
            st.write(f"### Travel options from {source} to {destination} on {date.strftime('%B %d, %Y')}")
            st.write("---")
            st.markdown(summarize_travel_options(travel_options))
            
            for category, icon in zip(["flights", "trains", "buses", "cabs"], ["✈", "🚆", "🚌", "🚖"]):
                if travel_options.get(category):
                    st.subheader(f"{icon} {category.capitalize()}")
                    for option in travel_options[category]:
                        details = " - ".join([f"**{k.capitalize()}**: {v}" for k, v in option.items()])
                        st.markdown(f"- {details}")
    else:
        st.error("Please provide both source and destination.")
