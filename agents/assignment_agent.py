"""
Assignment Agent: Routes complaint to the appropriate internal team.
"""

import anthropic
import json
from typing import Optional

client = anthropic.Anthropic()

# Internal team definitions — customize these for your org
TEAMS = {
    "fraud_and_security": {
        "name": "Fraud & Security Team",
        "handles": ["Fraud", "Unauthorized transactions", "Identity theft", "Account takeover"],
        "sla_hours": 4,
        "escalation_path": "CISO → Legal"
    },
    "billing_and_disputes": {
        "name": "Billing & Disputes Team",
        "handles": ["Billing Dispute", "Incorrect charges", "Refund issues", "Fee disputes"],
        "sla_hours": 24,
        "escalation_path": "VP Operations"
    },
    "compliance_and_legal": {
        "name": "Compliance & Legal Team",
        "handles": ["Regulatory violations", "UDAAP", "FCRA", "TILA", "Discrimination"],
        "sla_hours": 2,
        "escalation_path": "Chief Compliance Officer → General Counsel"
    },
    "customer_experience": {
        "name": "Customer Experience Team",
        "handles": ["Customer Service", "General dissatisfaction", "Process complaints"],
        "sla_hours": 48,
        "escalation_path": "VP Customer Success"
    },
    "technical_support": {
        "name": "Technical Support Team",
        "handles": ["Account Access", "App issues", "Login problems", "Digital Banking issues"],
        "sla_hours": 8,
        "escalation_path": "VP Engineering"
    },
    "loan_servicing": {
        "name": "Loan Servicing Team",
        "handles": ["Loan Servicing", "Interest Rate", "Payment processing", "Loan modifications"],
        "sla_hours": 24,
        "escalation_path": "VP Lending"
    },
    "data_privacy": {
        "name": "Data Privacy Team",
        "handles": ["Data Privacy", "Data sharing", "CCPA", "GDPR"],
        "sla_hours": 12,
        "escalation_path": "Chief Privacy Officer"
    }
}

def assign_complaint(
    classification: dict,
    root_cause: dict,
    complaint_id: Optional[str] = None
) -> dict:
    """
    Assigns the complaint to the appropriate team(s).
    """
    system_prompt = """You are a complaint routing system for a fintech company.
You assign complaints to internal teams based on classification and root cause.
You must consider severity, compliance risk, and SLA requirements.
Always respond with valid JSON only."""

    user_prompt = f"""Route this complaint to the appropriate team(s):

CLASSIFICATION:
{json.dumps(classification, indent=2)}

ROOT CAUSE:
{json.dumps(root_cause, indent=2)}

AVAILABLE TEAMS:
{json.dumps(TEAMS, indent=2)}

Return a JSON object with these fields:
{{
  "primary_team": "team_key from AVAILABLE TEAMS",
  "secondary_teams": ["list of additional team keys if needed"],
  "priority": "P1 | P2 | P3 | P4",
  "sla_hours": number (override SLA if needed),
  "escalate_immediately": true/false,
  "escalation_reason": "why escalation is needed (or null)",
  "routing_rationale": "explain why these teams were selected",
  "required_actions": ["list", "of", "immediate", "actions", "required"]
}}

Priority levels: P1=critical/compliance risk (resolve in hours), P2=high (24h), P3=medium (72h), P4=low (1 week)"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    result = json.loads(message.content[0].text.strip())
    result["complaint_id"] = complaint_id
    
    # Attach full team info
    primary = result.get("primary_team", "")
    if primary in TEAMS:
        result["primary_team_info"] = TEAMS[primary]
    
    return result
