from playwright.sync_api import sync_playwright

URL='https://nuba.grid-code.tech'
USER='Laia@grid-code.tech'
PW='elsaltodelpapu'

def sel_try(page, selectors):
    for s in selectors:
        loc=page.locator(s).first
        if loc.count()>0:
            return loc,s
    return None,None

with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    c=b.new_context()
    page=c.new_page(); page.set_default_timeout(30000)
    page.goto(URL); page.wait_for_timeout(8000)
    sel_try(page,['input[name="username"]','input[name="email"]','input[type="email"]'])[0].fill(USER)
    sel_try(page,['input[name="password"]','input[type="password"]'])[0].fill(PW)
    sel_try(page,['button:has-text("SUBMIT")','button[type="submit"]'])[0].click(); page.wait_for_timeout(2500)
    adm,_=sel_try(page,['a:has-text("ADMIN ZONE")','a:has-text("Administration")','a:has-text("Admin")'])
    if adm: adm.click(); page.wait_for_timeout(1200)
    acttab,_=sel_try(page,['button:has-text("Activation Codes")','a:has-text("Activation Codes")'])
    acttab.click(); page.wait_for_timeout(1400)

    info = page.evaluate('''() => {
      const btns = Array.from(document.querySelectorAll('button'));
      return btns.map((b,idx) => {
        const r = b.getBoundingClientRect();
        return {
          idx,
          text:(b.innerText||'').trim(),
          aria:b.getAttribute('aria-label'),
          title:b.getAttribute('title'),
          cls:b.className,
          x:r.x,y:r.y,w:r.width,h:r.height,
          visible: !!(r.width>0 && r.height>0)
        }
      }).filter(x=>x.visible).sort((a,b)=> (b.y-a.y) || (b.x-a.x));
    }''')
    print('VISIBLE_BUTTONS',len(info))
    for row in info[:20]:
      print(row)

    # click bottom-right visible button
    if info:
      target = info[0]
      print('CLICKING_IDX',target['idx'])
      page.evaluate('(idx)=>document.querySelectorAll("button")[idx].click()', target['idx'])
      page.wait_for_timeout(1200)
      print('AFTER_CLICK_URL', page.url)
      counts = page.evaluate('''() => ({
        inputs: document.querySelectorAll('input').length,
        textareas: document.querySelectorAll('textarea').length,
        selects: document.querySelectorAll('select').length,
        dialogs: document.querySelectorAll('[role="dialog"], .modal, [class*="modal"]').length,
      })''')
      print('COUNTS', counts)
      # print field metadata
      fields = page.evaluate('''() => {
        const out=[];
        document.querySelectorAll('input,textarea,select').forEach(el=>{
          out.push({tag:el.tagName.toLowerCase(),type:el.type||null,name:el.name||null,id:el.id||null,placeholder:el.placeholder||null});
        });
        return out;
      }''')
      print('FIELDS', fields[:80])

    c.close(); b.close()
