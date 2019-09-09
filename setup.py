from setuptools import setup

setup(
    name="jeweler",
    version='0.0',
    packages=['jeweler', 'jeweler.catalog'],
    install_requires=[
        'click',
        'numpy',
        'tqdm',
    ],
    python_requires='>=3.6',
    entry_points='''
        [console_scripts]
        jeweler=jeweler.cli:cli
    ''',
    package_data={'': ['*.json']},
)
