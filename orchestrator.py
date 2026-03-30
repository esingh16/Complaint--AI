"""
Main Orchestrator: Coordinates all agents to process complaints end-to-end.
"""

import json
import time
import pandas as pd
from datetime import datetime
from typing import Optional
from agents.classifier_agent import classify_complaint
from agents.root_cause_agent import analyze_root_cause
from agents.assignment_agent import assign_complaint
from agents.resolution_agent import generate_resolution


def process_complaint(
    narrative: str,
    complaint_id: Optional[str] = None,
    verbose: bool = True
) -> dict:
    """
    Full pipeline: takes a complaint narrative → returns complete resolution package.
    
    Args:
        narrative: The complaint text
        complaint_id: Optional ID
        verbose: Print progress
    
    Returns:
        Complete complaint resolution package
    """
    if not complaint_id:
        complaint_id = f"COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🔄 Processing Complaint: {complaint_id}")
        print(f"{'='*60}")
    
    # --- AGENT 1: Classify ---
    if verbose: print("\n📊 Step 1/4: Classifying complaint...")
    t0 = time.time()
    classification = classify_complaint(narrative, complaint_id)
    if verbose:
        print(f"  ✅ Done in {time.time()-t0:.1f}s")
        print(f"  → Issue: {classification.get('issue_type')}")
        print(f"  → Severity: {classification.get('severity')}")
        print(f"  → Compliance Risk: {classification.get('compliance_risk')}")
    
    # --- AGENT 2: Root Cause ---
    if verbose: print("\n🔍 Step 2/4: Analyzing root cause...")
    t0 = time.time()
    root_cause = analyze_root_cause(narrative, classification, complaint_id)
    if verbose:
        print(f"  ✅ Done in {time.time()-t0:.1f}s")
        print(f"  → Root Cause: {root_cause.get('primary_root_cause')}")
        print(f"  → Systemic: {root_cause.get('systemic_issue')}")
    
    # --- AGENT 3: Assign ---
    if verbose: print("\n🎯 Step 3/4: Assigning to teams...")
    t0 = time.time()
    assignment = assign_complaint(classification, root_cause, complaint_id)
    if verbose:
        print(f"  ✅ Done in {time.time()-t0:.1f}s")
        print(f"  → Primary Team: {assignment.get('primary_team')}")
        print(f"  → Priority: {assignment.get('priority')}")
        print(f"  → Escalate: {assignment.get('escalate_immediately')}")
    
    # --- AGENT 4: Resolution ---
    if verbose: print("\n📋 Step 4/4: Generating resolution plan...")
    t0 = time.time()
    resolution = generate_resolution(narrative, classification, root_cause, assignment, complaint_id)
    if verbose:
        print(f"  ✅ Done in {time.time()-t0:.1f}s")
        print(f"  → Resolution: {resolution.get('resolution_summary')}")
    
    # --- Package Result ---
    result = {
        "complaint_id": complaint_id,
        "processed_at": datetime.now().isoformat(),
        "narrative": narrative,
        "classification": classification,
        "root_cause": root_cause,
        "assignment": assignment,
        "resolution": resolution,
        "pipeline_version": "1.0.0"
    }
    
    if verbose:
        print(f"\n✅ Complaint {complaint_id} fully processed!")
    
    return result


def process_batch(
    input_csv: str = "data/complaints.csv",
    output_json: str = "data/results.json",
    max_complaints: int = 20
) -> list[dict]:
    """
    Processes a batch of complaints from CSV.
    
    Args:
        input_csv: Path to complaints CSV
        output_json: Where to save results
        max_complaints: Cap to avoid high API costs during testing
    
    Returns:
        List of processed complaint packages
    """
    df = pd.read_csv(input_csv)
    df = df.dropna(subset=["narrative"])
    df = df.head(max_complaints)
    
    print(f"\n🚀 Processing {len(df)} complaints...")
    
    results = []
    for i, row in df.iterrows():
        narrative = row.get("narrative", row.get("complaint_what_happened", ""))
        cid = str(row.get("complaint_id", f"COMP-{i:04d}"))
        
        if len(narrative.strip()) < 30:
            print(f"⏭️  Skipping {cid} (narrative too short)")
            continue
        
        try:
            result = process_complaint(narrative, cid, verbose=True)
            results.append(result)
            
            # Save after each complaint (in case of crash)
            with open(output_json, "w") as f:
                json.dump(results, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error processing {cid}: {e}")
    
    print(f"\n🎉 Batch complete! {len(results)}/{len(df)} complaints processed")
    print(f"📄 Results saved to: {output_json}")
    return results


if __name__ == "__main__":
    # Quick single test
    test_complaint = """
    I have been a customer for 3 years and my credit card was suddenly closed without any notice. 
    When I called customer service, they told me it was due to 'account review' but couldn't 
    give me any specific reason. This caused my credit score to drop by 87 points because my 
    credit utilization ratio changed drastically. I had $15,000 in available credit and now 
    I have nothing. I was never late on a payment and always paid more than the minimum. 
    I believe this may be discriminatory as I recently disclosed a disability. 
    I need this account reinstated immediately and my credit score damage addressed.
    """
    
    result = process_complaint(test_complaint, "TEST-001")
    
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))
