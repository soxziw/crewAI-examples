#!/usr/bin/env python3
"""
Simple runner script for the interactive trip planner.
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main module
try:
    from trip_planner.main import run
except ImportError:
    from src.trip_planner.main import run

if __name__ == "__main__":
    run()