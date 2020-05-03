import sys
import subprocess

def exec_process(cmdline, silent, input=None, **kwargs):
    """Execute a subprocess and returns the returncode, stdout buffer and stderr buffer.
       Optionally prints stdout and stderr while running."""
    try:
        sub = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        stdout, stderr = sub.communicate(input=input)
        returncode = sub.returncode
        if not silent:
            sys.stdout.write(stdout)
            sys.stderr.write(stderr)
    except OSError as e:
        if e.errno == 2:
            raise RuntimeError('"%s" is not present on this system' % cmdline[0])
        else:
            raise
    if returncode != 0:
        raise RuntimeError('Got return value %d while executing "%s", stderr output was:\n%s' % (returncode, " ".join(cmdline), stderr.rstrip("\n")))
    return stdout


def get_dmesg():
   return exec_process(['dmesg'], True).decode('utf_8').split('\n')


def get_syslog():
    with open('/var/log/syslog') as f:
        syslog = [line.strip() for line in f.readlines()]

    try:
        with open('/var/log/syslog.1') as f:
            syslog += [line.strip() for line in f.readlines()]
    except:
        pass

    return syslog
