import asyncio
import sys
from pathlib import Path

replay_file= (Path(__file__).parent / 'replay_log.py')
print(replay_file)

async def launch_rafal_API_batch():
    # Create the subprocess; redirect the standard output
    # into a pipe.
    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(replay_file),
        stdout=asyncio.subprocess.PIPE)

    # Read one line of output.
    data = await proc.stdout.readline()
    line = data.decode('ascii').rstrip()

    # Wait for the subprocess exit.
    await proc.wait()
    return line

if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy())
        
result = asyncio.run(launch_rafal_API_batch())
print(result)
