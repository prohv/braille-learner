"""Display base class for Braille output.

The display layer is responsible for visual/tactile output only.
Timing and state management are handled by the application layer.
"""

from abc import ABC, abstractmethod
from typing import List


class Display(ABC):
    """
    Abstract base class for Braille display implementations.

    Implementations must provide set_pattern() and reset() methods.
    The display layer is stateless - timing and sequencing are handled
    by the application controller.

    Example:
        >>> display = ServoDisplay()  # or SimulationDisplay()
        >>> display.set_pattern([1, 0, 0, 0, 0, 0])  # Show 'A'
        >>> # ... wait for DISPLAY_DURATION seconds ...
        >>> display.reset()  # Clear display
    """

    @abstractmethod
    def set_pattern(self, pattern: List[int]) -> None:
        """
        Set the display to show a Braille pattern.

        Args:
            pattern: List of 6 integers (0 or 1), representing dots 1-6:
                    1 o o 4
                    2 o o 5
                    3 o o 6

        This method should be non-blocking and return immediately.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset display to default state (all dots lowered/cleared).

        This method should be non-blocking and return immediately.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources (GPIO, etc.) on shutdown.

        Called once when the application exits.
        """
        pass
