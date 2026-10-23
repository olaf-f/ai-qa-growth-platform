"""Read-only source indexing. Never imports or executes learning-source code."""
import hashlib,json,os,re
from collections import Counter
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=Path('D:/大辰金卡MBA/AI测试学习之路_周周')
DATA=ROOT/'.learning-data'
SKIP={'node_modules','.git','.venv','venv','__pycache__','dist','build','.idea','.pytest_cache','.mypy_cache'}
TEXT={'.md','.txt','.py','.vue','.js','.ts','.sql','.html','.css','.sh','.ps1','.ipynb'}
CATEGORIES=[('foundation','大模型与Prompt基础','模型原理、Token、上下文、提示词'),('python','Python与pytest','编程基础、单元测试、自动化框架'),('api','接口与业务测试','API、抓包、业务系统、数据库'),('rag','RAG与知识检索','检索、切分、向量、知识库'),('agent','Agent与Skills','工具调用、技能、MCP、多步执行'),('evaluation','评测与质量工程','指标、数据集、回归、可观测性'),('projects','实战项目与源码','业务系统、测试套件、项目实践'),('career','面试与简历作品','面试题、求职、个人作品集'),('roadmap','目录与学习路线','阅读入口、目录、综合笔记'),('attachments','附件与压缩包','图片、归档及其他辅助文件')]
def redact(value):
    value=re.sub(r'\bsk-[A-Za-z0-9_-]{12,}', '[已隐藏密钥]',value)
    value=re.sub(r'(?i)(bearer\s+)[A-Za-z0-9._-]{16,}',r'\1[已隐藏凭据]',value)
    value=re.sub(r'''(?im)((?:api[_-]?key|access[_-]?token|secret|password|passwd|密钥|密码)\s*[=:：]\s*["']?)[^\s"'`,;]{8,}''',r'\1[已隐藏凭据]',value)
    return value
def category(path,title):
    s=(path+' '+title).lower()
    if any(x in s for x in ['面试','简历','找工作','个人作品','作品集']):return 'career'
    if any(x in s for x in ['目录','start_here','readme','学习路线','听书稿']):return 'roadmap'
    if any(x in s for x in ['pytest','python基础','python语法']):return 'python'
    if any(x in s for x in ['rag','检索','向量','embedding','知识库','chunk']):return 'rag'
    if any(x in s for x in ['评测','eval','langfuse','指标','可观测','回归']):return 'evaluation'
    if any(x in s for x in ['agent','skill','mcp','工具调用']):return 'agent'
    if any(x in s for x in ['接口','抓包','postman','api代码','03-接口']):return 'api'
    if any(x in s for x in ['prompt','大模型基础','token','上下文','提示词']):return 'foundation'
    return 'projects'
def title_from(path,body):
    if path.suffix.lower()=='.md':
        match=re.search(r'^#{1,3}\s+(.+)',body,re.M)
        if match:return re.sub(r'[*`#]','',match[1]).strip()[:140]
    return path.stem[:140]
def build(source=SOURCE,data_dir=DATA):
    source=source.resolve()
    if not source.is_dir():raise ValueError('学习目录不可访问，请确认D盘与目录权限。')
    rows=[];skipped=Counter();hashes={};total=0
    for base,dirs,files in os.walk(source,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not (Path(base)/d).is_symlink())
        for name in sorted(files):
            p=Path(base)/name
            if p.is_symlink():continue
            total+=1;rel=p.relative_to(source).as_posix();suffix=p.suffix.lower()
            if name.startswith('.') or suffix in {'.pem','.key','.db','.sqlite','.log'} or any(x in name.lower() for x in ['credential','config.local','package-lock','pnpm-lock','faiss_index']):skipped['配置/缓存/隐藏文件']+=1;continue
            try:size=p.stat().st_size
            except OSError:skipped['不可读取']+=1;continue
            body='';preview='';kind='资料';status='仅文件索引'
            if suffix in TEXT and size<=2*1024*1024:
                try:
                    raw=p.read_bytes()
                    if b'\x00' in raw[:1000]:skipped['非文本内容']+=1;continue
                    try:body=raw.decode('utf-8-sig')
                    except UnicodeError:body=raw.decode('gb18030',errors='replace')
                    if suffix=='.ipynb':
                        nb=json.loads(body);body='\n\n'.join(''.join(c.get('source',[])) for c in nb.get('cells',[]) if c.get('cell_type')in{'markdown','code'})
                    if suffix=='.html':body=re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>','',body,flags=re.I);body=re.sub('<[^>]+>',' ',body)
                    body=redact(body);status='可阅读';kind='文档' if suffix in {'.md','.txt','.html'} else '代码'
                except (OSError,ValueError):skipped['无法提取文本']+=1;continue
            elif suffix in {'.zip','.7z','.rar'}:kind='压缩包'
            elif suffix in {'.png','.jpg','.jpeg','.gif','.webp'}:kind='图片'
            else:kind='附件'
            title=title_from(p,body);cat=category(rel,title) if body else 'attachments'
            headings=re.findall(r'^#{1,4}\s+(.+)',body,re.M)[:12] if suffix=='.md' else []
            clean=re.sub(r'!\[[^]]*\]\([^)]*\)|```[\s\S]*?```',' ',body)
            clean=re.sub(r'[#*`>|\[\]]',' ',clean);clean=re.sub(r'\s+',' ',clean).strip()
            preview=clean[:200]
            digest=hashlib.sha256(body.strip().encode()).hexdigest() if body else None
            duplicate=hashes.get(digest) if digest else None
            identifier=hashlib.sha256(rel.encode()).hexdigest()[:20]
            if digest and not duplicate:hashes[digest]=identifier
            rows.append({'id':identifier,'title':redact(title),'path':rel,'category':cat,'kind':kind,'extension':suffix,'size':size,'status':status,'summary':preview or '该资源为附件或归档文件，知识库记录其位置，不执行或解压。','headings':headings,'body':body[:180000],'truncated':len(body)>180000,'duplicate_of':duplicate,'minutes':min(90,max(5,round(len(body)/500))) if body else 0})
    rows.sort(key=lambda r:(r['category'],r['duplicate_of']is not None,r['kind']!='文档',r['path']))
    meta={'source':str(source),'indexed_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'scanned':total,'indexed':len(rows),'readable':sum(bool(r['body']) for r in rows),'duplicates':sum(bool(r['duplicate_of'])for r in rows),'skipped':dict(skipped),'categories':[{'id':i,'name':n,'description':d,'count':sum(r['category']==i for r in rows)}for i,n,d in CATEGORIES]}
    data_dir.mkdir(parents=True,exist_ok=True);temp=data_dir/'library.tmp';temp.write_text(json.dumps({'meta':meta,'items':rows},ensure_ascii=False),encoding='utf-8');temp.replace(data_dir/'library.json');return meta
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=True))
