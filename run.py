# -*- coding: utf-8 -*-
"""启动器：优先用无控制台的 pythonw 拉起桌宠，避免留一个黑框。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PET = os.path.join(HERE, "pet.pyw")

# 找一个不弹控制台的解释器；找不到就用当前的
exe = sys.executable
if sys.platform == "win32":
    cand = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(cand):
        exe = cand

# 依赖没装的话给个明确提示，别让人对着闪退的窗口猜
try:
    import PySide6  # noqa: F401
except ImportError:
    print("[!] 还没装依赖。请先双击 install_deps.py，或在命令行执行：")
    print("    python install_deps.py")
    input("\n回车关闭…")
    sys.exit(1)

subprocess.Popen([exe, PET], cwd=HERE)
print("桌宠已启动。如果没看到它，检查一下屏幕右下角～")
