"""
Model persistence and management utilities
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import joblib
import logging

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class ModelManager:
    """Handles model saving, loading, and versioning"""

    def __init__(self, model_dir="backend/models"):
        self.model_dir = model_dir
        Path(self.model_dir).mkdir(parents=True, exist_ok=True)
        self.version_file = os.path.join(self.model_dir, "version.txt")

    def save_model(self, model, metadata=None):
        """
        Save model to disk with metadata
        
        Args:
            model: The trained model to save
            metadata: Dictionary with model metadata (accuracy, timestamp, etc.)
            
        Returns:
            Path to the saved model
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self._get_next_version()
        
        model_path = os.path.join(
            self.model_dir, 
            f"model_v{version}_{timestamp}.joblib"
        )
        
        try:
            joblib.dump(model, model_path)
            logger.info(f"Model saved to {model_path}")
            
            # Save metadata
            if metadata:
                metadata_path = model_path.replace(".joblib", "_meta.txt")
                with open(metadata_path, "w") as f:
                    for key, value in metadata.items():
                        f.write(f"{key}: {value}\n")
                logger.info(f"Metadata saved to {metadata_path}")
            
            # Update latest version
            self._save_version(version)
            
            return model_path
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise

    def load_model(self, model_path=None, version=None):
        """
        Load model from disk
        
        Args:
            model_path: Full path to model file (takes precedence over version)
            version: Version number to load (default: latest)
            
        Returns:
            Loaded model or None if not found
        """
        try:
            if model_path and os.path.exists(model_path):
                model = joblib.load(model_path)
                logger.info(f"Model loaded from {model_path}")
                return model
            
            # Find latest model if no path provided
            latest_model = self._find_latest_model(version)
            if latest_model:
                model = joblib.load(latest_model)
                logger.info(f"Model loaded from {latest_model}")
                return model
            else:
                logger.warning("No trained model found")
                return None
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None

    def _get_next_version(self):
        """Get next version number"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, "r") as f:
                    version = int(f.read().strip()) + 1
            else:
                version = 1
            return version
        except Exception as e:
            logger.warning(f"Could not read version file: {e}")
            return 1

    def _save_version(self, version):
        """Save current version"""
        try:
            with open(self.version_file, "w") as f:
                f.write(str(version))
        except Exception as e:
            logger.warning(f"Could not save version file: {e}")

    def _find_latest_model(self, version=None):
        """Find latest model file"""
        if not os.path.exists(self.model_dir):
            return None
        
        models = [f for f in os.listdir(self.model_dir) if f.endswith(".joblib")]
        if not models:
            return None
        
        # Sort by filename (includes timestamp)
        models.sort(reverse=True)
        return os.path.join(self.model_dir, models[0])
