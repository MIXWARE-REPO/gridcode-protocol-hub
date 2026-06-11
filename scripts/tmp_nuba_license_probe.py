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
    page=c.new_page()
    page.goto(URL, wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(8000)
    u,_=sel_try(page,['input[name="username"]','input[name="email"]','input[type="email"]'])
    pw,_=sel_try(page,['input[name="password"]','input[type="password"]'])
    sb,_=sel_try(page,['button:has-text("SUBMIT")','button[type="submit"]'])
    u.fill(USER); pw.fill(PW); sb.click(); page.wait_for_timeout(2000)

    adm,_=sel_try(page,['a:has-text("Administration")','button:has-text("Administration")','a:has-text("Admin")'])
    if adm: adm.click(); page.wait_for_timeout(1200)

    lic,_=sel_try(page,['a:has-text("Licenses")','button:has-text("Licenses")','a:has-text("Activation")'])
    if lic: lic.click(); page.wait_for_timeout(1200)

    act,_=sel_try(page,['button:has-text("Activation Codes")','a:has-text("Activation Codes")'])
    if act:
        act.click(); page.wait_for_timeout(1200)

    print('TITLE', page.title())
    print('URL', page.url)
    print('BUTTONS:')
    for btt in page.query_selector_all('button')[:120]:
        t=btt.inner_text().strip()
        aria=btt.get_attribute('aria-label')
        title=btt.get_attribute('title')
        cls=btt.get_attribute('class')
        print('-',repr(t), 'aria=',repr(aria), 'title=',repr(title), 'class=',repr((cls or '')[:80]))
    print('INPUTS:')
    for i in page.query_selector_all('input')[:120]:
        print('-', i.get_attribute('type'), i.get_attribute('name'), i.get_attribute('id'), i.get_attribute('placeholder'))
    print('SELECTS:')
    for s in page.query_selector_all('select')[:40]:
        print('-', s.get_attribute('name'), s.get_attribute('id'))
    print('TEXTAREAS:')
    for t in page.query_selector_all('textarea')[:40]:
        print('-', t.get_attribute('name'), t.get_attribute('id'), t.get_attribute('placeholder'))
    print('LINKS:')
    for a in page.query_selector_all('a')[:200]:
        txt=a.inner_text().strip()
        href=a.get_attribute('href')
        aria=a.get_attribute('aria-label')
        if txt or href:
            print('-', repr(txt), 'href=', repr(href), 'aria=', repr(aria))

    c.close(); b.close()
