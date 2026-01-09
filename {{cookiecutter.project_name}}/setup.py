from setuptools import setup, find_packages

setup(
    name='{{cookiecutter.project_name}}',
    version='{{cookiecutter.version}}',
    description='{{cookiecutter.description}}',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            '{{cookiecutter.command_name}} = {{cookiecutter.package_name}}.shell:main',
        ],
    },
)
