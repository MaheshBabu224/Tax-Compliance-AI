"""
Flask REST API for Tax Compliance AI system
"""
import sys
import os
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure directories exist
Path("logs").mkdir(exist_ok=True)

import logging
from flask import Flask, jsonify, request
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import configuration and utilities
from config import API_CONFIG, DATA_CONFIG, CITY_COORDINATES, DEFAULT_COORDINATES
from backend.model import calculate_risk
from backend.model_manager import ModelManager


# Create Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize model manager
model_manager = ModelManager()

# ===== HELPER FUNCTIONS =====

def load_data():
    """Load tax profiles from CSV"""
    try:
        df = pd.read_csv(DATA_CONFIG["output_file"])
        logger.info(f"Loaded {len(df)} records from data")
        return df
    except FileNotFoundError:
        logger.error(f"Data file not found: {DATA_CONFIG['output_file']}")
        return None


# ===== API ROUTES =====

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return jsonify({"status": "healthy", "version": "1.0.0"}), 200


@app.route("/api/data/summary", methods=["GET"])
def get_data_summary():
    """Get summary statistics of tax data"""
    try:
        df = load_data()
        if df is None or df.empty:
            return jsonify({"error": "No data available"}), 404
        
        summary = {
            "total_records": len(df),
            "risk_distribution": df["RiskLevel"].value_counts().to_dict(),
            "anomaly_count": len(df[df["Anomaly"] == "Anomaly"]),
            "avg_risk_score": float(df["RiskScore"].mean()),
            "cities": df["City"].unique().tolist(),
        }
        
        logger.info("Data summary retrieved")
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Error retrieving summary: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/data", methods=["GET"])
def get_data():
    """Get tax profiles with optional filtering"""
    try:
        df = load_data()
        if df is None or df.empty:
            return jsonify({"error": "No data available"}), 404
        
        # Apply filters
        risk_level = request.args.get("risk_level")
        city = request.args.get("city")
        limit = request.args.get("limit", default=100, type=int)
        
        if risk_level:
            df = df[df["RiskLevel"] == risk_level]
            logger.info(f"Filtered by risk level: {risk_level}")
        
        if city:
            df = df[df["City"] == city]
            logger.info(f"Filtered by city: {city}")
        
        # Limit results
        df = df.head(limit)
        
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/taxpayer/<person_id>", methods=["GET"])
def get_taxpayer(person_id):
    """Get specific taxpayer details"""
    try:
        df = load_data()
        if df is None or df.empty:
            return jsonify({"error": "No data available"}), 404
        
        taxpayer = df[df["PersonID"] == person_id]
        if taxpayer.empty:
            return jsonify({"error": f"Taxpayer {person_id} not found"}), 404
        
        logger.info(f"Taxpayer {person_id} retrieved")
        return jsonify(taxpayer.to_dict("records")[0]), 200
    except Exception as e:
        logger.error(f"Error retrieving taxpayer: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/risk/calculate", methods=["POST"])
def calculate_risk_endpoint():
    """Calculate risk for given income values"""
    try:
        data = request.get_json()
        declared = data.get("declared_income")
        estimated = data.get("estimated_income")
        
        if declared is None or estimated is None:
            return jsonify({"error": "Missing required fields"}), 400
        
        score, level = calculate_risk(declared, estimated)
        
        logger.info(f"Risk calculated - score: {score}, level: {level}")
        return jsonify({
            "declared_income": declared,
            "estimated_income": estimated,
            "risk_score": score,
            "risk_level": level,
        }), 200
    except Exception as e:
        logger.error(f"Error calculating risk: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/top-risky", methods=["GET"])
def get_top_risky():
    """Get top risky individuals"""
    try:
        df = load_data()
        if df is None or df.empty:
            return jsonify({"error": "No data available"}), 404
        
        limit = request.args.get("limit", default=10, type=int)
        top_risky = df.nlargest(limit, "RiskScore")[
            ["PersonID", "Name", "City", "DeclaredIncome", "EstimatedIncome", 
             "TaxEvaded", "RiskScore", "RiskLevel", "AI_Reason"]
        ]
        
        logger.info(f"Top {limit} risky individuals retrieved")
        return jsonify(top_risky.to_dict("records")), 200
    except Exception as e:
        logger.error(f"Error retrieving top risky: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/by-city", methods=["GET"])
def analytics_by_city():
    """Get analytics grouped by city"""
    try:
        df = load_data()
        if df is None or df.empty:
            return jsonify({"error": "No data available"}), 404
        
        analytics = df.groupby("City").agg({
            "PersonID": "count",
            "RiskScore": ["mean", "max", "min"],
            "TaxEvaded": "sum",
        }).round(2)
        
        analytics.columns = ["total_records", "avg_risk_score", "max_risk_score", 
                            "min_risk_score", "total_tax_evaded"]
        
        logger.info("City-level analytics retrieved")
        return jsonify(analytics.reset_index().to_dict("records")), 200
    except Exception as e:
        logger.error(f"Error retrieving city analytics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    """Export filtered data as CSV"""
    try:
        df = load_data()
        if df is None or df.empty:
            return jsonify({"error": "No data available"}), 404
        
        risk_level = request.args.get("risk_level")
        if risk_level:
            df = df[df["RiskLevel"] == risk_level]
        
        filename = f"tax_profiles_{risk_level or 'all'}.csv"
        
        logger.info(f"Export requested: {filename}")
        return {
            "status": "success",
            "message": f"Export data to {filename}",
            "records": len(df)
        }
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({"error": str(e)}), 500


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


# ===== STARTUP =====

if __name__ == "__main__":
    logger.info("Starting Tax Compliance AI API...")

    try:
        df = pd.read_csv(DATA_CONFIG["output_file"])
        logger.info("Dataset loaded for evaluation")

        model_manager.evaluate_model(df)

    except Exception as e:
        logger.error(f"Error during model evaluation: {e}")

    app.run(
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        debug=False
    )