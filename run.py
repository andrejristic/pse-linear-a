#!/usr/bin/env python3
"""Dev launcher for PSE Linear A."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pse_linear_a.gui.app import main
raise SystemExit(main())
