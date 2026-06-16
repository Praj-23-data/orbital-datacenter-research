"""Ensure the repository root is importable during tests.

This lets `import simulations` and `import models` work whether or not the
package has been installed with `pip install -e .`.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
