import curses

class Screen:
    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)

        self.curses = curses
        self.curses.start_color()
        self.curses.noecho()
        self.curses.cbreak()

    def __del__(self):
        self.stdscr.keypad(0)

        self.curses.nocbreak()
        self.curses.echo()
        self.curses.endwin()


if __name__ == "__main__":
    import time


    screen = Screen()

    for i in xrange(curses.COLORS):
        curses.init_pair(i + 1, curses.COLOR_WHITE, curses.COLOR_GREEN)

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)



    for i in xrange(curses.COLORS):
        screen.stdscr.clear()

        msg = "Text: %s %s" % (i, curses.COLOR_BLACK)
        screen.stdscr.addstr(i, 0, msg, curses.color_pair(i + 1))

        screen.stdscr.addch(curses.ACS_CKBOARD, curses.color_pair(1))
        screen.stdscr.addstr('A', curses.color_pair(2))

        screen.stdscr.refresh()
        time.sleep(0.5)

