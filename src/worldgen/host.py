"""Runs a generated world.py in its own process and answers the runner over stdin/stdout.

The runner starts this file inside a sandbox. One JSON request per line comes in,
{"op": name, "args": [...]}, and one JSON reply per line goes out, {"ok": value} or
{"error": traceback}. Anything the world prints goes to stderr.
"""

import importlib.util
import json
import sys
import traceback

OPS = ("start", "agents_today", "tools", "call_tool", "status", "next_day", "records")


def main() -> None:
    out = sys.stdout
    sys.stdout = sys.stderr

    def reply(message: dict[str, object]) -> None:
        out.write(json.dumps(message, default=str) + "\n")
        out.flush()

    try:
        spec = importlib.util.spec_from_file_location("world", sys.argv[1])
        assert spec and spec.loader
        world = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(world)
        missing = [op for op in OPS if not callable(getattr(world, op, None))]
        if missing:
            raise AttributeError("world.py does not define: " + ", ".join(missing))
    except BaseException:
        reply({"error": traceback.format_exc()})
        return
    reply({"ok": "loaded"})

    for line in sys.stdin:
        request = json.loads(line)
        try:
            if request["op"] not in OPS:
                raise ValueError(f"unknown op {request['op']}")
            value = getattr(world, request["op"])(*request["args"])
            text = json.dumps({"ok": value}, default=str)
        except BaseException:
            text = json.dumps({"error": traceback.format_exc()})
        out.write(text + "\n")
        out.flush()


if __name__ == "__main__":
    main()
