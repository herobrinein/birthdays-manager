#!/usr/bin/env python3
"""
生日管家 - PWA专用服务器
增加了对 manifest 的 MIME 类型支持，并禁止缓存 Service Worker
修改：启动后自动打开浏览器
"""

import http.server
import socketserver
import os
import sys
import mimetypes
import webbrowser  # 1. 引入 webbrowser 模块

PORT = 8000

# 切换到当前目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 确保 .json 文件被识别为 application/json 或 application/manifest+json
mimetypes.add_type('application/manifest+json', '.json')
mimetypes.add_type('application/manifest+json', '.webmanifest')

class PWAHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 禁止浏览器缓存 sw.js
        if self.path.endswith('sw.js'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        
        super().end_headers()

print(f"启动生日管家 PWA 服务器，端口: {PORT}")
print(f"请使用 Chrome/Edge 访问: http://localhost:{PORT}")
print("注意：PWA 功能仅在 localhost 或 HTTPS 下生效")
print("按 Ctrl+C 停止服务器\n")

with socketserver.TCPServer(("", PORT), PWAHandler) as httpd:
    try:
        # 2. 在进入死循环之前，自动打开浏览器
        url = f"http://localhost:{PORT}"
        print(f"正在自动打开浏览器: {url} ...")
        webbrowser.open(url)

        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")