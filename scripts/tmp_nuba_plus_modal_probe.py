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
    u,_=sel_try(page,['input[name="username"]','input[name="email"]','input[type="email"]'])
    p,_=sel_try(page,['input[name="password"]','input[type="password"]'])
    sbtn,_=sel_try(page,['button:has-text("SUBMIT")','button[type="submit"]'])
    if not (u and p and sbtn):
        raise RuntimeError('login selectors not found')
    u.fill(USER)
    p.fill(PW)
    sbtn.click(); page.wait_for_timeout(2500)
    adm,_=sel_try(page,['a:has-text("ADMIN ZONE")','a:has-text("Administration")','a:has-text("Admin")'])
    if adm:
        adm.click(); page.wait_for_timeout(1200)
    acttab,_=sel_try(page,['button:has-text("Activation Codes")','a:has-text("Activation Codes")'])
    if not acttab:
        raise RuntimeError('activation codes tab not found')
    acttab.click(); page.wait_for_timeout(1400)

    plus, s = sel_try(page,['button:has-text("+")','button.rounded-full','button[aria-label="Add"]'])
    print('PLUS_SELECTOR', s)
    if plus:
        plus.click(); page.wait_for_timeout(1200)

    print('CURRENT_URL', page.url)
    print('BUTTONS AFTER PLUS:')
    for btt in page.query_selector_all('button')[:200]:
        t=btt.inner_text().strip()
        aria=btt.get_attribute('aria-label')
        title=btt.get_attribute('title')
        if t or aria or title:
            print('-', repr(t), 'aria=',repr(aria), 'title=',repr(title))
    print('INPUTS AFTER PLUS:')
    for i in page.query_selector_all('input')[:200]:
        print('-', i.get_attribute('type'), i.get_attribute('name'), i.get_attribute('id'), i.get_attribute('placeholder'))
    print('TEXTAREAS AFTER PLUS:')
    for t in page.query_selector_all('textarea')[:200]:
        print('-', t.get_attribute('name'), t.get_attribute('id'), t.get_attribute('placeholder'))
    print('SELECTS AFTER PLUS:')
    for s in page.query_selector_all('select')[:200]:
        print('-', s.get_attribute('name'), s.get_attribute('id'))

    c.close(); b.close()
