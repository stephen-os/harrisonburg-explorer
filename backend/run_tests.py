#!/usr/bin/env python3
"""
Test runner script for the TSP Route Optimizer backend.
Run this script to execute all tests.
"""

import pytest
import sys
import os

def main():
    """Run all tests"""
    
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Test arguments
    test_args = [
        "tests/",                    # Test directory
        "-v",                        # Verbose output
        "--tb=short",               # Short traceback format
        "--strict-markers",         # Strict marker checking
        "--disable-warnings",       # Disable warnings
        "--color=yes",              # Colored output
    ]
    
    # Add coverage if available
    try:
        import coverage
        test_args.extend([
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
        ])
        print("Running tests with coverage...")
    except ImportError:
        print("Running tests without coverage (install pytest-cov for coverage)")
    
    # Run tests
    exit_code = pytest.main(test_args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())