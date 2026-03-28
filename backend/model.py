"""
Tax risk calculation and ML model utilities
"""
import sys
import os
import logging

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import RISK_SCORE_CONFIG, RISK_THRESHOLDS

logger = logging.getLogger(__name__)


def calculate_risk(declared, estimated):
    """
    Calculate risk score and level based on income discrepancy
    
    Args:
        declared: Declared income amount
        estimated: Estimated income amount
        
    Returns:
        Tuple of (risk_score, risk_level)
    """
    gap = estimated - declared
    score = min(RISK_SCORE_CONFIG["max_score"], int(gap / RISK_SCORE_CONFIG["divisor"]))
    
    logger.debug(f"Risk calculated - declared: {declared}, estimated: {estimated}, score: {score}")

    if score < RISK_THRESHOLDS["low"]["max"]:
        level = "Low"
    elif score < RISK_THRESHOLDS["high"]["min"]:
        level = "Medium"
    elif score < RISK_THRESHOLDS["critical"]["min"]:
        level = "High"
    else:
        level = "Critical"
    
    return score, level


def explain_risk(row):
    """
    Generate AI explanation for risk level
    
    Args:
        row: DataFrame row with TaxEvaded and RiskLevel columns
        
    Returns:
        Explanation string
    """
    risk_level = row.get("RiskLevel", "Unknown")
    tax_evaded = row.get("TaxEvaded", 0)
    
    if risk_level == "Critical":
        explanation = f"Severe income mismatch - {tax_evaded:,} in suspected tax evasion"
    elif risk_level == "High":
        explanation = f"High discrepancy detected - {tax_evaded:,} tax evasion suspected"
    elif risk_level == "Medium":
        explanation = f"Moderate mismatch - {tax_evaded:,} potential underpayment"
    else:
        explanation = "Normal tax compliance pattern"
    
    return explanation