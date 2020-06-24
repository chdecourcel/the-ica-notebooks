from pathlib import Path
from subprocess import Popen, PIPE
import time

replay_file= (Path(__file__).parent / 'replay_log.py')
print(replay_file)

running_procs = [
    Popen(['cmd', '/C', 'python', str(replay_file)], stdout=PIPE, stderr=PIPE)
                for i in range(2)
        ]

while running_procs:
    for proc in running_procs:
        retcode = proc.poll()
        if retcode is not None: # Process finished.
            running_procs.remove(proc)
            break
        else: # No process is done, wait a bit and check again.
            time.sleep(.1)
            continue

        # Here, `proc` has finished with return code `retcode`
        if retcode != 0:
            """Error handling."""
            raise SystemError(proc.stdout)



# for i in range(2):
#     print(f'itération {i}')
#     subprocess.run(args= ['cmd', '/C', 'python', str(replay_file)], check= True)
