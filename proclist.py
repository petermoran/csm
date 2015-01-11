import psutil

proc_attrs = ["name","pid","get_cpu_percent","get_memory_percent","username"]

def get_processes():
    return {p.pid:p.as_dict(proc_attrs) for p in psutil.process_iter()}


_prev_cpu = {}
_prev_mem = {}

def get_top(process, prev_values, key, N=10, alpha=0.1):
    """
    """
    values = []

    for pid, proc in process.iteritems():
        this_val = proc[key]
        prev_val = _prev_cpu.get(pid, this_val)

        ema = alpha*this_val + (1 - alpha)*prev_val

        values.append((ema, pid))
        prev_values[pid] = ema

    values.sort()

    top = [process[c[1]] for c in values[:-N:-1]]

    return top


proc_cache = get_processes()
top_cpu = get_top(proc_cache, _prev_cpu, 'cpu_percent')
top_mem = get_top(proc_cache, _prev_mem, 'memory_percent')


user_len = max(len(p['username']) for p in top_cpu)


hdr_fmt = " %7s %" + str(user_len) + "s %5s %5s %4s"
row_fmt = (
    " %(pid)7d" +
    " %(username)" + str(user_len) + "s" +
    " %(cpu_percent)5.1f" +
    " %(memory_percent)5.1f" +
    " %(name)s")


print hdr_fmt % ("pid", "user", "cpu", "mem", "name")
for p in top_cpu:
    print row_fmt % p

