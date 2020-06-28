from cx_Freeze import setup, Executable

setup(name="league-vcs",
      version="0.0.1",
      description="",
      executables=[
          # Executable("entrypoints/cli.py", targetName='league-vcs'),
          # Executable("entrypoints/watch.py"),
          Executable("entrypoints/main.py", targetName='League VCS',
                     icon='raster/icon.ico', base='Win32GUI'),
      ],
      )
      # options={'build_exe': {
      #     'include_files': ['league_vcs/gui/icons']}})
