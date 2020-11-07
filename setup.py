from skbuild import setup

setup(
    name="jeweler",
    version='0.0',
    packages=['jeweler'],
    package_dir={'': 'src'},
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
    include_package_data=True,
)
