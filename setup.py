from setuptools import setup

setup(
    name='league-vcs',
    version='0.1.0',
    packages=['league_vcs', 'league_vcs.parsers', 'league_vcs.gui', 'league_vcs.gui.frames', 'league_vcs.gui.icons',
              'league_vcs.gui.utils'],
    author='Pranav Nutalapati',
    entry_points={
        'console_scripts': ['league-vcs=league_vcs.cli:main']
    },
    install_requires=['click', 'pywin32', 'wxPython'],
)
