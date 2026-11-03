"""The runner's handle on a generated world: world.py running in a sandboxed process."""

import json
import os
import select
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

HOST = Path(__file__).with_name("host.py")

# A run covers the main prompt's time range: next_day() returns None after its last day.
# A world still returning dates after this many days is broken, not long.
MAX_DAYS = 3660

# macOS sandbox: no network, writes only inside the run folder.
PROFILE = """(version 1)
(allow default)
(deny network*)
(deny file-write*)
(allow file-write* (subpath "{run_dir}") (literal "/dev/null"))
"""


class WorldError(Exception):
    """world.py crashed, timed out or broke the interface. The message is its traceback."""


class World:
    def __init__(self, run_dir: Path, timeout: float = 60):
        run_dir = run_dir.resolve()
        self.timeout = timeout
        command = [sys.executable, "-I", "-B", str(HOST), str(run_dir / "world.py")]
        if shutil.which("sandbox-exec"):
            command = ["sandbox-exec", "-p", PROFILE.format(run_dir=run_dir), *command]
        self._stderr = (run_dir / "world_stderr.log").open("a")
        try:
            self._process = subprocess.Popen(
                command,
                cwd=run_dir,
                # No API keys or other secrets reach the generated code.
                env={"PATH": os.environ.get("PATH", "")},
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=self._stderr,
                text=True,
            )
        except BaseException:
            self._stderr.close()
            raise
        try:
            self._read()
        except BaseException:
            self.close()
            raise

    def call(self, op: str, *args: Any) -> Any:
        assert self._process.stdin
        try:
            self._process.stdin.write(
                json.dumps({"op": op, "args": list(args)}, default=str) + "\n"
            )
            self._process.stdin.flush()
        except BrokenPipeError as error:
            raise WorldError(f"world.py exited before {op}") from error
        return self._read(op)

    def close(self) -> None:
        if self._process.poll() is None:
            self._process.kill()
        self._process.wait()
        if self._process.stdin:
            self._process.stdin.close()
        if self._process.stdout:
            self._process.stdout.close()
        if not self._stderr.closed:
            self._stderr.close()

    def _read(self, op: str = "loading") -> Any:
        stdout = self._process.stdout
        assert stdout
        ready, _, _ = select.select([stdout], [], [], self.timeout)
        if not ready:
            self._process.kill()
            raise WorldError(f"world.py took more than {self.timeout:.0f}s on {op}")
        line = stdout.readline()
        if not line:
            raise WorldError(f"world.py exited during {op} (see world_stderr.log)")
        try:
            reply = json.loads(line)
        except json.JSONDecodeError as error:
            raise WorldError(f"world.py returned invalid JSON on {op}: {line[:200]!r}") from error
        if "error" in reply:
            raise WorldError(reply["error"])
        return reply["ok"]
