"""Display abstraction layer for Braille output.

Provides unified interface for both hardware (servo) and simulation (console) displays.
"""

from .base import Display
from .servo import ServoDisplay
from .sim import SimulationDisplay

__all__ = ["Display", "ServoDisplay", "SimulationDisplay"]
