#!/usr/bin/env python3
"""
Test runner wrapper - launches tests from the scripts directory
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the main test runner
from scripts.run_tests import main

if __name__ == "__main__":
    main()