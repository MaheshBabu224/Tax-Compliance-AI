# SatyaTax: AI-Based Tax Compliance System

An intelligent system for detecting and monitoring tax compliance anomalies using machine learning algorithms.

## Overview

SatyaTax is a comprehensive tax compliance monitoring system that combines synthetic data generation, machine learning anomaly detection, and interactive visualization to identify suspicious tax patterns and potential cases of tax evasion.

### Key Features

- 🤖 **ML Anomaly Detection** - Isolation Forest algorithm for detecting suspicious patterns
- 📊 **Risk Scoring** - Intelligent scoring based on income discrepancies
- 🗺️ **Geographic Analysis** - City-level risk assessment and visualization
- 🔍 **Individual Search** - Detailed taxpayer profiles and analytics
- 📈 **Advanced Analytics** - Comprehensive data insights and trends
- 🔌 **REST API** - Backend API for programmatic access
- 💾 **Model Persistence** - Trained models saved and versioned
- 📝 **Comprehensive Logging** - Detailed logs for monitoring and debugging

## Architecture

```
┌─────────────────────────────────────────────────┐
│                Frontend (Streamlit)             │
│   Dashboard | Search | Map | Analytics | About  │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│           Backend API (Flask/REST)              │
│   /api/data | /api/risk | /api/analytics       │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │  Data  │  │  ML    │  │ Logging  │
    │  CSV   │  │ Models │  │   Logs   │
    └────────┘  └────────┘  └──────────┘
```

## Project Structure

```
Tax_Compliance_AI/
├── config.py                           # Configuration management
├── generate_dataset.py                 # Synthetic data generation
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── run.sh                              # Startup script
├── README.md                           # This file
│
├── backend/
│   ├── model.py                        # Risk calculation & ML utilities
│   ├── model_manager.py                # Model persistence layer
│   ├── api.py                          # Flask REST API
│   └── models/                         # Saved models directory
│
├── frontend/
│   └── dashboard.py                    # Streamlit dashboard
│
└── data/
    └── tax_profiles.csv                # Generated dataset
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Step 1: Clone/Setup
```bash
cd Tax_Compliance_AI
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate    # On Windows
# OR
source venv/bin/activate        # On macOS/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
```bash
cp .env.example .env
# Edit .env with your preferred settings (optional)
```

## Usage

### Generate Dataset
```bash
python generate_dataset.py
```
This creates:
- `data/tax_profiles.csv` - Synthetic tax compliance data
- `backend/models/model_v1_*.joblib` - Trained ML model
- `logs/data_generation.log` - Generation logs

### Start the Dashboard
```bash
streamlit run frontend/dashboard.py
```
Access at: `http://localhost:8501`

### Start the Backend API
```bash
python backend/api.py
```
API runs at: `http://localhost:5000`

### Quick Start (All-in-one)
```bash
bash run.sh
```

## Configuration

Edit `config.py` or `.env` to customize:

### Data Generation
- `NUM_RECORDS` - Number of synthetic records (default: 5000)
- `RANDOM_SEED` - Random seed for reproducibility
- `DECLARED_MIN/MAX` - Income range for generated data

### ML Model
- `ANOMALY_CONTAMINATION` - Anomaly percentage (default: 0.15)
- `ML_RANDOM_STATE` - Model random state

### Risk Scoring
- `RISK_DIVISOR` - Divisor for risk score calculation
- `RISK_MAX_SCORE` - Maximum risk score (default: 100)

### API
- `API_HOST` - API host (default: localhost)
- `API_PORT` - API port (default: 5000)

## API Endpoints

### Health & Summary
- `GET /api/health` - Health check
- `GET /api/data/summary` - Dataset summary

### Data Access
- `GET /api/data` - Get tax profiles (with filters)
- `GET /api/data?risk_level=Critical&limit=100` - Filter by risk level
- `GET /api/taxpayer/<person_id>` - Get specific taxpayer

### Analytics
- `GET /api/analytics/top-risky` - Top 10 risky individuals
- `GET /api/analytics/by-city` - Analytics by city

