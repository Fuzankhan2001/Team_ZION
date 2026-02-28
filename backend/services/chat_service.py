import os
from groq import Groq
from app.database import execute_query
import json
from dotenv import load_dotenv


# Get the API key securely
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
# Initialize the Groq client
client = Groq(api_key=api_key)

def get_live_data(facility_id):
    """Fetches real-time dashboard data for context.""" 
    query = "SELECT * FROM hospital_live_dashboard WHERE facility_id = %s"
    return execute_query(query, (facility_id,), fetch_one=True)

def process_chat_message(user_message, facility_id, mode="NORMAL", triage_context=None):
    # 1. Fetch Real Context
    data = get_live_data(facility_id)
    if not data:
        return "System Error: Cannot access hospital sensors."

    context_str = f"""
    Current Vitals:
    - Oxygen Level: {data['oxygen_percent']}% ({data['oxygen_status']})
    - Beds Occupied: {data['beds_occupied']}/{data['beds_total']}
    - Ventilators In Use: {data['ventilators_in_use']}/{data['ventilators_total']}
    """

    # 2. Add Predictive Context (The "Future" Brain)
    prediction_str = ""
    if triage_context:
        prediction_str = f"""
        PREDICTIVE ANALYTICS (TRIAGE ENGINE):
        - Status: {triage_context.get('status', 'UNKNOWN')}
        - AI Analysis: "{triage_context.get('message', 'N/A')}"
        - Time to Failure: {triage_context.get('hours_remaining', 99)} HOURS
        """

    # 3. SELECT THE PERSONALITY
    if mode == "CRITICAL":
        system_prompt = f"""
        ROLE: You are the INCIDENT COMMANDER for a hospital in CRISIS.
        
        CRITICAL SITUATION REPORT:
        {context_str}
        {prediction_str}
        
        INSTRUCTIONS:
        1. Your tone must be URGENT, DIRECTIVE, and MILITARY-STYLE.
        2. Do not explain "why" unless asked. Give ORDERS.
        3. If "Time to Failure" is low (under 2 hours), scream for immediate resupply.
        4. Recommend diverting ambulances if Beds or Oxygen are failing.
        
        Example Response:
        "**ACTION REQUIRED:** Oxygen reserves failing in 0.4 hours. 
        1. Divert all incoming trauma cases to Sahyadri. 
        2. Dispatch Emergency Cryogenic Tanker immediately."
        """
    else:
        system_prompt = f"""
        ROLE: You are a Helpful Operations Analyst.
        
        STATUS REPORT:
        {context_str}
        {prediction_str}
        
        INSTRUCTIONS:
        - Answer the user's question using the data.
        - If the user asks about the future, quote the "Predictive Analytics" section.
        - Keep answers professional and detailed.
        """

    # 4. Call AI
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3 if mode == "CRITICAL" else 0.7,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "⚠️ AI Link Unstable. Executing manual override protocols."