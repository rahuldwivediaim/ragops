from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).parent
DOCKER_DIR = PROJECT_ROOT / "infrastructure" / "docker"


def run_compose(*args):
    """Execute docker compose from the infrastructure/docker directory."""
    command = ["docker", "compose", *args]

    result = subprocess.run(
        command,
        cwd=DOCKER_DIR,
    )
    print(f"Working Directory : {DOCKER_DIR}")
    print(f"Command           : {' '.join(command)}")
    return result.returncode


def usage():
    print(
        """
Usage:

python rundocker.py start
python rundocker.py stop
python rundocker.py restart
python rundocker.py logs
python rundocker.py ps
python rundocker.py down
python rundocker.py build
"""
    )


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    commands = {
        "start": ["up", "-d"],
        "stop": ["stop"],
        "restart": ["restart"],
        "logs": ["logs", "-f"],
        "ps": ["ps"],
        "down": ["down"],
        "build": ["build"],
    }

    if cmd not in commands:
        usage()
        sys.exit(1)

    sys.exit(run_compose(*commands[cmd]))


if __name__ == "__main__":
    main()
