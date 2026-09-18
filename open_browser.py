# 在浏览器里预览（不起透明桌宠窗口，只是看看立绘和交互）
# 直接双击 open_browser.html 也行，这个脚本只是帮你自动打开
import os
import sys
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
page = os.path.join(HERE, "whale.html")
webbrowser.open("file:///" + page.replace("\\", "/"))
print("已用默认浏览器打开:", page)
print("提示：浏览器模式下没有语音、没有窗口穿透、也没有自动游荡（这些要桌宠本体才有）。")
if sys.platform == "win32":
    input("\n回车关闭…")
