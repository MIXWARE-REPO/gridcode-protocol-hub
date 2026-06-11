from playwright.sync_api import sync_playwright

url='https://nuba.grid-code.tech'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    c=b.new_context()
    page=c.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(8000)
    print('TITLE', page.title())
    text=page.inner_text('body')
    print('BODY_TEXT_START')
    print(text[:2000])
    print('BODY_TEXT_END')
    inputs=page.query_selector_all('input')
    print('INPUT_COUNT',len(inputs))
    for i,el in enumerate(inputs[:30]):
        print(i, el.get_attribute('type'), el.get_attribute('name'), el.get_attribute('id'), el.get_attribute('placeholder'))
    btns=page.query_selector_all('button')
    print('BUTTON_COUNT',len(btns))
    for i,bn in enumerate(btns[:30]):
        print(i, repr(bn.inner_text()[:120]), bn.get_attribute('type'))
    links=page.query_selector_all('a')
    print('LINK_COUNT',len(links))
    for i,a in enumerate(links[:20]):
        print(i, repr(a.inner_text()[:80]), a.get_attribute('href'))
    c.close(); b.close()
