#!/usr/bin/env python3
"""
Script to run PEP 8 compliance checks using flake8.
"""

import subprocess
import sys
from pathlib import Path


def run_flake8():
    """Run flake8 on the project."""
    try:
        # Run flake8 with the configuration from .flake8
        result = subprocess.run(
            ["flake8", "."],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print("✅ PEP 8 compliance check passed!")
            print("No style violations found.")
            return True
        else:
            print("❌ PEP 8 compliance check failed!")
            print("Style violations found:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            return False

    except FileNotFoundError:
        print("❌ Error: flake8 not found. Please install it with:")
        print("   pip install flake8")
        return False
    except Exception as e:
        print(f"❌ Error running flake8: {e}")
        return False


if __name__ == "__main__":
    success = run_flake8()
    sys.exit(0 if success else 1)
