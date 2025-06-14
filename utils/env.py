import os
from dotenv import load_dotenv

def load_environment():
    """Load variables from .env and set OS environment (idempotent)."""
    load_dotenv(override=True)
    # Optionally: Print confirmation for debug
    print("[ENV] Loaded .env variables.")