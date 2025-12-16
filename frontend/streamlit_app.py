import streamlit as st
import json
import sys
import os

# Page Config MUST be the first line
st.set_page_config(page_title="✈️ AI Travel Planner", layout="wide")

# Setup Path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.join(current_dir, '..')
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Import Backend
try:
    from backend.agent.travel_agent import initialize_travel_agent, run_travel_agent
except ImportError as e:
    st.error(f"Critical Error: Could not import backend. Details: {e}")
    st.stop()

st.title("✈️ AI Travel Itinerary Generator")

# Initialize Agent
if 'agent' not in st.session_state:
    try:
        with st.spinner("Initializing AI Agent..."):
            st.session_state.agent = initialize_travel_agent()
            st.success("AI Agent Ready!")
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        st.info("Please check if GOOGLE_API_KEY is set in .env file.")
        st.stop()

# UI Inputs
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Plan Your Trip")
    source = st.text_input("From", "Delhi")
    destination = st.text_input("To", "Goa")
    days = st.number_input("Days", 1, 15, 3)
    budget = st.selectbox("Budget", ["Budget", "Luxury"])
    btn = st.button("Generate Plan", type="primary")

with col2:
    if btn:
        query = f"Plan a {days}-day trip from {source} to {destination}. Budget: {budget}. Include flights, hotels, places, weather, and budget breakdown."
        
        st.info("AI is thinking...")
        
        try:
            # Run Agent
            response = run_travel_agent(query, st.session_state.agent)
            
            # Clean and Parse JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].strip()
            
            data = json.loads(response)
            
            # Display Results
            st.success("Plan Generated!")
            
            # Summary
            st.header("Trip Summary")
            st.write(data.get("trip_summary", ""))
            st.write(f"**Total Budget:** ₹{data.get('total_budget_estimated', 0)}")
            st.write(f"**Reasoning:** {data.get('reasoning', '')}")
            
            st.markdown("---")
            
            # Flight & Hotel
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Flight")
                st.json(data.get("flight_selected", {}))
            with c2:
                st.subheader("Hotel")
                st.json(data.get("hotel_selected", {}))
            
            # Day Wise
            st.subheader("Day-wise Plan")
            for day in data.get("day_wise_plan", []):
                st.markdown(f"**Day {day.get('day', '?')}:** {day.get('activity', '')} ({day.get('note', '')})")
                st.markdown("---")
                
        except Exception as e:
            st.error(f"Error: {e}")
            st.write("Raw Response:", response if 'response' in locals() else "No response")