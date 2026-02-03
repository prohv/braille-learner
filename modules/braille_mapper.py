import config


class BrailleMapper:
    @staticmethod
    def get_braille_pattern(char):
        char = char.lower()
        return config.BRAILLE_MAP.get(char, None)

    @staticmethod
    def get_unicode_braille(char):
        char = char.lower()
        return config.UNICODE_BRAILLE.get(char, None)

    @staticmethod
    def is_valid_character(char):
        return len(char) == 1 and char.isalpha()

    @staticmethod
    def format_braille_pattern(pattern):
        return "".join(["1" if p else "0" for p in pattern])

    @staticmethod
    def display_braille_grid(pattern):
        dot_1, dot_2, dot_3, dot_4, dot_5, dot_6 = pattern

        left_top = "●" if dot_1 else "○"
        right_top = "●" if dot_4 else "○"
        left_mid = "●" if dot_2 else "○"
        right_mid = "●" if dot_5 else "○"
        left_bottom = "●" if dot_3 else "○"
        right_bottom = "●" if dot_6 else "○"

        grid = f"{left_top} {right_top}\n{left_mid} {right_mid}\n{left_bottom} {right_bottom}"
        return grid

    @staticmethod
    def get_dots_raised(pattern):
        return [i + 1 for i, dot in enumerate(pattern) if dot == 1]
