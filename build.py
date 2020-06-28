from cx_Freeze import setup, Executable

setup(name="League VCS",
      version="0.1.0",
      description="Version control system and replay watcher for League of Legends.",
      executables=[
          Executable("entrypoints/main.py", targetName='League VCS',
                     icon='raster/icon.ico', base='Win32GUI'),
      ])
