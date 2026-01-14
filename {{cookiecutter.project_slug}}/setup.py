from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="{{cookiecutter.project_name}}",
    version="{{cookiecutter.version}}",
    author="{{cookiecutter.author_name}}",
    description="{{cookiecutter.description}}",
    packages=find_packages(exclude=["dist", "build", "*.egg-info", "tests"]),
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["requests", "prettytable"],
    entry_points={
        "console_scripts": [
            "{{cookiecutter.command_name}} = {{cookiecutter.project_slug}}.shell:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
)
