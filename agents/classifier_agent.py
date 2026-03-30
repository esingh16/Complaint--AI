"""
Classifier Agent: Classifies complaint by product, issue type, severity, and compliance risk.
"""

import anthropic
import json
from typing import Optional

client = anthropic.Anthropic()

CLASSIFICATION_SCHEMA = {
    "product_category": "string (Credit Card | Personal Loan | Digital Banking | Checking Account | Other)",
    "issue_type": "string (Billing Dispute | Fraud | Account Access | Interest Rate | Customer Service | Fees | Loan Servicing | Data Privacy | Other)",
    "severity": "string (low | medium | high | critical)",
    "compliance_risk": "string (none | low | medium | high)",
    "compliance_flags": "list of strings (e.g. UDAAP, FCRA, TILA, ECOA violations)",
    "sentiment_score": "float between -1.0 (very negative) and 1.0 (very positive)",
    "urgency_score": "float between 0.0 (not urgent) and 1.0 (extremely urgent)",
    "reasoning": "string explaining the classification"
}

def classify_complaint(narrative: str, complaint_id: Optional[str] = None) -> dict:
    """
    Classifies a single complaint narrative.
    
    Args:
        narrative: The complaint text
        complaint_id: Optional ID for tracking
    
    Returns:
        dict with classification results
    """
    system_prompt = """You are a financial services compliance expert and complaint analyst.
You classify customer complaints for a national fintech company.
You must identify regulatory risks (UDAAP, FCRA, TILA, ECOA, EFTA, CFPA violations).
Always respond with valid JSON only. No markdown, no explanation outside JSON."""

    user_prompt = f"""Classify this customer complaint:

COMPLAINT:
{narrative}

Return a JSON object with exactly these fields:
{json.dumps(CLASSIFICATION_SCHEMA, indent=2)}

Be precise about compliance_flags - these determine regulatory risk exposure."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    result = json.loads(message.content[0].text.strip())
    result["complaint_id"] = complaint_id
    result["narrative_preview"] = narrative[:200] + "..." if len(narrative) > 200 else narrative
    return result


def batch_classify(narratives: list[dict]) -> list[dict]:
    """
    Classifies multiple complaints.
    
    Args:
        narratives: list of dicts with 'narrative' and optionally 'complaint_id'
    
    Returns:
        list of classification results
    """
    results = []
    for i, item in enumerate(narratives):
        narrative = item.get("narrative", item) if isinstance(item, dict) else item
        cid = item.get("complaint_id", f"COMP-{i:04d}") if isinstance(item, dict) else f"COMP-{i:04d}"
        
        try:
            result = classify_complaint(narrative, cid)
            results.append(result)
            print(f"  ✅ Classified [{cid}] → {result['severity']} severity, {result['issue_type']}")
        except Exception as e:
            print(f"  ❌ Failed to classify [{cid}]: {e}")
            results.append({"complaint_id": cid, "error": str(e)})
    
    return results
