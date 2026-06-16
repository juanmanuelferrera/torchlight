import json, html, re, os, shutil, collections
T=[t for t in json.load(open('data_full.json',encoding='utf-8')) if t['title'].strip()]
OUT='dist'; shutil.rmtree(OUT,ignore_errors=True)
os.makedirs(OUT+'/q',exist_ok=True); os.makedirs(OUT+'/c',exist_ok=True); shutil.copy('theme.css', OUT+'/style.css')
CAT={'1':'Philosophy','2':'Health','5':'Tech','7':'Sadhana','9':'Other','11':'Social'}
CATDESC={'Social':'Everything related to social interactions (ISKCON issues go here too).','Other':'Questions that do not relate to any other category.'}
CATORDER=['Philosophy','Social','Sadhana','Health','Tech','Other']
NQ=len(T); NA=sum(len(t['answers']) for t in T)
TAGLINE='A read-only archive of {:,} questions and {:,} answers from a Gauḍīya Vaiṣṇava forum (2007–2012).'.format(NQ,NA)
def cn(t): return CAT.get(t.get('cat',''),'Other')
ESC2={'n':'\n','r':'\n','t':'  ','"':'"',"'":"'",'\\':'\\','/':'/'}
def unesc2(s): return re.sub(r'\\(.)', lambda m: ESC2.get(m.group(1), m.group(1)), s or '')
for t in T:
    t['title']=unesc2(t['title']); t['body']=unesc2(t['body'])
    for a in t['answers']: a['text']=unesc2(a['text'])
def esc(s): return html.escape(s or '')
def fmt(s):
    s=s or ''
    if re.search(r'<\s*(div|span|br|p|a|b|i|strong|em|img|blockquote|font|ul|ol|li|table)\b', s, re.I):
        s=re.sub(r'<\s*img[^>]*src="([^"]+)"[^>]*>', r' \1 ', s, flags=re.I)
        s=re.sub(r'<\s*br\s*/?>', '\n', s, flags=re.I)
        s=re.sub(r'</\s*(div|p|blockquote|li|tr|h[1-6])\s*>', '\n', s, flags=re.I)
        s=re.sub(r'<[^>]+>', '', s)
        s=html.unescape(s)
    s=re.sub(r'\n{3,}','\n\n', s)
    s=esc(s)
    s=re.sub(r'(https?://[^\s<)]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)
    return s.strip().replace('\n','<br>')
FONTS=('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
 '<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Spectral:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')
SVG=('<svg class="mark" viewBox="0 0 48 48" fill="none" aria-hidden="true">'
 '<path d="M24 6c-2.4 4.8-2.4 9.6 0 14.4 2.4-4.8 2.4-9.6 0-14.4Z" fill="currentColor" opacity=".9"/>'
 '<path d="M24 22c-3.2-3.6-7.2-5.6-12-6 .8 5.2 4 9.2 9.2 11.2" fill="currentColor" opacity=".55"/>'
 '<path d="M24 22c3.2-3.6 7.2-5.6 12-6-.8 5.2-4 9.2-9.2 11.2" fill="currentColor" opacity=".55"/>'
 '<path d="M10 24c-2 1.2-3.6 3-4.8 5.6 6.4 5.2 14 7.2 18.8 7.2s12.4-2 18.8-7.2C41.6 27 40 25.2 38 24c-4 4.4-9.2 6.8-14 6.8S14 28.4 10 24Z" fill="currentColor"/></svg>')
HEADER=('<header><div class="wrap"><a class="brand" href="/">'+SVG+'<h1>Pariprashnena <span class="em">— Q&amp;A Archive</span></h1></a>'
        '<p class="tagline">'+TAGLINE+'</p><div id="search"></div></div></header>')
INIT='<script>window.addEventListener("DOMContentLoaded",function(){new PagefindUI({element:"#search",showSubResults:true,pageSize:15,resetStyles:false})});</script>'
def page(title, body):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'
      +esc(title)+'</title>'+FONTS+'<link rel="stylesheet" href="/style.css"><link href="/pagefind/pagefind-ui.css" rel="stylesheet"><script src="/pagefind/pagefind-ui.js"></script></head><body>'
      +HEADER+INIT+'<div class="wrap">'+body+'<footer>Pariprashnena — read-only archive · '+format(NQ,",")+' questions</footer></div></body></html>')
def taglink(t): return '<a class="tag" href="/c/'+cn(t).lower()+'.html">'+cn(t)+'</a>'
def tagspan(t): return '<span class="tag">'+cn(t)+'</span>'
def row(t): return ('<a href="/q/'+t['id']+'.html">'+esc(t['title'])+'<span class="m">'+tagspan(t)+' '+str(len(t['answers']))+' answers · '+esc(t['date'])+'</span></a>')
for t in T:
    ans="".join('<div class="ans" data-pagefind-body><div class="who">user ['+esc(a['user'])+']'+(' · '+esc(a['date']) if a.get('date') else '')+'</div>'+fmt(a['text'])+'</div>' for a in t['answers'])
    body=('<article class="q"><h2 data-pagefind-meta="title">'+esc(t['title'])+'</h2>'
      +'<div class="sub">'+taglink(t)+' · asked by user ['+esc(t.get('user',''))+'] · '+esc(t['date'])+' · '+str(len(t['answers']))+' answers</div>'
      +'<div class="body" data-pagefind-body>'+fmt(t['body'])+'</div>'+ans+'<p><a href="/">‹ all questions</a></p></article>')
    open(OUT+'/q/'+t['id']+'.html','w',encoding='utf-8').write(page(t['title'],body))
counts=collections.Counter(cn(t) for t in T)
for c in CATORDER:
    cts=sorted([t for t in T if cn(t)==c], key=lambda x:x['date'], reverse=True)
    desc='<p class="cdesc">'+CATDESC[c]+'</p>' if c in CATDESC else ''
    cbody='<h2 class="ctitle">'+c+' <span class="m">· '+str(len(cts))+' questions</span></h2>'+desc+'<div class="list">'+''.join(row(t) for t in cts)+'</div><p><a href="/">‹ all sections</a></p>'
    open(OUT+'/c/'+c.lower()+'.html','w',encoding='utf-8').write(page(c+' — Pariprashnena', cbody))
nav='<div class="catnav">'+''.join('<a href="/c/'+c.lower()+'.html">'+c+' <b>'+str(counts[c])+'</b></a>' for c in CATORDER)+'</div>'
allrows=''.join(row(t) for t in sorted(T,key=lambda x:x['date'],reverse=True))
open(OUT+'/index.html','w',encoding='utf-8').write(page('Pariprashnena — Q&A Archive', nav+'<div class="list">'+allrows+'</div>'))
print('generated', NQ, 'threads,', NA, 'answers')
