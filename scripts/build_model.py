"""Build the local model without relying on native-Windows stdin support."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="qwen3.5:9b")
    args = parser.parse_args()
    cli = shutil.which("ollama")
    if not cli:
        raise SystemExit("Ollama is not on PATH")
    subprocess.run([cli, "pull", args.base], check=True)
    source = Path("model/Modelfile").read_text()
    lines = source.splitlines()
    lines = [f"FROM {args.base}" if line.startswith("FROM ") else line for line in lines]
    with tempfile.TemporaryDirectory() as directory:
        definition = Path(directory) / "Modelfile"
        definition.write_text("\n".join(lines) + "\n")
        subprocess.run([cli, "create", "bikeshare-coder", "-f", str(definition)], check=True)
