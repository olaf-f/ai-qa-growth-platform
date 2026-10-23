"""Vercel API: stateless document extraction and protected AI requests."""
import json
import os
import sys
import hmac
from pathlib import Path
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from email.parser import BytesParser
from email.policy import default
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

class handler(BaseHTTPRequestHandler):
    def endpoint(self):
        parsed = urlparse(self.path)
        endpoint = parse_qs(parsed.query).get('endpoint', [''])[0]
        return '/api/' + endpoint if endpoint else parsed.path

    def reply(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.endpoint() == '/api/status':
            key, model = server.config()
            return self.reply(200, {'configured': bool(key and os.getenv('TESTLAB_ACCESS_TOKEN')), 'provider': 'DeepSeek', 'model': model, 'cloud': True})
        self.reply(404, {'error': '接口不存在。'})

    def do_POST(self):
        origin = self.headers.get('Origin', '')
        host = self.headers.get('X-Forwarded-Host') or self.headers.get('Host', '')
        if self.headers.get('X-TestLab-Request') != '1' or (origin and urlparse(origin).netloc != host):
            return self.reply(403, {'error': '请从平台页面发起请求。'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4 * 1024 * 1024:
                return self.reply(413, {'error': '在线上传不能超过4MB。'})
            body = self.rfile.read(length)
            path = self.endpoint()
            if path == '/api/extract':
                content_type = self.headers.get('Content-Type', '')
                if not content_type.startswith('multipart/form-data'):
                    raise ValueError('请选择Word或PDF文件。')
                msg = BytesParser(policy=default).parsebytes(('Content-Type: '+content_type+'\r\nMIME-Version: 1.0\r\n\r\n').encode()+body)
                for part in msg.iter_parts():
                    if part.get_param('name', header='content-disposition') == 'file':
                        return self.reply(200, server.extract_upload(part.get_filename() or '', part.get_payload(decode=True)))
                raise ValueError('没有找到文件。')
            if path == '/api/ai':
                access = os.getenv('TESTLAB_ACCESS_TOKEN', '')
                if not access:
                    return self.reply(503, {'error': '在线AI尚未启用：管理员需设置模型密钥和访问口令。本地配置不会自动上传。'})
                if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer '+access):
                    return self.reply(401, {'error': '请填写正确的在线AI访问口令。'})
                payload = json.loads(body)
                result = server.call_deepseek(payload.get('task'), payload.get('payload'))
                return self.reply(200, {'result': result})
            return self.reply(404, {'error': '接口不存在。'})
        except ValueError as e:
            return self.reply(400, {'error': str(e)})
        except Exception:
            return self.reply(500, {'error': '在线服务暂时无法处理，请稍后重试。'})
