"""Controller layer for threshold configuration."""
from domain.thresholds import load_thresholds

def get_thresholds():
    return load_thresholds()
