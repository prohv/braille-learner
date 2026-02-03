import unittest
from unittest.mock import patch
from modules.servo_controller import ServoController


class TestServoController(unittest.TestCase):
    def setUp(self):
        self.controller = ServoController(simulation_mode=True)

    def test_initialization_simulation(self):
        self.assertTrue(self.controller.simulation_mode)
        self.assertEqual(self.controller.servos, {})

    def test_raise_dot_simulation(self):
        self.controller._raise_dot(1)
        self.assertTrue(self.controller.simulation_mode)

    def test_lower_dot_simulation(self):
        self.controller._lower_dot(1)
        self.assertTrue(self.controller.simulation_mode)

    def test_reset_all(self):
        pattern = [1, 1, 1, 1, 1, 1]
        self.controller.reset_all()
        self.assertTrue(self.controller.simulation_mode)

    def test_display_braille(self):
        pattern = [1, 0, 0, 0, 0, 0]
        with patch("modules.servo_controller.time.sleep"):
            self.controller.display_braille(pattern, "a")
        self.assertTrue(self.controller.simulation_mode)

    @patch("modules.servo_controller.config.SIMULATION_MODE", False)
    def test_cleanup(self):
        self.controller = ServoController()
        self.controller.cleanup()
