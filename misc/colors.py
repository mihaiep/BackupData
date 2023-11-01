class Colors:
    END = "\033[0m"

    class COL:
        DEFAULT = "\033[39m"
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        GREY = "\033[37m"

        class BRIG:
            BLACK = "\033[90m"
            RED = "\033[91m"
            GREEN = "\033[92m"
            YELLOW = "\033[93m"
            BLUE = "\033[94m"
            MAGENTA = "\033[95m"
            CYAN = "\033[96m"
            GREY = "\033[97m"

        class PURE:
            BLACK = "\033[38;2;0;0;0m"
            RED = "\033[38;2;255;0;0m"
            GREEN = "\033[38;2;0;255;0m"
            BLUE = "\033[38;2;0;0;255m"
            WHITE = "\033[38;2;255;255;255m"

    # noinspection SpellCheckingInspection
    class ALT:
        BOLD = "\033[1m"
        BRIG = "\033[1m"
        FAINT = "\033[2m"
        ITAL = "\033[3m"
        UNDER = "\033[4m"
        RVRS = "\033[7m"
        CROSS = "\033[9m"
        FRAME = "\033[51m"
        ENCIR = "\033[52m"

    class BGD:
        DEFAULT = "\033[49m"
        BLACK = "\033[40m"
        RED = "\033[41m"
        GREEN = "\033[42m"
        YELLOW = "\033[43m"
        BLUE = "\033[44m"
        MAGENTA = "\033[45m"
        CYAN = "\033[46m"
        GREY = "\033[47m"

        class PURE:
            BLACK = "\033[48;2;0;0;0m"
            RED = "\033[48;2;255;0;0m"
            GREEN = "\033[48;2;0;255;0m"
            BLUE = "\033[48;2;0;0;255m"
            WHITE = "\033[48;2;255;255;255m"

        class BRIG:
            BLACK = "\033[100m"
            RED = "\033[101m"
            GREEN = "\033[102m"
            YELLOW = "\033[103m"
            BLUE = "\033[104m"
            MAGENTA = "\033[105m"
            CYAN = "\033[106m"
            GREY = "\033[107m"

    @staticmethod
    def custom(r, g, b) -> str:
        return f"\033[38;2;{r};{g};{b}m"
