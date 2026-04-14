"""
Tax compliance dataset generator with ML anomaly detection
"""
import sys
import os
from pathlib import Path
from sklearn.metrics import accuracy_score


# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import random
import logging
from sklearn.ensemble import IsolationForest

# Setup logging
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/data_generation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import configuration
from config import (
    DATA_CONFIG,
    TAXPAYER_DATA,
    INCOME_CONFIG,
    ML_CONFIG,
    RISK_THRESHOLDS,
    RISK_SCORE_CONFIG,
)
from backend.model import calculate_risk, explain_risk
from backend.model_manager import ModelManager


def generate_dataset():
    """Generate synthetic tax compliance dataset"""
    logger.info("Starting dataset generation...")
    
    # Create directories
    Path(DATA_CONFIG["output_dir"]).mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    names = TAXPAYER_DATA["names"]
    cities = TAXPAYER_DATA["cities"]
    
    random.seed(DATA_CONFIG["random_seed"])
    
    data = []
    logger.info(f"Generating {DATA_CONFIG['num_records']} tax records...")
    
    for i in range(DATA_CONFIG["num_records"]):
        name = random.choice(names)
        city = random.choice(cities)
        
        declared = random.randint(
            INCOME_CONFIG["declared_min"],
            INCOME_CONFIG["declared_max"]
        )
        
        # Select risk case based on weights
        risk_cases = INCOME_CONFIG["risk_cases"]
        case = random.choices(
            list(risk_cases.keys()),
            weights=[risk_cases[c]["weight"] for c in risk_cases.keys()]
        )[0]
        
        case_config = risk_cases[case]
        extra = random.randint(case_config["extra_min"], case_config["extra_max"])
         
        estimated = declared + extra
        tax_evaded = int(extra * INCOME_CONFIG["tax_evasion_rate"])
        # ✅ ADD NOISE

        declared += np.random.randint(-20000, 20000)
        estimated += np.random.randint(-30000, 30000)

        # keep values valid
        declared = max(10000, declared)
        estimated = max(declared, estimated)

        # ✅ TRUE LABEL (ground truth)
        is_anomaly = 1 if extra > 70000 else 0

        
        # Calculate risk using model function
        risk_score, risk_level = calculate_risk(declared, estimated)
        
        data.append({
            "PersonID": f"P{1000+i}",
            "Name": name,
            "City": city,
            "DeclaredIncome": declared,
            "EstimatedIncome": estimated,
            "TaxEvaded": tax_evaded,
            "RiskScore": risk_score,
            "RiskLevel": risk_level,
            "TrueLabel": is_anomaly
        })
    
    df = pd.DataFrame(data)
    logger.info(f"Created {len(df)} records")
    
    # ML Anomaly Detection
    logger.info("Training Isolation Forest model...")
    model = IsolationForest(
        contamination=ML_CONFIG["anomaly_contamination"],
        random_state=ML_CONFIG["random_state"]
    )
    
    df["Anomaly"] = model.fit_predict(
        df[["DeclaredIncome", "EstimatedIncome", "TaxEvaded"]]
    )
    df["Anomaly"] = df["Anomaly"].map({1: "Normal", -1: "Anomaly"})
    y_pred = df["Anomaly"].map({"Normal": 0, "Anomaly": 1})
    y_true = df["TrueLabel"]

    accuracy = accuracy_score(y_true, y_pred)
    
    logger.info(f"Anomalies detected: {len(df[df['Anomaly'] == 'Anomaly'])}")
    
    # Add AI explanations
    df["AI_Reason"] = df.apply(explain_risk, axis=1)
    
    # Save dataset
    output_path = DATA_CONFIG["output_file"]
    df.to_csv(output_path, index=False)
    logger.info(f"[SUCCESS] Dataset saved to {output_path}")
    
    # Save model
    manager = ModelManager()
    metadata = {
        "records": len(df),
        "anomaly_contamination": ML_CONFIG["anomaly_contamination"],
        "random_state": ML_CONFIG["random_state"],
    }
    manager.save_model(model, metadata)
    logger.info("[SUCCESS] Model saved")
    
    # Print summary
    print("\n" + "="*50)
    print("DATASET GENERATION SUMMARY")
    print("="*50)
    print(f"Total Records: {len(df)}")
    print(f"Risk Distribution:")
    print(df["RiskLevel"].value_counts().to_string())
    print(f"\nAnomalies: {len(df[df['Anomaly'] == 'Anomaly'])}")
    print("="*50 + "\n")


if __name__ == "__main__":
    try:
        generate_dataset()
    except Exception as e:
        logger.error(f"Dataset generation failed: {e}", exc_info=True)
        sys.exit(1)