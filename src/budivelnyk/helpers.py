import subprocess
from warnings import warn


def run_and_maybe_fail(*command_with_args: str) -> None:
    process = subprocess.run(command_with_args, capture_output=True)
    stdout = process.stdout.decode(errors='replace')
    stderr = process.stderr.decode(errors='replace')
    if stdout:
        print(stdout)

    if process.returncode == 0:  # no error
        if stderr:
            warn(stderr, RuntimeWarning)
    else:
        if stderr:
            raise RuntimeError(stderr)
        else:
            raise RuntimeError(f"return code: {process.returncode}")
