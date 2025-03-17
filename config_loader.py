import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def get_pdf_processing_config(self) -> Dict[str, Any]:
        """Get PDF processing configuration."""
        return self.config.get('pdf_processing', {})

    def get_metadata_config(self) -> Dict[str, Any]:
        """Get metadata extraction configuration."""
        return self.config.get('metadata', {})

    def get_paths_config(self) -> Dict[str, Any]:
        """Get file paths configuration."""
        return self.config.get('paths', {})

    def get_collection_config(self) -> Dict[str, Any]:
        """Get collection configuration."""
        return self.config.get('collection', {})

    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing settings configuration."""
        return self.config.get('processing', {})

    def get_quality_config(self) -> Dict[str, Any]:
        """Get quality check configuration."""
        return self.config.get('quality', {})

    def get_path(self, key: str) -> Path:
        """Get a path from the configuration."""
        paths = self.get_paths_config()
        return Path(paths.get(key, ""))

    def validate_config(self) -> bool:
        """Validate the configuration."""
        required_sections = ['pdf_processing', 'paths', 'collection']
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required configuration section: {section}")
                return False
        return True
