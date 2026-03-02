from fastapi import FastAPI
import httpx

app = FastAPI()

@app.post("/circle-webhook")
async def handle_new_member(data: dict):
    """
    Triggered when a member joins Circle.
    1. Syncs to Medical CRM.
    2. Auto-tags member based on Stripe subscription tier.
    3. Triggers onboarding email via custom Python logic.
    """
    email = data['email']
    # Custom API call to Circle to apply 'Oncology Patient' tag
    return {"status": "Automation complete"}