"""Export runtime dependencies and generate a Git-backed Connect manifest."""

import json
import subprocess
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    subprocess.run(
        [
            "uv",
            "export",
            "--locked",
            "--no-dev",
            "--no-hashes",
            "--no-annotate",
            "--no-header",
            "--no-emit-project",
            "--output-file",
            "requirements.txt",
        ],
        cwd=root,
        check=True,
    )
    subprocess.run(
        [
            "rsconnect",
            "write-manifest",
            "streamlit",
            ".",
            "--entrypoint",
            "app.py",
            "--requirements-file",
            "requirements.txt",
            "--exclude",
            ".venv/**",
            "--exclude",
            ".git/**",
            "--exclude",
            "__pycache__/**",
            "--exclude",
            ".pytest_cache/**",
            "--exclude",
            ".ruff_cache/**",
            "--exclude",
            ".mypy_cache/**",
            "--exclude",
            ".rsconnect-python/**",
            "--overwrite",
        ],
        cwd=root,
        check=True,
    )

    # rsconnect-python 1.32.0 drops --package-installer for Streamlit manifests.
    # Use the documented pip-compatible schema and explicitly permit uv.
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    package_manager = manifest["python"]["package_manager"]
    package_manager["name"] = "pip"
    package_manager["allow_uv"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Created manifest.json with python.package_manager.allow_uv=true")


if __name__ == "__main__":
    main()
