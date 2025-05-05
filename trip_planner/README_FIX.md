# Trip Planner Fix

## Summary of Fixes

This document explains the fixes applied to make the trip planner work:

1. **Created a setup.py file** for pip installation
2. **Fixed import paths** throughout the codebase to handle both direct execution and installed package scenarios
3. **Implemented mock tools** for missing dependencies
   - Created mock implementations for crewai.tools.BaseTool 
   - Created mock implementations for SerperDevTool and ScrapeWebsiteTool
4. **Added path flexibility** with try/except imports to support multiple import styles
5. **Fixed f-string syntax** in the maia_orchestrator.py file to avoid leading zeros in decimal integers
6. **Implemented pydantic import flexibility** for different versions of the library

## Requirements

To run the trip planner:
1. Install crewai package: `pip install crewai`
2. Set the OPENAI_API_KEY environment variable: `export OPENAI_API_KEY=your-api-key`
3. Run the planner: `python3 simple_planner.py`

## Additional Notes

- The planner is now compatible with Python 3.8+
- Mock implementations provide placeholders for the missing crewai-tools package
- The simple_planner.py script provides a non-interactive version for easier testing