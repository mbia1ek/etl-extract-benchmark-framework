import subprocess
from utils.timer import Timer
import os


def run_bcp_export(server, database, user, password, query, output_file):
    with Timer() as t:
        bcp_command = ['bcp', query, 'queryout', output_file, '-c', '-t,', '-S', server, '-d', database, '-U', user, '-P', password]
        subprocess.run(bcp_command, check=True)
    file_size = os.path.getsize(output_file)
    return t.elapsed, file_size
