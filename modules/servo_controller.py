import time
import config


class ServoController:
    def __init__(self, simulation_mode=None):
        self.simulation_mode = (
            simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        )
        self.servos = {}
        self._initialize()

    def _initialize(self):
        if not self.simulation_mode:
            try:
                from gpiozero import AngularServo

                for dot_num, pin in config.SERVO_PINS.items():
                    self.servos[dot_num] = AngularServo(
                        pin, min_angle=-90, max_angle=90
                    )
                if config.VERBOSE_MODE:
                    print(
                        "[VERBOSE] Initialized 6 servos on pins:",
                        list(config.SERVO_PINS.values()),
                    )
            except ImportError:
                print("gpiozero not available, switching to simulation mode")
                self.simulation_mode = True
            except Exception as e:
                print(f"Failed to initialize GPIO: {e}")
                print("Switching to simulation mode")
                self.simulation_mode = True

        if self.simulation_mode and config.VERBOSE_MODE:
            print("[VERBOSE] Running in simulation mode")

    def display_braille(self, pattern, char):
        dots_raised = []

        for dot_num, is_raised in enumerate(pattern, start=1):
            if is_raised:
                dots_raised.append(dot_num)
                self._raise_dot(dot_num)
            else:
                self._lower_dot(dot_num)

        if config.VERBOSE_MODE:
            print(f"[VERBOSE] Character: {char.upper()}")
            print(f"[VERBOSE] Dots raised: {dots_raised}")

        time.sleep(config.DISPLAY_DURATION)
        self.reset_all()

    def _raise_dot(self, dot_num):
        if not self.simulation_mode and dot_num in self.servos:
            angle = config.SERVO_ANGLES["RAISED"]
            self.servos[dot_num].angle = angle
            if config.VERBOSE_MODE:
                pin = config.SERVO_PINS[dot_num]
                print(
                    f"[VERBOSE] Raising servo on pin {pin} (dot {dot_num}) to angle {angle}°"
                )
        elif config.VERBOSE_MODE:
            angle = config.SERVO_ANGLES["RAISED"]
            pin = config.SERVO_PINS[dot_num]
            print(
                f"[VERBOSE] Would raise servo on pin {pin} (dot {dot_num}) to angle {angle}°"
            )

    def _lower_dot(self, dot_num):
        if not self.simulation_mode and dot_num in self.servos:
            angle = config.SERVO_ANGLES["LOWERED"]
            self.servos[dot_num].angle = angle
            if config.VERBOSE_MODE:
                pin = config.SERVO_PINS[dot_num]
                print(
                    f"[VERBOSE] Lowering servo on pin {pin} (dot {dot_num}) to angle {angle}°"
                )
        elif config.VERBOSE_MODE:
            angle = config.SERVO_ANGLES["LOWERED"]
            pin = config.SERVO_PINS[dot_num]
            print(
                f"[VERBOSE] Would lower servo on pin {pin} (dot {dot_num}) to angle {angle}°"
            )

    def reset_all(self):
        for dot_num in range(1, 7):
            self._lower_dot(dot_num)

    def cleanup(self):
        if not self.simulation_mode:
            try:
                from gpiozero import Device

                Device.pin_factory.close()
            except:
                pass
