import subprocess
import sys
import time


# class FlushFile(object):
#     """Write-only flushing wrapper for file-type objects."""
#
#     def __init__(self, f):
#         self.f = f
#
#     def write(self, x):
#         self.f.write(x)
#         self.f.flush()


def run_sat_basic(obfuscated, original, verbose=False):
    success_flag = False
    # sys.stdout = FlushFile(sys.__stdout__)
    popen = subprocess.Popen(['./src/sld', '-N 2', obfuscated, original], stdout=subprocess.PIPE)
    start = time.time()
    correct_key = []
    key_count = 0
    dip_list = []
    odip_list = []
    while True:
        next_line = popen.stdout.readline().decode("utf-8")
        if next_line == '' and popen.poll() is not None:
            break
        if verbose:
            sys.stdout.write(next_line)
        if 'inputs' in next_line:
            start = time.time()
        if 'iteration:' in next_line:
            end = time.time()
            to_file = open(obfuscated[: obfuscated.index('.')] + 'Runtime.txt', 'w')
            to_file.write('%f, %s' % (end - start, next_line))
            to_file.close()
            start = end
        if 'fail_count' in next_line:
            if 'fail_count = 0' in next_line:
                success_flag = True
        if 'key=' in next_line:
            correct_key.append(next_line[next_line.index('=') + 1:].rstrip())
            key_count += 1
            # print(correct_key)
        if 'DIP=<' in next_line:
            dip_list.append(next_line[next_line.index('<') + 1: next_line.index('>')])
            next_line = next_line[next_line.index('>') + 1:]
            odip_list.append(next_line[next_line.index('<') + 1: next_line.index('>')])

    if key_count <= 1:
        unique_key_flag = True
    else:
        unique_key_flag = False
    # print(dip_list)
    # print(odip_list)
    return success_flag, unique_key_flag, correct_key, dip_list, odip_list


if __name__ == '__main__':
    obfuscated = sys.argv[1]
    original = sys.argv[2]
    run_sat_basic(obfuscated, original)
