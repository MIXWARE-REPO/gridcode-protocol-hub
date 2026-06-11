from playwright.sync_api import sync_playwright
URL='https://nuba.grid-code.tech'; USER='Laia@grid-code.tech'; PW='elsaltodelpapu'

def sel(page,arr):
    for s in arr:
        l=page.locator(s).first
        if l.count()>0:return l,s
    return None,None

with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    c=b.new_context(viewport={"width":1920,"height":1080})
    page=c.new_page(); page.set_default_timeout(30000)
    page.goto(URL); page.wait_for_timeout(8000)
    sel(page,['input[name="username"]','input[name="email"]','input[type="email"]'])[0].fill(USER)
    sel(page,['input[name="password"]','input[type="password"]'])[0].fill(PW)
    sel(page,['button:has-text("SUBMIT")','button[type="submit"]'])[0].click(); page.wait_for_timeout(2500)
    page.goto('https://nuba.grid-code.tech/admin-zone/activation-codes'); page.wait_for_timeout(2500)
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(500)
    fixed=page.evaluate('''() => {
      const els=[...document.querySelectorAll('*')];
      return els.map(el=>{const cs=getComputedStyle(el); const r=el.getBoundingClientRect(); return {tag:el.tagName.toLowerCase(),cls:el.className||'',id:el.id||'',text:(el.innerText||'').trim().slice(0,30),pos:cs.position,bottom:cs.bottom,right:cs.right,left:cs.left,top:cs.top,w:r.width,h:r.height,x:r.x,y:r.y,role:el.getAttribute('role')};})
      .filter(x=>x.pos==='fixed' && x.w>10 && x.h>10)
      .sort((a,b)=>(b.y-a.y)||(b.x-a.x)).slice(0,40)
    }''')
    print('FIXED',len(fixed))
    for f in fixed: print(f)
    plus=page.locator('div.fixed.right-0.bottom-0.rounded-full').first
    if plus.count()>0:
      plus.click(); page.wait_for_timeout(1200)
      print('PLUS_CLICKED')
    else:
      print('PLUS_NOT_FOUND')

    counts = page.evaluate('''() => ({
      inputs: document.querySelectorAll('input').length,
      textareas: document.querySelectorAll('textarea').length,
      selects: document.querySelectorAll('select').length,
      dialogs: document.querySelectorAll('[role="dialog"], .modal, [class*="modal"]').length,
    })''')
    print('COUNTS_AFTER', counts)

    fields = page.evaluate('''() => {
      const out=[];
      document.querySelectorAll('input,textarea,select').forEach(el=>{
        out.push({tag:el.tagName.toLowerCase(),type:el.type||null,name:el.name||null,id:el.id||null,placeholder:el.placeholder||null});
      });
      return out;
    }''')
    print('FIELDS_AFTER', fields)

    buttons = page.evaluate('''() => Array.from(document.querySelectorAll('button')).map(b=>({text:(b.innerText||'').trim(),aria:b.getAttribute('aria-label'),title:b.getAttribute('title')})).filter(x=>x.text||x.aria||x.title)''')
    print('BUTTONS_AFTER', buttons[:80])

    page.screenshot(path='out/nuba_plus_probe.png',full_page=True)
    c.close(); b.close()
