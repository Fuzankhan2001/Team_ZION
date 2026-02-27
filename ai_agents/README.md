# AI Agents

AI-powered hospital monitoring and referral agents.

## Components (planned)
- `hospital_aggregator.py` — Aggregate MQTT sensor events per hospital
- `state_updator_agent.py` — Write aggregated state to PostgreSQL
- `monitoring_agent.py` — Detect resource risks, generate alerts
- `referral_agent.py` — Score & recommend hospitals for patient referrals

## Setup
```bash
pip install -r requirements.txt
```
