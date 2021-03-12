import datetime
import os


def write_log(lines):
    """
    Appends the given list of lines to the log file.

    :param lines list(str):
    """
    now = datetime.datetime.now()

    path = os.path.expanduser('~/.local/share/vigilant-crypto-snatch/log.txt')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as f:
        f.write(now.isoformat() + '\n')
        for line in lines:
            f.write('  ' + line.strip() + '\n')
            print(line)