"""
Resolution Agent: Generates complete resolution plan including customer response.
"""

import anthropic
import json
from typing import Optional

client = anthropic.Anthropic()

def generate_resolution(
    narrative: str,
    classification: dict,
    root_cause: dict,
    assignment: dict,
    complaint_id: Optional[str] = None
) -> dict:
    """
    Generates a complete resolution plan for the complaint.
    
    Returns remediation steps, customer response, and preventive measures.
    """
    system_prompt = """You are a senior complaints resolution specialist and compliance officer.
You create complete resolution plans that are:
1. Regulatory-compliant (CFPB, UDAAP, FCRA, TILA standards)
2. Customer-centric and empathetic
3. Actionable with clear owners and timelines
4. Preventive to reduce future recurrence

All customer-facing responses must comply with CFPB Regulation X and EFTA requirements.
Always respond with valid JSON only."""

    user_prompt = f"""Generate a complete resolution plan for this complaint:

ORIGINAL COMPLAINT:
{narrative}

CLASSIFICATION:
{json.dumps(classification, indent=2)}

ROOT CAUSE:
{json.dumps(root_cause, indent=2)}

ASSIGNMENT:
{json.dumps(assignment, indent=2)}

Return a JSON object with these fields:
{{
  "resolution_summary": "1-2 sentence summary of the resolution approach",
  
  "remediation_steps": [
    {{
      "step": 1,
      "action": "specific action to take",
      "owner": "team/role responsible",
      "deadline_hours": number,
      "is_customer_facing": true/false
    }}
  ],
  
  "customer_response_draft": "Full regulatory-compliant letter/email to customer. Be empathetic, acknowledge the issue, explain what will be done, and provide a timeline. Do NOT admit liability without legal review.",
  
  "regulatory_response_notes": "Notes for compliance team about regulatory reporting requirements",
  
  "preventive_recommendations": [
    {{
      "recommendation": "description",
      "impact": "what this prevents",
      "effort": "low | medium | high",
      "timeline": "immediate | short-term | long-term"
    }}
  ],
  
  "compensation_recommended": true/false,
  "compensation_details": "if recommended, what and how much",
  
  "case_closure_criteria": ["conditions that must be met before closing this case"],
  
  "estimated_resolution_hours": number
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    result = json.loads(message.content[0].text.strip())
    result["complaint_id"] = complaint_id
    return result
