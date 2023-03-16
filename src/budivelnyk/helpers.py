import subprocess
from warnings import warn


def run_and_maybe_fail(*command_with_args: str) -> None:
    process = subprocess.run(command_with_args, capture_output=True)
    stdout = process.stdout.decode(errors='replace')
    stderr = process.stderr.decode(errors='replace')
    if stdout:
        print(stdout)
    if stderr:
        if process.returncode == 0:
            warn(stderr, RuntimeWarning)
        else:
            raise RuntimeError(stderr)
