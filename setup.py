from setuptools import setup

setup(
    name='league-vcs',
    version='0.0.1',
    packages=['league_vcs', 'league_vcs.parsers', 'league_vcs.support'],
    author='Pranav Nutalapati',
    entry_points={
        'console_scripts': ['league-vcs=league_vcs.cli:main']
    },
    install_requires=['click', 'pywin32', 'tqdm', 'wxPython'],
)
