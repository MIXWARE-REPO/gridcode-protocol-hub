from playwright.sync_api import sync_playwright
import re
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
    page.goto('https://nuba.grid-code.tech/admin-zone/activation-codes'); page.wait_for_timeout(2000)
    plus=page.locator('div.fixed.right-0.bottom-0.rounded-full.cursor-pointer').first
    plus.click(); page.wait_for_timeout(1200)
    desc=page.locator('input[placeholder*="description" i]').first
    desc.fill('codigo activacion plus auto hermes 20260522')
    # select first option maybe plus? print options
    opts=page.evaluate('''() => Array.from(document.querySelectorAll('select option')).map(o=>({label:o.label,value:o.value,text:o.textContent}))''')
    print('OPTIONS',opts)
    if opts:
        # choose option containing plus
        idx=0
        for i,o in enumerate(opts):
            t=(o.get('label') or o.get('text') or '').lower()
            if 'plus' in t:
                idx=i;break
        page.select_option('select', index=idx)
    page.locator('button:has-text("SAVE")').first.click(); page.wait_for_timeout(2000)
    txt=page.inner_text('body')
    print('BODY_START')
    print(txt[:4000])
    print('BODY_END')
    m=re.findall(r'[a-z]+-[a-z0-9]{8,}(?:-[a-z0-9]+)*',txt,re.I)
    print('CODES',m)
    c.close(); b.close()
