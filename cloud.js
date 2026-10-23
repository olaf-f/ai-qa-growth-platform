// Loaded only by the cloud build. Personal records stay in this browser.
const cloudStudyKey='ai-qa-cloud-study-v1';
const cloudDay=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
function cloudRead(){const d=JSON.parse(localStorage.getItem(cloudStudyKey)||'{"version":1,"tasks":[],"logs":[],"progress":[]}');return {...d,today:cloudDay(),exported_at:new Date().toISOString()}}
function cloudStudy(body){const d=cloudRead(),stamp=new Date().toISOString(),id=crypto.randomUUID().replaceAll('-','');
 if(!body)return d;
 const title=String(body.title||'').trim().slice(0,200),rid=String(body.resource_id||'').slice(0,40);
 switch(body.action){
 case 'add_task':if(!title)throw Error('请填写待办内容');d.tasks.unshift({id,title,resource_id:rid,due:body.due||'',status:'todo',created:stamp,updated:stamp});break;
 case 'task_status':if(!['todo','done','archived'].includes(body.status))throw Error('状态无效');{const t=d.tasks.find(t=>t.id===body.id);if(t){t.status=body.status;t.updated=stamp}}break;
 case 'log':if(!title||!Number.isInteger(body.minutes)||body.minutes<1||body.minutes>1440)throw Error('请填写内容及1–1440分钟时长');d.logs.unshift({id,date:body.date||cloudDay(),resource_id:rid,title,minutes:body.minutes,note:String(body.note||'').slice(0,3000),created:stamp});break;
 case 'delete_log':d.logs=d.logs.filter(l=>l.id!==body.id);break;
 case 'progress':if(!['unread','learning','done'].includes(body.status)||!rid)throw Error('状态无效');d.progress=d.progress.filter(p=>p.resource_id!==rid);d.progress.push({resource_id:rid,status:body.status,updated:stamp});break;
 case 'import':{const b=body.backup;if(!b||b.version!==1||!['tasks','logs','progress'].every(k=>Array.isArray(b[k])&&b[k].length<=50000))throw Error('备份格式不正确');for(const k of ['tasks','logs','progress']){const key=k==='progress'?'resource_id':'id',seen=new Set(d[k].map(x=>x[key]));for(const x of b[k])if(x&&typeof x[key]==='string'&&!seen.has(x[key])){d[k].push(x);seen.add(x[key])}}break}
 default:throw Error('不支持的操作');}
 localStorage.setItem(cloudStudyKey,JSON.stringify(d));return cloudRead();
}
const originalLocalApi=localApi;
localApi=async function(path,body){
 if(path==='/api/study'||path==='/api/study/export')return cloudStudy(body);
 if(path==='/api/library/reindex')throw Error('在线版不能访问电脑D盘，请在本地版刷新私人资料。');
 if(path.startsWith('/api/library/item'))throw Error('本机私人资料未公开上传，请使用本地版阅读。');
 if(path.startsWith('/api/library'))return {meta:{indexed:0,readable:0,duplicates:0,categories:[],source:'在线版不公开本机私人目录。平台课程、行业知识和RAG实战可在对应菜单学习。'},items:[],total:0,page:1,pages:1};
 return originalLocalApi(path,body);
};
const originalKbHead=kbHead;
kbHead=function(tab='library'){return originalKbHead(tab)+'<div class="callout">在线版：待办与每日进度仅保存在当前浏览器，可导出备份；不会自动同步其他设备。本机D盘资料未上传。</div>'};
const cloudFetch=window.fetch.bind(window);
window.fetch=async function(input,options){if(input==='/api/ai'){const token=sessionStorage.getItem('ai-qa-cloud-access')||prompt('请输入管理员提供的在线AI访问口令（不是DeepSeek密钥）');if(token){sessionStorage.setItem('ai-qa-cloud-access',token);options={...options,headers:{...options?.headers,Authorization:'Bearer '+token}}}}return cloudFetch(input,options)};
render();
