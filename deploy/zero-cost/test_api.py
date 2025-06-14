#!/usr/bin/env python3
"""
Minimal test API server for ProStudio Zero-Cost deployment
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Simple in-memory cache for testing
cache = {}

class ProStudioHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'status': 'healthy',
                'service': 'prostudio-cache',
                'environment': os.environ.get('PROSTUDIO_ENV', 'development'),
                'redis_host': os.environ.get('REDIS_HOST', 'not-connected'),
                'cache_size': len(cache)
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed_path.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            metrics = f"""# HELP prostudio_cache_size Number of items in cache
# TYPE prostudio_cache_size gauge
prostudio_cache_size {len(cache)}

# HELP prostudio_up Service up status
# TYPE prostudio_up gauge
prostudio_up 1
"""
            self.wfile.write(metrics.encode())
            
        elif parsed_path.path.startswith('/api/cache/get/'):
            key = parsed_path.path.split('/')[-1]
            if key in cache:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'key': key, 'value': cache[key], 'found': True}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'key': key, 'found': False, 'error': 'Key not found'}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/cache/set':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                key = data.get('key')
                value = data.get('value')
                
                if key and value:
                    cache[key] = value
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'success': True, 'key': key}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'error': 'Missing key or value'}
                    self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    port = int(os.environ.get('PORT', '8000'))
    server_address = ('', port)
    
    print(f"Starting ProStudio Test API Server on port {port}")
    print(f"Environment: {os.environ.get('PROSTUDIO_ENV', 'development')}")
    print(f"Redis Host: {os.environ.get('REDIS_HOST', 'not-configured')}")
    print("Server ready!")
    
    httpd = HTTPServer(server_address, ProStudioHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    main()