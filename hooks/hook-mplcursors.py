# hook-mplcursors.py

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('mplcursors')
datas = collect_data_files('mplcursors')
