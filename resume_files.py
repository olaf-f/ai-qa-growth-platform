"""Extract PDF text in a short-lived local worker; no network or uploaded-file retention."""
import io
import json
import logging
import sys

MAX_CHARS = 25000
MAX_PAGES = 30

def extract_pdf(content):
    if not content or len(content) > 5 * 1024 * 1024:
        raise ValueError('文件为空或超过5MB，请精简后上传。')
    if b'%PDF-' not in content[:1024]:
        raise ValueError('文件内容不是有效PDF，请勿只修改扩展名。')
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ValueError('当前Python缺少PDF解析组件，请安装requirements.txt后重启服务。') from None
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    try:
        reader = PdfReader(io.BytesIO(content), strict=False)
        if reader.is_encrypted:
            try:
                opened = reader.decrypt('')
            except Exception:
                opened = False
            if not opened:
                raise ValueError('PDF已加密，请在本机解除打开密码后重新上传。')
        count = len(reader.pages)
        if count < 1 or count > MAX_PAGES:
            raise ValueError('PDF页数需在1–30页内，请仅上传简历部分。')
        pages, blank_pages = [], []
        for i, page in enumerate(reader.pages):
            value = (page.extract_text() or '').replace('\x00', '').strip()
            if not value:
                blank_pages.append(i + 1)
            pages.append(value)
            if sum(len(t) for t in pages) > MAX_CHARS:
                raise ValueError('简历文字超过25000字，请精简后重新上传。')
        text = '\n\n'.join(pages).strip()
        if not text:
            raise ValueError('未发现可提取文字，可能是扫描件或图片PDF。请先用OCR识别，或上传原始Word文件。')
        warnings = ['PDF分栏、表格可能影响文字顺序，请检查正文后再诊断。']
        if blank_pages:
            warnings.append('第'+ '、'.join(map(str, blank_pages))+'页未提取到文字，可能是图片或空白页，请核对是否遗漏。')
        if '\ufffd' in text:
            warnings.append('提取结果可能有乱码，请检查字体编码或改用Word文件。')
        return {'text': text, 'pages': count, 'warnings': warnings, 'format': 'pdf'}
    except ValueError:
        raise
    except Exception:
        raise ValueError('PDF无法解析，可能已损坏、加密或使用了不支持的编码。请重新导出PDF或上传Word。') from None

if __name__ == '__main__':
    try:
        result = extract_pdf(sys.stdin.buffer.read(5 * 1024 * 1024 + 1))
        output = {'result': result}
    except ValueError as error:
        output = {'error': str(error)}
    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False).encode('utf-8'))
