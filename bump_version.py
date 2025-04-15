import re
import sys

path = "flapkine/version.py"
level = sys.argv[1] if len(sys.argv) > 1 else "patch"

with open(path, "r+") as f:
    content = f.read()
    match = re.search(r'"(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        raise ValueError("Version not found.")
    major, minor, patch = map(int, match.groups())

    if level == "major":
        major += 1; minor = 0; patch = 0
    elif level == "minor":
        minor += 1; patch = 0
    else:
        patch += 1

    new_version = f'"{major}.{minor}.{patch}"'
    updated = re.sub(r'"(\d+)\.(\d+)\.(\d+)"', new_version, content)
    f.seek(0); f.write(updated); f.truncate()
    print(f"🔁 Bumped version to {new_version.strip('\"')}")
