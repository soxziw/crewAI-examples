#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="trip_planner",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8,<3.13",
    install_requires=[
        "crewai",
        "google-search-results>=2.4.2",
    ],
)