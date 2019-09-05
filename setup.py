from setuptools import setup

setup(
    name="jeweler",
    version='0.0',
    packages=['jeweler'],
    install_requires=[
        'click',
        'numpy',
        'tqdm',
    ],
    entry_points='''
        [console_scripts]
        jeweler=jeweler.cli:cli
    ''',
)
