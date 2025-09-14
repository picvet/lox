from pathlib import Path

from setuptools import find_packages, setup


def read_requirement():
    """Read requirements from requirements.txt file."""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        return []

    requirements = []
    with req_file.open("r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith(("#", "-e")):
                requirements.append(line)
    return requirements


setup(
    name="lox-password-manager",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=read_requirement(),
    entry_points={
        "console_scripts": [
            "lox=main:main",
        ],
    },
    python_requires=">=3.8",
)
