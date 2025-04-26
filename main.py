from os import system as os_system
import colorama

num_key = [x for x in range(10)]

cout = lambda *printed: print(*printed, end="", sep="")


def make_getch():
    from os import name
    if name == "nt":
        from msvcrt import getch

        def win_get():
            return getch().decode()

        return win_get
    else:
        import termios
        from tty import setraw
        from sys import stdin

        def unix_get():
            fd = stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                setraw(stdin.fileno())
                ch = stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return unix_get


getch = make_getch()


def print_all(All, Line):
    cout("-" * (Line * 2 + 2))
    for i in All:

        pass
    pass


def run(Line=10, All=None):
    if not All:
        All = [["?"] * Line] * Line
