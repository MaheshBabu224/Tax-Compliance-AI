"""
Configuration management for Tax Compliance AI system
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===== DATA GENERATION CONFIG =====
DATA_CONFIG = {
    "output_dir": "data",
    "output_file": "data/tax_profiles.csv",
    "num_records": int(os.getenv("NUM_RECORDS", 5000)),
    "random_seed": int(os.getenv("RANDOM_SEED", 42)),
}

# ===== TAXPAYER DATA CONFIG =====
TAXPAYER_DATA = {
    "names": ["Ravi Kumar", "Anjali Rao", "Rahul Sharma", "Arjun Mehta", "Priya Singh"],
    "cities": ["Hyderabad", "Chennai", "Delhi", "Mumbai", "Bangalore"],
}

# ===== INCOME SIMULATION CONFIG =====
INCOME_CONFIG = {
    "declared_min": int(os.getenv("DECLARED_MIN", 200000)),
    "declared_max": int(os.getenv("DECLARED_MAX", 1500000)),
    "risk_cases": {
        "low": {"weight": 0.40, "extra_min": 0, "extra_max": 50000},
        "medium": {"weight": 0.35, "extra_min": 50000, "extra_max": 150000},
        "high": {"weight": 0.20, "extra_min": 150000, "extra_max": 300000},
        "critical": {"weight": 0.05, "extra_min": 300000, "extra_max": 700000},
    },
    "tax_evasion_rate": float(os.getenv("TAX_EVASION_RATE", 0.3)),
}

# ===== ML MODEL CONFIG =====
ML_CONFIG = {
    "anomaly_contamination": float(os.getenv("ANOMALY_CONTAMINATION", 0.15)),
    "random_state": int(os.getenv("ML_RANDOM_STATE", 42)),
    "model_save_path": "backend/models/isolation_forest.joblib",
}

# ===== RISK SCORING CONFIG =====
RISK_THRESHOLDS = {
    "low": {"max": 20},
    "medium": {"min": 20, "max": 40},
    "high": {"min": 40, "max": 70},
    "critical": {"min": 70},
}

# ===== RISK SCORE CALCULATION CONFIG =====
RISK_SCORE_CONFIG = {
    "divisor": int(os.getenv("RISK_DIVISOR", 1000)),
    "max_score": int(os.getenv("RISK_MAX_SCORE", 100)),
}

# ===== API CONFIG =====
API_CONFIG = {
    "host": os.getenv("API_HOST", "localhost"),
    "port": int(os.getenv("API_PORT", 5000)),
    "debug": os.getenv("API_DEBUG", "False").lower() == "true",
}

# ===== LOGGING CONFIG =====
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/app.log",
}

# ===== DATABASE CONFIG =====
DB_CONFIG = {
    "type": os.getenv("DB_TYPE", "csv"),  # csv, sqlite, postgresql
    "sqlite_path": "data/tax_compliance.db",
}

# ===== CITY COORDINATES =====
CITY_COORDINATES = {
    "Hyderabad": [17.385, 78.4867],
    "Chennai": [13.0827, 80.2707],
    "Delhi": [28.7041, 77.1025],
    "Mumbai": [19.0760, 72.8777],
    "Bangalore": [12.9716, 77.5946],
}

# ===== DEFAULT COORDINATES (if city not found) =====
DEFAULT_COORDINATES = [20.5937, 78.9629]
