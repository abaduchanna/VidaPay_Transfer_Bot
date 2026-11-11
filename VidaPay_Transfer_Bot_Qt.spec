# -*- mode: python ; coding: utf-8 -*-
import datetime as _dt
_year = _dt.date.today().year

SPEC_DOC = f"""PyInstaller spec (PySide6/Qt build)
Developed by www.3SVerse.com © {_year}
Build command: pyinstaller VidaPay_Transfer_Bot_Qt.spec
"""


block_cipher = None

a = Analysis(
    ['VidaPay_Transfer_Bot_Qt.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('VidaPay_icon.ico', '.'),
        ('VidaPay_Logo.png', '.'),
        ('theme_manager_qt.py', '.'),
        ('header_manager_qt.py', '.'),
        ('native_titlebar_qt.py', '.'),
    ],
    hiddenimports = [
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'shiboken6',
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.edge',
        'selenium.webdriver.edge.options',
        'selenium.webdriver.edge.service',
        'selenium.webdriver.edge.webdriver',
        'selenium.webdriver.common',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.common.service',
        'selenium.webdriver.support',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.webdriver.remote',
        'selenium.webdriver.remote.webdriver',
        'selenium.webdriver.remote.command',
        'selenium.webdriver.remote.remote_connection',
        'selenium.common',
        'selenium.common.exceptions',
        'requests',
        'theme_manager_qt',
        'header_manager_qt',
        'native_titlebar_qt',
        'PIL',
        'pandas',
        'pytesseract',
        'schedule',
        # license_core.py (untouched business logic) shows a Tk-based
        # activation dialog when no valid license is present - tkinter
        # must stay bundled even though the main GUI no longer uses it.
        'tkinter',
        '_tkinter',
        # bs4: just declare the top-level package. PyInstaller's built-in
        # bs4 hook (from _pyinstaller_hooks_contrib) automatically pulls
        # in the correct builder modules for the installed bs4 version.
        # Listing 'bs4.builder.html_parser' manually fails because that
        # module name doesn't exist in modern bs4 (it's _htmlparser).
        'bs4',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[
        'doctest',
        'pdb',
        'pyperclip',
        'torch',
        'torchvision',
        'torchaudio',
        'matplotlib',
        'matplotlib.pyplot',
        'numba',
        'llvmlite',
        'sympy',
        'tensorflow',
        'scipy',
        'sklearn',
        'scikit-learn',
        'gi',
        'pygments',
        'fsspec',
        'tensorboard',
        'IPython',
        'ipython',
        'jupyter',
        'notebook',
        'PyQt6',
        'PyQt5',
        'PySide2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(60, 316),
    text_size=11,
    text_color='#96a8cd',
    text_default='Starting...',
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VidaPay_Transfer_Bot_Qt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='VidaPay_icon.ico',
)
