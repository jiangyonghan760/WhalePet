# -*- coding: utf-8 -*-
"""一键安装依赖。用当前 Python 解释器把 requirements.txt 装好。"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REQ = os.path.join(HERE, "requirements.txt")


def main():
    print("=" * 46)
    print(" WhalePet 依赖安装")
    print(" Python:", sys.executable)
    print("=" * 46)
    cmd = [sys.executable, "-m", "pip", "install", "-r", REQ]
    print("$ " + " ".join(cmd) + "\n")
    rc = subprocess.call(cmd)
    if rc == 0:
        print("\n[OK] 依赖装好了，双击 launch.bat（Windows）或 python pet.pyw 即可启动。")
    else:
        print("\n[FAIL] 安装失败（退出码 %d）。" % rc)
        print("       可换成国内源重试：")
        print("       pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")
    input("\n回车关闭…")


if __name__ == "__main__":
    main()
