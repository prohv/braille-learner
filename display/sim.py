"""Simulation display for testing without hardware.

Prints Braille patterns to console instead of controlling servos.
"""

from typing import List
from .base import Display


class SimulationDisplay(Display):
    """
    Simulation display for testing without hardware.

    Prints Braille patterns to console instead of controlling servos.
    """

    def __init__(self):
        self._initialized = True

    def set_pattern(self, pattern: List[int]) -> None:
        """
        Print the Braille pattern to console.

        Args:
            pattern: 6-element list (0=lowered, 1=raised)
        """
        from braille.render import render_ascii_grid

        grid = render_ascii_grid(pattern)

        print("\n[DISPLAY] Braille pattern set:")
        print(grid)

    def reset(self) -> None:
        """Print reset message."""
        print("\n[DISPLAY] Reset (all dots lowered)")

    def cleanup(self) -> None:
        """No cleanup needed for simulation."""
        pass
