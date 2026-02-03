"""Servo-based hardware display for Braille output.

Controls 6 servo motors via GPIO pins to raise/lower tactile pins.
"""

from typing import List
import config
from .base import Display


class ServoDisplay(Display):
    """
    Hardware display using servo motors for tactile Braille output.

    Controls 6 servos via GPIO pins to raise/lower tactile pins.

    Example:
        >>> display = ServoDisplay()
        >>> display.set_pattern([1, 0, 0, 0, 0, 0])  # Raise dot 1
        >>> display.reset()  # Lower all dots
        >>> display.cleanup()  # Release GPIO
    """

    def __init__(self):
        self.servos = {}
        self._initialized = False
        self._initialize()

    def _initialize(self):
        """Initialize servo motors on GPIO pins."""
        try:
            from gpiozero import AngularServo

            for dot_num, pin in config.SERVO_PINS.items():
                self.servos[dot_num] = AngularServo(pin, min_angle=-90, max_angle=90)

            self._initialized = True

            if config.VERBOSE_MODE:
                print(f"[VERBOSE] Initialized {len(self.servos)} servos")

        except ImportError:
            print("Warning: gpiozero not available. Servo display disabled.")
            print("Install with: sudo apt install python3-gpiozero")

        except Exception as e:
            print(f"Error initializing servos: {e}")
            print("Hardware display disabled.")

    def set_pattern(self, pattern: List[int]) -> None:
        """
        Raise/lower servos to match the Braille pattern.

        Args:
            pattern: 6-element list (0=lowered, 1=raised)
        """
        if not self._initialized:
            return

        for dot_num, is_raised in enumerate(pattern, start=1):
            if dot_num in self.servos:
                angle = (
                    config.SERVO_ANGLES["RAISED"]
                    if is_raised
                    else config.SERVO_ANGLES["LOWERED"]
                )
                self.servos[dot_num].angle = angle

                if config.VERBOSE_MODE:
                    state = "raised" if is_raised else "lowered"
                    print(f"[VERBOSE] Dot {dot_num}: {state} ({angle}°)")

    def reset(self) -> None:
        """Lower all servos to default position."""
        if not self._initialized:
            return

        for dot_num, servo in self.servos.items():
            servo.angle = config.SERVO_ANGLES["LOWERED"]

        if config.VERBOSE_MODE:
            print("[VERBOSE] All servos reset to lowered position")

    def cleanup(self) -> None:
        """Release GPIO resources."""
        if not self._initialized:
            return

        try:
            from gpiozero import Device

            Device.pin_factory.close()
        except:
            pass
