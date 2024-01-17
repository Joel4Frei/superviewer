class Marker:
    def __init__(self):
        def rgb_to_ansi(r, g, b):
            return f'\033[38;2;{r};{g};{b}m'

        self.Colors = {
            'RESET': '\033[0m',
            'red': rgb_to_ansi(255, 0, 0),
            'orange': rgb_to_ansi(255, 165, 0),
            'gold': rgb_to_ansi(255, 215, 0),
            'yellow': rgb_to_ansi(255, 255, 0),
            'lime': rgb_to_ansi(50, 205, 50),
            'olive': rgb_to_ansi(128, 128, 0),
            'green': rgb_to_ansi(0, 255, 0),
            'turquoise_blue': rgb_to_ansi(0, 199, 140),
            'teal': rgb_to_ansi(0, 128, 128),
            'turquoise': rgb_to_ansi(64, 224, 208),
            'cyan': rgb_to_ansi(0, 255, 255),
            'blue': rgb_to_ansi(0, 0, 255),
            'navy': rgb_to_ansi(0, 0, 128),
            'indigo': rgb_to_ansi(75, 0, 130),
            'purple': rgb_to_ansi(128, 0, 128),
            'pink': rgb_to_ansi(255, 192, 203),
            'peach': rgb_to_ansi(255, 218, 185),
            'rosa': rgb_to_ansi(255, 102, 204),
            'brown': rgb_to_ansi(165, 42, 42),
            'maroon': rgb_to_ansi(128, 0, 0),
            'burgundy': rgb_to_ansi(128, 0, 32),
            'silver': rgb_to_ansi(192, 192, 192),
            'gray': rgb_to_ansi(128, 128, 128),
            'dark_gray': rgb_to_ansi(169, 169, 169),
            'charcoal': rgb_to_ansi(54, 69, 79),
            'beige': rgb_to_ansi(245, 245, 220),
            'white': rgb_to_ansi(255, 255, 255),
            'black': rgb_to_ansi(0, 0, 0),
        }


        self.checkpoints = 0
        self.signals = "Signal Mark"  # Placeholder for your signal text

    def help(self):
        print('Package information\n')
        print('2 Functions: \n',
              '------------ \n',
              'cp() = Checkpoint\n',
              '\t Prints a new number every execution, no color distinction\n\n',
              'sig("color") = Signal Mark\n',
              '\t different colors to distinguish different paths\n\n')

        print('All avaible colors\n',
              '-------------------\n')
        count = 0
        for color_name, color_code in self.Colors.items():
            if color_name != 'RESET':
                print(f"{color_code}{color_name}{self.Colors['RESET']}", end=" ")
                count += 1

                if count == 10:
                    print()  # Move to the next line after printing 10 colors
                    count = 0

    def cp(self):
        print(f"{self.Colors['cyan']}Checkpoint {self.checkpoints}{self.Colors['RESET']}")
        self.checkpoints += 1

    def sig(self, color):
        if color in self.Colors:
            color_code = self.Colors[color]
            print(f"{color_code}{self.signals}{self.Colors['RESET']}")
        else:
            print(f"Invalid color: {color}. Available colors are: {', '.join(self.Colors.keys())}")