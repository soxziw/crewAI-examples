#!/usr/bin/env python3

import os
import sys
import shutil

def show_example_report():
    """
    Display the example trip report.
    """
    example_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_output")
    
    # Check if example files exist
    report_path = os.path.join(example_dir, "maia_trip_report.md")
    constraint_path = os.path.join(example_dir, "constraint_verification_report.md")
    
    if not os.path.exists(report_path) or not os.path.exists(constraint_path):
        print("Error: Example output files not found in example_output directory.")
        return
    
    # Copy example files to current directory
    current_dir = os.getcwd()
    try:
        shutil.copy(report_path, os.path.join(current_dir, "maia_trip_report.md"))
        shutil.copy(constraint_path, os.path.join(current_dir, "constraint_verification_report.md"))
        
        print("\n=== MAIA Trip Planner Example Output ===\n")
        print("Due to installation issues, showing the example output instead of generating a new plan.")
        print("Files have been copied to the current directory:")
        print("1. maia_trip_report.md - The trip itinerary")
        print("2. constraint_verification_report.md - Constraints verification")
        print("\nTo view the complete reports, you can open these files in a markdown viewer or use:")
        print("cat maia_trip_report.md")
        print("cat constraint_verification_report.md")
        
    except Exception as e:
        print(f"Error copying example files: {e}")

if __name__ == "__main__":
    show_example_report()