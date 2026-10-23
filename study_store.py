"""Local SQLite study journal. All source material stays on this computer."""
import json,sqlite3,uuid,os
from contextlib import contextmanager
from datetime import datetime,timezone,timedelta,date
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DATA=Path(os.environ.get('TESTLAB_STUDY_DIR',str(ROOT/'.learning-data')))
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
def day():return datetime.now(timezone(timedelta(hours=8))).date().isoformat()
@contextmanager
def connect():
    DATA.mkdir(exist_ok=True);db=sqlite3.connect(DATA/'study.sqlite',timeout=10);db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,title TEXT NOT NULL,resource_id TEXT,due TEXT,status TEXT,created TEXT,updated TEXT);CREATE TABLE IF NOT EXISTS logs(id TEXT PRIMARY KEY,date TEXT,resource_id TEXT,title TEXT,minutes INTEGER,note TEXT,created TEXT);CREATE TABLE IF NOT EXISTS progress(resource_id TEXT PRIMARY KEY,status TEXT,updated TEXT);')
    try:
        with db:yield db
    finally:db.close()
def clean(s,maxlen=3000):
    if not isinstance(s,str)or len(s)>maxlen:raise ValueError('字段格式或长度不正确。')
    return s.strip()
def valid_date(s):
    s=clean(s,10)
    try:date.fromisoformat(s)
    except ValueError:raise ValueError('日期格式应为YYYY-MM-DD。')from None
    return s
def snapshot():
    with connect()as db:
        return {'version':1,'today':day(),'tasks':[dict(x)for x in db.execute('SELECT * FROM tasks ORDER BY created DESC')],'logs':[dict(x)for x in db.execute('SELECT * FROM logs ORDER BY date DESC,created DESC')],'progress':[dict(x)for x in db.execute('SELECT * FROM progress')],'exported_at':now()}
def mutate(d):
    if not isinstance(d,dict):raise ValueError('请求格式错误。')
    action=d.get('action');stamp=now()
    with connect()as db:
        if action=='add_task':
            title=clean(d.get('title',''),200)
            if not title:raise ValueError('请填写待办内容。')
            due=valid_date(d['due'])if d.get('due')else ''
            db.execute('INSERT INTO tasks VALUES(?,?,?,?,?,?,?)',(uuid.uuid4().hex,title,clean(d.get('resource_id',''),40),due,'todo',stamp,stamp))
        elif action=='task_status':
            status=d.get('status')
            if status not in {'todo','done','archived'}:raise ValueError('待办状态不正确。')
            cur=db.execute('UPDATE tasks SET status=?,updated=? WHERE id=?',(status,stamp,clean(d.get('id',''),40)))
            if not cur.rowcount:raise ValueError('待办不存在。')
        elif action=='log':
            minutes=d.get('minutes')
            if isinstance(minutes,bool)or not isinstance(minutes,int)or not 1<=minutes<=1440:raise ValueError('学习时长应为1–1440分钟。')
            title=clean(d.get('title',''),200)
            if not title:raise ValueError('请填写本次学习内容。')
            db.execute('INSERT INTO logs VALUES(?,?,?,?,?,?,?)',(uuid.uuid4().hex,valid_date(d.get('date','')),clean(d.get('resource_id',''),40),title,minutes,clean(d.get('note','')),stamp))
        elif action=='delete_log':
            # Only explicit confirmation in the UI triggers removal of a mistaken journal entry.
            db.execute('DELETE FROM logs WHERE id=?',(clean(d.get('id',''),40),))
        elif action=='progress':
            status=d.get('status');rid=clean(d.get('resource_id',''),40)
            if status not in {'unread','learning','done'}or not rid:raise ValueError('学习状态不正确。')
            db.execute('INSERT INTO progress VALUES(?,?,?) ON CONFLICT(resource_id) DO UPDATE SET status=excluded.status,updated=excluded.updated',(rid,status,stamp))
        elif action=='import':
            backup=d.get('backup')
            if not isinstance(backup,dict)or backup.get('version')!=1:raise ValueError('不是有效的学习记录备份。')
            if any(not isinstance(backup.get(k),list)or len(backup[k])>50000 for k in ('tasks','logs','progress')):raise ValueError('备份记录格式不正确或数量超限。')
            for t in backup['tasks']:
                if not isinstance(t,dict)or t.get('status')not in {'todo','done','archived'}:raise ValueError('备份中的待办状态不正确。')
                title=clean(t.get('title',''),200);identifier=clean(t.get('id',''),40)
                if not title or not identifier:raise ValueError('备份中的待办缺少内容。')
                db.execute('INSERT OR IGNORE INTO tasks VALUES(?,?,?,?,?,?,?)',(identifier,title,clean(t.get('resource_id',''),40),valid_date(t['due'])if t.get('due')else '',t['status'],clean(t.get('created',stamp),50),stamp))
            for l in backup['logs']:
                if not isinstance(l,dict)or isinstance(l.get('minutes'),bool)or not isinstance(l.get('minutes'),int)or not 1<=l['minutes']<=1440:raise ValueError('备份中的学习时长不正确。')
                title=clean(l.get('title',''),200);identifier=clean(l.get('id',''),40)
                if not title or not identifier:raise ValueError('备份中的日记缺少内容。')
                db.execute('INSERT OR IGNORE INTO logs VALUES(?,?,?,?,?,?,?)',(identifier,valid_date(l.get('date','')),clean(l.get('resource_id',''),40),title,l['minutes'],clean(l.get('note','')),clean(l.get('created',stamp),50)))
            for p in backup['progress']:
                if not isinstance(p,dict)or p.get('status')not in {'unread','learning','done'}:raise ValueError('备份中的进度不正确。')
                identifier=clean(p.get('resource_id',''),40)
                if not identifier:raise ValueError('进度缺少资料ID。')
                db.execute('INSERT OR IGNORE INTO progress VALUES(?,?,?)',(identifier,p['status'],clean(p.get('updated',stamp),50)))
        else:raise ValueError('不支持的学习操作。')
    return snapshot()
_cached=None;_mtime=None
def library():
    global _cached,_mtime
    p=DATA/'library.json'
    if not p.exists():return {'meta':{'indexed':0,'categories':[]},'items':[]}
    stamp=p.stat().st_mtime_ns
    if _cached is None or _mtime!=stamp:_cached=json.loads(p.read_text(encoding='utf-8'));_mtime=stamp
    return _cached
def search(query):
    lib=library();q=query.get('q',[''])[0].lower()[:150];category=query.get('category',['all'])[0];kind=query.get('kind',['all'])[0]
    try:page=max(1,int(query.get('page',['1'])[0]))
    except ValueError:page=1
    items=[r for r in lib['items']if(category=='all'or r['category']==category)and(kind=='all'or r['kind']==kind)and(not q or q in(r['title']+' '+r['path']+' '+r['body']).lower())]
    # Prefer unique learning documents over repeated copies and implementation files.
    items.sort(key=lambda r:(r['duplicate_of']is not None,r['kind']!='文档',q not in r['title'].lower(),r['path']))
    return {'meta':lib['meta'],'total':len(items),'page':page,'pages':max(1,(len(items)+19)//20),'items':[{k:v for k,v in r.items()if k!='body'}for r in items[(page-1)*20:page*20]]}
def item(identifier):
    return next((r for r in library()['items']if r['id']==identifier),None)
