import curses
import psutil
import numpy as np
import time



def getbar(barlen, char='|', maxlen=20):
    barlen -= 50./maxlen

    bar = ''
    while barlen > 0:
        bar += char
        barlen -= 100./maxlen

    return bar


def emalist(new, old, alpha):
    out = [alpha*n + (1 - alpha)*o for n, o in zip(new, old)]
    return out


if __name__ == "__main__":


    stdscr = curses.initscr()
    stdscr.keypad(1)

    curses.start_color()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    if True:
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    else:
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)


    # CPU
    stdscr.addstr(1, 1, "CPU")
    stdscr.refresh()


    usage = psutil.cpu_percent(percpu=True)
    nproc = len(usage)

    barwidth = 50
    width = barwidth + 7
    height = nproc

    win = curses.newwin(height, width, 1, 4)


    alpha = 0.15


    try:
        while True:

            for _ in xrange(10):
                usage = emalist(
                        psutil.cpu_percent(percpu=True),
                        usage,
                        alpha)
                time.sleep(0.1)

            win.erase()
            #win.border()

            for ip in xrange(nproc):
                bar = getbar(usage[ip], char='|', maxlen=barwidth)

                win.addstr(ip, 1, '%5.1f ' % usage[ip])

                icol = 1 + min(int(usage[ip]/25.0), 3)
                win.addstr(bar, curses.color_pair(icol))

            win.refresh()

    except KeyboardInterrupt:
        pass

    stdscr.keypad(0)

    curses.nocbreak()
    curses.echo()
    curses.endwin()
