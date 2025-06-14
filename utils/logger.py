# logger.py

"""
Production-grade logger utility for the AI Stock Picker project.
- Loads configuration from YAML using Hydra.
- Provides a get_logger() function for all modules.
- Ensures log rotation, formatting, and error resilience.
"""
import logging
from logging.config import dictConfig
import hydra
from omegaconf import OmegaConf
import os

LOGGING_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/logging.yaml')

def setup_logger(name: str = None):
    """
    Set up logger from YAML config (uses Hydra/omegaconf).
    Args:
        name (str): Optional logger name for submodule logging.
    Returns:
        logging.Logger: Configured logger instance.
    """
    import yaml
    with open(LOGGING_CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    dictConfig(config)
    return logging.getLogger(name)

# Example usage in other modules:
# from utils.logger import setup_logger
# logger = setup_logger(__name__)
# logger.info('Logger initialized successfully!')
