from cx_Freeze import setup, Executable

setup(name="league-vcs",
      version="0.1.0",
      description="",
      executables=[
          Executable("entrypoints/main.py", targetName='League VCS',
                     icon='raster/icon.ico', base='Win32GUI'),
      ])
