#!/usr/bin/env python3
import html, json, os, re, threading, urllib.parse, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION="0.3"
HOST,PORT="127.0.0.1",8765
ROOT=os.path.dirname(os.path.abspath(__file__))
STATE=os.path.join(ROOT,"selected.json")
QUERIES=[
    "unexpected shorts","crazy animals shorts","oddly satisfying shorts",
    "insane skills shorts","funny fails shorts","crazy nature shorts","weird things shorts"
]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36"

PAGE=r'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Viral Scout</title>
<style>
:root{--bg:#0e0f11;--card:#17191d;--line:#292c32;--text:#f5f6f7;--muted:#9399a5;--accent:#d8ff55}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.4 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:1060px;margin:auto;padding:30px 20px 60px}.top{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}
h1{margin:0;font-size:24px}.sub,#status{color:var(--muted);font-size:13px}.sub{margin-top:4px}#status{margin-bottom:18px}
button,a.btn{border:0;border-radius:10px;padding:11px 15px;font-weight:800;cursor:pointer;text-decoration:none;display:inline-flex;justify-content:center;align-items:center}
.primary{background:var(--accent);color:#111}.ghost{background:#23262b;color:var(--text)}button:disabled{opacity:.55}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}.picked{outline:2px solid var(--accent);outline-offset:-2px}
.thumb{height:170px;background:#090a0c}.thumb img{width:100%;height:100%;object-fit:cover}.body{padding:14px}.meta{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.title{font-weight:800;min-height:42px;margin:7px 0 10px}.momentum{font-size:24px;font-weight:900;color:var(--accent)}.label{font-size:11px;color:var(--muted);text-transform:uppercase}.stats{font-size:12px;color:#c8ccd4;margin:9px 0 13px;display:flex;gap:12px}.actions{display:flex;gap:8px}.actions>*{flex:1}
.empty{border:1px dashed var(--line);border-radius:14px;padding:34px;text-align:center;color:var(--muted)}
@media(max-width:650px){.top{flex-direction:column;align-items:stretch}.grid{grid-template-columns:1fr}}
</style></head><body><div class="wrap">
<div class="top"><div><h1>Viral Scout</h1><div class="sub">Свежие визуальные кандидаты. Ничего лишнего.</div></div><button id="scan" class="primary">Сканировать</button></div>
<div id="status">YouTube · свежесть до 7 дней · сортировка по просмотрам в час</div><div id="grid" class="grid"><div class="empty">Нажми «Сканировать».</div></div></div>
<script>
const grid=document.getElementById('grid'),statusEl=document.getElementById('status'),scan=document.getElementById('scan');let selected=new Set();
const esc=s=>(s||'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const compact=n=>n>=1e9?(n/1e9).toFixed(n>=1e10?0:1)+'B':n>=1e6?(n/1e6).toFixed(n>=1e7?0:1)+'M':n>=1e3?(n/1e3).toFixed(n>=1e4?0:1)+'K':Math.round(n).toString();
async function load(){try{let j=await (await fetch('/api/selected')).json();selected=new Set(j.ids||[])}catch(e){}}
function card(x){let p=selected.has(x.id);return `<div class="card ${p?'picked':''}" id="c-${x.id}"><div class="thumb"><img src="${esc(x.thumbnail)}" loading="lazy"></div><div class="body"><div class="meta">${esc(x.author||'YouTube')} · ${esc(x.age_label)} · ${esc(x.duration||'')}</div><div class="title">${esc(x.title)}</div><div class="momentum">⚡ ${compact(x.momentum)}/ч</div><div class="label">просмотров в час</div><div class="stats"><span>▶ ${compact(x.views)}</span><span>${esc(x.query)}</span></div><div class="actions"><a class="btn ghost" target="_blank" href="${esc(x.url)}">Открыть</a><button class="${p?'ghost':'primary'}" onclick="pick('${x.id}')">${p?'В работе ✓':'В работу'}</button></div></div></div>`}
async function pick(id){let j=await(await fetch('/api/select',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})})).json();selected=new Set(j.ids||[]);let c=document.getElementById('c-'+id);if(c){let p=selected.has(id);c.classList.toggle('picked',p);let b=c.querySelector('button');b.className=p?'ghost':'primary';b.textContent=p?'В работе ✓':'В работу'}}
scan.onclick=async()=>{scan.disabled=true;scan.textContent='Ищу…';statusEl.textContent='Сканирую свежие Shorts…';grid.innerHTML='<div class="empty">Сканирование…</div>';try{let r=await fetch('/api/scan'),j=await r.json();if(!r.ok)throw Error(j.error||'Ошибка');statusEl.textContent=`Найдено ${j.total_found} · TOP ${j.items.length} · v${j.version}`;grid.innerHTML=j.items.map(card).join('')||'<div class="empty">Сильных свежих кандидатов сейчас нет.</div>'}catch(e){statusEl.textContent='Ошибка: '+e.message;grid.innerHTML='<div class="empty">Источник не ответил. Повтори позже.</div>'}finally{scan.disabled=false;scan.textContent='Сканировать'}};
load();
</script></body></html>'''

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept-Language":"en-US,en;q=0.9"})
    with urllib.request.urlopen(req,timeout=15) as r:
        return r.read().decode("utf-8","replace")

def json_obj(text,pos):
    i=text.find("{",pos)
    if i<0: raise ValueError("json")
    depth=0; string=False; esc=False
    for j in range(i,len(text)):
        c=text[j]
        if string:
            if esc: esc=False
            elif c=="\\": esc=True
            elif c=='"': string=False
        else:
            if c=='"': string=True
            elif c=="{": depth+=1
            elif c=="}":
                depth-=1
                if depth==0:return text[i:j+1]
    raise ValueError("json")

def initial(page):
    for m in ("var ytInitialData =","window[\"ytInitialData\"] =","ytInitialData ="):
        p=page.find(m)
        if p>=0:return json.loads(json_obj(page,p+len(m)))
    raise RuntimeError("YouTube изменил страницу поиска")

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)

def txt(x):
    if not isinstance(x,dict):return ""
    if x.get("simpleText"):return str(x["simpleText"])
    return "".join(str(r.get("text","")) for r in x.get("runs",[]) if isinstance(r,dict))

def views(s):
    s=(s or "").lower().replace(",","")
    m=re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([kmb])?",s)
    if not m:return 0
    return int(float(m.group(1))*{None:1,"k":1e3,"m":1e6,"b":1e9}.get(m.group(2),1))

def age_hours(s):
    s=(s or "").lower()
    m=re.search(r"([0-9]+)\s*(minute|hour|day|week|month|year)",s)
    if not m:return None
    return int(m.group(1))*{"minute":1/60,"hour":1,"day":24,"week":168,"month":720,"year":8760}[m.group(2)]

def dur_seconds(s):
    try:
        n=0
        for p in s.split(":"):n=n*60+int(p)
        return n
    except:return None

def age_label(h):
    if h is None:return "?"
    if h<1:return f"{max(1,int(h*60))}м"
    if h<24:return f"{max(1,int(h))}ч"
    return f"{max(1,int(h/24))}д"

def parse(v,q):
    vid=v.get("videoId")
    if not vid:return None
    title=txt(v.get("title")) or "Без названия"
    vc=views(txt(v.get("viewCountText")) or txt(v.get("shortViewCountText")))
    ah=age_hours(txt(v.get("publishedTimeText")))
    duration=txt(v.get("lengthText"))
    sec=dur_seconds(duration)
    thumbs=(v.get("thumbnail") or {}).get("thumbnails") or []
    thumb=thumbs[-1].get("url","") if thumbs else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
    return {"id":vid,"title":html.unescape(title),"views":vc,"age_hours":ah,"age_label":age_label(ah),"duration":duration,"seconds":sec,"author":txt(v.get("ownerText")) or txt(v.get("longBylineText")),"thumbnail":thumb,"url":"https://www.youtube.com/watch?v="+vid,"query":q}

def query(q):
    url="https://www.youtube.com/results?search_query="+urllib.parse.quote_plus(q)+"&sp=CAI%3D"
    data=initial(fetch(url)); out=[]
    for n in walk(data):
        if "videoRenderer" in n:
            x=parse(n["videoRenderer"],q)
            if x:out.append(x)
    return out

def scan():
    rows=[]; errors=[]
    for q in QUERIES:
        try:rows.extend(query(q))
        except Exception as e:errors.append(str(e))
    uniq={}
    for x in rows:
        if x["id"] not in uniq or x["views"]>uniq[x["id"]]["views"]:uniq[x["id"]]=x
    out=[]
    for x in uniq.values():
        a=x["age_hours"]; s=x["seconds"]; v=x["views"]
        if a is None or a>168 or v<500:continue
        if s is not None and s>180:continue
        x["momentum"]=v/max(a,.5);out.append(x)
    out.sort(key=lambda x:(x["momentum"],x["views"]),reverse=True)
    if not out and errors:raise RuntimeError("YouTube сейчас не отдал свежие результаты")
    return out

def load_selected():
    try:
        with open(STATE,"r",encoding="utf-8") as f:return set(json.load(f).get("ids",[]))
    except:return set()

def save_selected(ids):
    with open(STATE,"w",encoding="utf-8") as f:json.dump({"ids":sorted(ids)},f,ensure_ascii=False,indent=2)

class H(BaseHTTPRequestHandler):
    def log_message(self,*_):pass
    def js(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False).encode();self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        p=urllib.parse.urlparse(self.path).path
        if p=="/":
            b=PAGE.encode();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
        elif p=="/api/scan":
            try:
                x=scan();self.js({"items":x[:20],"total_found":len(x),"version":VERSION})
            except Exception as e:self.js({"error":str(e)},503)
        elif p=="/api/selected":self.js({"ids":sorted(load_selected())})
        else:self.js({"error":"not found"},404)
    def do_POST(self):
        if urllib.parse.urlparse(self.path).path!="/api/select":self.js({"error":"not found"},404);return
        try:
            n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n) or b"{}");i=str(d.get("id","")).strip()
        except:i=""
        if not i:self.js({"error":"bad id"},400);return
        ids=load_selected()
        if i in ids:ids.remove(i)
        else:ids.add(i)
        save_selected(ids);self.js({"ids":sorted(ids)})

def main():
    s=ThreadingHTTPServer((HOST,PORT),H);u=f"http://{HOST}:{PORT}"
    print(f"Viral Scout v{VERSION}: {u}");print("Закрыть: Ctrl+C")
    threading.Timer(.7,lambda:webbrowser.open(u)).start()
    try:s.serve_forever()
    except KeyboardInterrupt:pass

if __name__=="__main__":main()
