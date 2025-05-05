"""
MAIA Hierarchical Multi-Agent System Agents Package

This package contains the specialized agents organized into their respective layers:
1. Area Layer - High-level destination selection
2. City Layer - City selection & duration, intercity transit
3. Within-City Layer - Activities, accommodation, dining, local transit
4. Verification Layer - Constraint verification
"""

from .area_layer import AreaLayerAgents

__all__ = ['AreaLayerAgents']