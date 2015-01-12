import curses
import psutil
import numpy as np
import time


class CursesManager:
    def __init__(self):
        self.scr = curses.initscr()
        self.scr.keypad(1)

        self.curses = curses

        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    def __del__(self):
        self.scr.keypad(0)

        self.curses.nocbreak()
        self.curses.echo()
        self.curses.endwin()


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


def get_top(process, prev_values, key, N=6, alpha=0.5):
    """
    """
    values = []

    for pid, proc in process.iteritems():
        this_val = proc[key]
        prev_val = prev_values.get(pid, this_val)

        ema = alpha*this_val + (1 - alpha)*prev_val

        values.append((ema, pid))
        prev_values[pid] = ema

    values.sort()

    top = [process[c[1]] for c in values[:-N:-1]]
    for p in top:
        p[key] = prev_values[p['pid']]

    return top


class SystemStats:
    def __init__(self):
        self.cpu = psutil.cpu_percent(percpu=True)
        self.nproc = len(self.cpu)
        self.attrs = ["name","pid","get_cpu_percent","get_memory_percent","username"]
        self.refresh()

    def refresh(self):
        alpha = 0.4
        niter = 2

        for _ in xrange(niter):
            self.cpu = emalist(
                    psutil.cpu_percent(interval=0.1, percpu=True), self.cpu, alpha)

        self.mem = psutil.virtual_memory()
        self.proc = {
                p.pid:p.as_dict(self.attrs) for p in psutil.process_iter()}

class InfoBox:
    def __init__(self, y, x, height, width, scr, name):
        scr.addstr(y, x, name, curses.color_pair(3))
        scr.refresh()

        xwin = x + len(name) + 1

        if not hasattr(height, '__iter__'):
            width = width - len(name) - 1
            self.win = curses.newwin(height, width, y, xwin)
            self.height = height

        else:
            ywin = y
            self.win = []
            for h in height:
                self.win.append(curses.newwin(h, width, ywin, xwin))
                ywin += h + 1
                xwin = x

            self.height = ywin - 2


class CpuInfoBox(InfoBox):
    def __init__(self, y, x, width, scr, stats):
        InfoBox.__init__(self, y, x, [1, stats.nproc, 6], width, scr, "CPU")
        self.barwidth = 50
        self.stats = stats
        self.prev_proc = {}

        win = self.win[0]
        win.addstr(0, 1, "ncores: %d" % stats.nproc)
        win.refresh()

        self.refresh()

    def refresh(self):
        self._refresh_bars()
        self._refresh_proc()

    def _refresh_bars(self):
        win = self.win[1]
        win.erase()

        usage = self.stats.cpu

        for ip in xrange(len(usage)):
            bar = getbar(usage[ip], char='|', maxlen=self.barwidth)

            win.addstr(ip, 1, '%5.1f ' % usage[ip])

            icol = 1 + min(int(usage[ip]/25.), 3)
            win.addstr(bar, curses.color_pair(icol))

        win.refresh()

    def _refresh_proc(self):
        top = get_top(self.stats.proc, self.prev_proc, 'cpu_percent')

        #user_len = max(len(p['username']) for p in top)
        user_len = 8

        hdr_fmt = "%7s %" + str(user_len) + "s %5s %5s  %4s"
        row_fmt = (
            "%(pid)7d " +
            "%(username)" + str(user_len) + "s " +
            "%(cpu_percent)5.1f " +
            "%(memory_percent)5.1f " +
            " %(name)s")

        win = self.win[2]
        win.erase()

        win.addstr(0, 1, hdr_fmt % ("pid", "user", "cpu", "mem", "name"))

        for ip, p in enumerate(top):
            p['username'] = p['username'][:8]
            win.addstr(ip+1, 1, row_fmt % p)

        win.refresh()


class MemInfoBox(InfoBox):
    def __init__(self, y, x, width, scr, stats):
        InfoBox.__init__(self, y, x, [1, 1, 6], width, scr, "MEM")
        self.barwidth = 50
        self.stats = stats
        self._prev_usage = -1
        self.prev_proc = {}

        self.refresh()

    def refresh(self):
        usage = int(self.stats.mem.percent)
        if usage == self._prev_usage:
            return

        self._refresh_text()
        self._refresh_bar()
        self._refresh_proc()

        self._prev_usage = usage

    def _refresh_text(self):
        win = self.win[0]
        win.erase()

        used = (stats.mem.total - stats.mem.available)/1073741824.
        total = stats.mem.total/1073741824.

        win.addstr(0, 1, "used: %.2f / %.2f G" % (used, total))
        win.refresh()

    def _refresh_bar(self):
        win = self.win[1]
        win.erase()

        usage = self.stats.mem.percent

        bar = getbar(usage, maxlen=self.barwidth)

        win.addstr(0, 1, '%5.1f ' % usage)

        icol = 1 + min(int(usage/25.), 3)
        attr = curses.color_pair(icol)

        if usage > 90:
            attr |= curses.A_BLINK

        win.addstr(bar, attr)
        win.refresh()

    def _refresh_proc(self):
        top = get_top(self.stats.proc, self.prev_proc, 'memory_percent')

        #user_len = max(len(p['username']) for p in top)
        user_len = 8

        hdr_fmt = "%7s %" + str(user_len) + "s %5s %5s  %4s"
        row_fmt = (
            "%(pid)7d " +
            "%(username)" + str(user_len) + "s " +
            "%(cpu_percent)5.1f " +
            "%(memory_percent)5.1f " +
            " %(name)s")

        row_fmt = (
                "%(pid)7d " +
                "%(username)" + str(user_len) + "s " +
                "%(cpu_percent)5.1f " +
                "%(memory_percent)5.1f " +
                " %(name)s")

        win = self.win[2]
        win.erase()

        win.addstr(0, 1, hdr_fmt % ("pid", "user", "cpu", "mem", "name"))

        for ip, p in enumerate(top):
            p['username'] = p['username'][:user_len]
            win.addstr(ip+1, 1, row_fmt % p)
            #win.addstr(ip+1, 1, 'hi')

        win.refresh()

if __name__ == "__main__":


    manager = CursesManager()
    stats = SystemStats()

    width = 200
    y0 = x0 = 1

    cpu = CpuInfoBox(y0, x0, width, manager.scr, stats)

    y0 += 1 + cpu.height
    mem = MemInfoBox(y0, x0, width, manager.scr, stats)


    manager.scr.refresh()

    while True:
        stats.refresh()
        cpu.refresh()
        mem.refresh()

        time.sleep(1.0)
