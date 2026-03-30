"""
Root Cause Agent: Identifies the underlying root cause of a complaint.
"""

import anthropic
import json
from typing import Optional

client = anthropic.Anthropic()

def analyze_root_cause(
    narrative: str,
    classification: dict,
    complaint_id: Optional[str] = None
) -> dict:
    """
    Performs root cause analysis on a classified complaint.
    
    Args:
        narrative: Original complaint text
        classification: Output from classifier_agent
        complaint_id: Optional tracking ID
    
    Returns:
        dict with root cause analysis
    """
    system_prompt = """You are a root cause analysis expert for financial services operations.
You identify systemic failures, process breakdowns, and their contributing factors.
You think in terms of: People, Process, Technology, Policy, and External factors.
Always respond with valid JSON only."""

    user_prompt = f"""Perform root cause analysis for this complaint:

COMPLAINT:
{narrative}

CLASSIFICATION:
- Issue Type: {classification.get('issue_type')}
- Severity: {classification.get('severity')}
- Product: {classification.get('product_category')}
- Compliance Risk: {classification.get('compliance_risk')}
- Compliance Flags: {classification.get('compliance_flags', [])}

Return a JSON object with these fields:
{{
  "primary_root_cause": "the single most important root cause",
  "root_cause_category": "People | Process | Technology | Policy | External",
  "contributing_factors": ["list", "of", "secondary", "factors"],
  "systemic_issue": true/false (is this likely affecting other customers?),
  "systemic_issue_description": "if systemic, describe the broader pattern",
  "customer_impact": "description of how this has impacted the customer",
  "business_impact": "description of operational/financial/reputational risk",
  "recurrence_risk": "low | medium | high",
  "evidence_from_narrative": "specific phrases/facts from complaint supporting this analysis"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1200,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    result = json.loads(message.content[0].text.strip())
    result["complaint_id"] = complaint_id
    return result