### Risk Calculation
- `POST /api/risk/calculate` - Calculate risk for income values
  ```json
  {
    "declared_income": 500000,
    "estimated_income": 750000
  }
  ```

### Export
- `GET /api/export/csv` - Export data as CSV

## Dashboard Features

### Dashboard Page
- **Risk Distribution** - Visual breakdown of risk levels
- **Top Risky Individuals** - List of most suspicious cases
- **Risk Score Distribution** - Histogram of risk scores
- **City Analysis** - Average risk by geographic location

### Search Page
- Search individual taxpayers
- View detailed profile information
- Check anomaly status
- Review AI analysis

### Map Page
- Geographic visualization of taxpayers
- City-level risk assessment

### Analytics Page
- Advanced data insights
- Trend analysis
- Risk patterns by city
- Top suspicious individuals

## Risk Scoring Formula

```
Risk Score = min(100, (EstimatedIncome - DeclaredIncome) / 1000)

Risk Levels:
- Low: Score < 20
- Medium: 20 <= Score < 40
- High: 40 <= Score < 70
- Critical: Score >= 70
```

## ML Model

**Algorithm:** Isolation Forest (scikit-learn)

**Features Used:**
- Declared Income
- Estimated Income
- Tax Evaded

**Configuration:**
- Contamination: 0.15 (15% expected anomalies)
- Random State: 42 (reproducibility)

## Logging

Logs are stored in the `logs/` directory:

- `app.log` - General application logs
- `data_generation.log` - Dataset generation logs
- `api.log` - REST API logs
- `dashboard.log` - Streamlit dashboard logs

Access logs to monitor system behavior and troubleshoot issues.

## Model Persistence

Trained models are saved with versions:

```
backend/models/
├── model_v1_20240325_123456.joblib
├── model_v1_20240325_123456_meta.txt
├── model_v2_20240326_145730.joblib
├── model_v2_20240326_145730_meta.txt
└── version.txt
```

Models are automatically loaded from the latest version.

## Performance Metrics

**Dataset Statistics:**

| Metric | Value |
|--------|-------|
| Total Records | 5,000 |
| Risk Levels | 4 (Low, Medium, High, Critical) |
| Cities | 5 |
| Anomalies | ~750 |
| ML Model Type | Isolation Forest |

## Troubleshooting

### Dataset not loading
```bash
# Regenerate dataset
python generate_dataset.py
```

### API not starting
```bash
# Check if port 5000 is in use
# Modify API_PORT in .env and restart
```

### Streamlit connection issues
```bash
# Clear cache and restart
streamlit run frontend/dashboard.py --logger.level=debug
```

### No models found
```bash
# Ensure data is generated first
python generate_dataset.py
```

## Future Enhancements

- [ ] Database integration (PostgreSQL/SQLite)
- [ ] Advanced ML models (XGBoost, Neural Networks)
- [ ] Authentication & Authorization
- [ ] Real data import from tax authorities
- [ ] Export to PDF/Excel
- [ ] Alerting system
- [ ] Historical trend analysis
- [ ] Docker containerization
- [ ] CI/CD pipeline

## Development

### Add New Feature
1. Create feature branch
2. Update relevant config in `config.py`
3. Add logging for debugging
4. Update README with new features
5. Test with sample data

### Extend ML Model
Edit `backend/model.py` and `generate_dataset.py`:
```python
# Add new features or algorithms
# Update configuration in config.py
# Regenerate dataset for testing
```

## Testing

Run the system with sample data:
```bash
python generate_dataset.py
streamlit run frontend/dashboard.py
```

Then test features via UI or API.

## Performance Tips

- Cache data loading with `@st.cache_data`
- Optimize queries with filters
- Use API pagination for large datasets
- Regular model retraining

## License

Proprietary - All Rights Reserved

## Support

For issues, questions, or contributions:
1. Check this README
2. Review logs in `logs/` directory
3. Check configuration in `config.py`

## Version

**Current Version:** 1.0.0

**Last Updated:** March 2024

---

© 2024 Tax Compliance AI System
