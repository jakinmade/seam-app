"""
SEAM Rules Loader
Loads versioned YAML rule files. Engine reads from this — never hardcodes thresholds.

Usage:
    from engine.rules_loader import load_rules, get_active_rules
    rules = get_active_rules()          # loads SEAM-R-v1.0 (current)
    rules = load_rules("SEAM-R-v1.0")  # explicit version
"""

import os
import yaml
from functools import lru_cache

RULES_DIR = os.path.join(os.path.dirname(__file__), "rules")
ACTIVE_VERSION = "SEAM-R-v1.0"


@lru_cache(maxsize=10)
def load_rules(version: str = ACTIVE_VERSION) -> dict:
    """Load a specific rules version from YAML. Cached after first load."""
    path = os.path.join(RULES_DIR, f"{version}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Rules version {version} not found at {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def get_active_rules() -> dict:
    """Return the currently active rules version."""
    return load_rules(ACTIVE_VERSION)


def list_available_versions() -> list[str]:
    """Return all available rule versions."""
    return [
        f.replace(".yaml", "")
        for f in os.listdir(RULES_DIR)
        if f.endswith(".yaml")
    ]
