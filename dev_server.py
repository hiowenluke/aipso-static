#!/usr/bin/env python3
"""
开发环境静态资源服务器
支持多产品架构，通过子域名或路径识别产品
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, unquote
import mimetypes

# 配置
PORT = 8080
STORE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# 产品配置（子域名到产品slug的映射）
PRODUCT_MAPPING = {
    'headshot': 'headshot-ai',
    'groupphoto': 'group-photo-ai',
    'fashionshot': 'fashion-shot-ai',
}

class MultiProductHandler(http.server.SimpleHTTPRequestHandler):
    """支持多产品架构的静态资源处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STORE_ROOT, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        # 解析请求
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)
        
        # 从Host头获取子域名
        host = self.headers.get('Host', '')
        product_slug = self._get_product_from_host(host)
        
        # 如果从Host无法识别，尝试从路径识别
        if not product_slug:
            product_slug = self._get_product_from_path(path)
        
        # 构建实际文件路径
        if product_slug:
            # 移除路径中的产品slug（如果存在）
            path = self._remove_product_from_path(path, product_slug)
            file_path = os.path.join(STORE_ROOT, product_slug, path.lstrip('/'))
        else:
            # 直接访问路径
            file_path = os.path.join(STORE_ROOT, path.lstrip('/'))
        
        # 检查文件是否存在
        if os.path.isfile(file_path):
            self._serve_file(file_path)
        elif os.path.isdir(file_path):
            # 如果是目录，尝试列出目录内容
            self._serve_directory(file_path, path)
        else:
            self.send_error(404, f"File not found: {path}")
    
    def _get_product_from_host(self, host):
        """从Host头提取产品slug"""
        # 移除端口号
        hostname = host.split(':')[0]
        
        # 提取子域名
        parts = hostname.split('.')
        if len(parts) >= 2:
            subdomain = parts[0]
            if subdomain in PRODUCT_MAPPING:
                return PRODUCT_MAPPING[subdomain]
        
        return None
    
    def _get_product_from_path(self, path):
        """从路径提取产品slug"""
        parts = path.strip('/').split('/')
        if parts and parts[0] in PRODUCT_MAPPING.values():
            return parts[0]
        return None
    
    def _remove_product_from_path(self, path, product_slug):
        """从路径中移除产品slug"""
        parts = path.strip('/').split('/')
        if parts and parts[0] == product_slug:
            return '/' + '/'.join(parts[1:])
        return path
    
    def _serve_file(self, file_path):
        """提供文件服务"""
        try:
            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # 读取文件
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 发送响应
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', len(content))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def _serve_directory(self, dir_path, url_path):
        """列出目录内容"""
        try:
            items = os.listdir(dir_path)
            items.sort()
            
            # 生成HTML
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Directory: {url_path}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ padding: 5px 0; }}
        a {{ text-decoration: none; color: #0066cc; }}
        a:hover {{ text-decoration: underline; }}
        .dir {{ font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Directory: {url_path}</h1>
    <ul>
        <li><a href="../">../</a></li>
"""
            
            for item in items:
                item_path = os.path.join(dir_path, item)
                is_dir = os.path.isdir(item_path)
                display_name = item + '/' if is_dir else item
                css_class = 'dir' if is_dir else ''
                html += f'        <li class="{css_class}"><a href="{item}">{display_name}</a></li>\n'
            
            html += """    </ul>
</body>
</html>"""
            
            # 发送响应
            content = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            self.send_error(500, f"Error listing directory: {str(e)}")
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def main():
    """启动服务器"""
    print("=" * 60)
    print("🚀 开发环境静态资源服务器")
    print("=" * 60)
    print(f"📁 根目录: {STORE_ROOT}")
    print(f"🌐 端口: {PORT}")
    print()
    print("📦 支持的产品:")
    for subdomain, slug in PRODUCT_MAPPING.items():
        print(f"   • {subdomain}.localhost:{PORT} → {slug}/")
    print()
    print("🔗 访问方式:")
    print(f"   1. 子域名: http://headshot.localhost:{PORT}/images/home/...")
    print(f"   2. 路径:   http://localhost:{PORT}/headshot-ai/images/home/...")
    print()
    print("💡 提示:")
    print("   • 使用 Ctrl+C 停止服务器")
    print("   • 支持 CORS，可跨域访问")
    print("   • 自动识别 MIME 类型")
    print("=" * 60)
    print()
    
    try:
        with socketserver.TCPServer(("", PORT), MultiProductHandler) as httpd:
            print(f"✅ 服务器已启动: http://localhost:{PORT}")
            print()
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
