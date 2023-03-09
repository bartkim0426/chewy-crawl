import os
from http import HTTPStatus
from datetime import datetime

import httpx
from bs4 import BeautifulSoup


SLACK_HOOK_URL = os.environ('SLACK_HOOK_URL')


PRODUCTS: dict = {
    # Should add item number and title
    # '138371': 'Beef 6.5oz',
    # '178629': 'Chicken 6.5oz',
    # '141896': 'Lamb 6.5oz',
    # '184249': 'Mackerel 6.5oz',
    # '141898': 'Mackerel & Lamb 6.5oz',
    # '138370': 'Rabbit & Lamb 6.5oz',
    # '141895': 'Vension 6.5oz',
    # '322199': 'Garfield litter (purple)',
    # '147769': 'Garfield litter (green)',
}


def send_slack_message(message):
    message = {'text': message}
    httpx.post(SLACK_HOOK_URL, json=message, headers={'Content-Type': 'application/json'})


def crawl_page(url: str) -> str:
    print(f'start crawl page: {url}')
    res = httpx.get(url, headers={
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    })
    while res.status_code == HTTPStatus.MOVED_PERMANENTLY:
        next_url = str(res.next_request.url)
        print(f'move to nexd redirecdt: {next_url}')
        res = httpx.get(next_url, headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        })
    return res.content


def crawl_chewy_page(url):
    html_doc = crawl_page(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup


def is_in_stock(soup) -> bool:
    # in stock: strong -> In Stock
    # out of stock: <strong class="styles_header__qQtUY">Temporarily Out of Stock</strong>
    text = soup.find('strong').text
    if text == 'In Stock':
        return True
    if text == 'Temporarily Out of Stock':
        return False
    return False


def get_price(soup) -> str:
    # <div role="text" data-testid="advertised-price" class="kib-product-price kib-product-price--lg">$78.12<span class="kib-product-price__label">Chewy Price</span></div>
    price = soup.find('div', class_='kib-product-price').contents[0][:6]
    return price


def get_prev_history() -> str:
    '''read history.log file and return prev history'''
    with open('./history.log', 'r') as f:
        content = f.read()
    return content


def write_history(messages: str):
    with open('./history.log', 'w') as f:
        f.write(messages)


def crawl_chewy():
    base_url = 'https://www.chewy.com/dp'
    messages = ''

    for product_id, product_name in PRODUCTS.items(): 
        url = f'{base_url}/{product_id}'
        soup = crawl_chewy_page(url)
        is_stock = is_in_stock(soup)
        print(f'{product_name} in stock: {is_stock}')
        if is_stock:
            price = get_price(soup)
            print(f'{product_name} price: {price}')
            messages += f'''
product name: {product_name}
price: {price}

'''
    if messages:

        prev_messages = get_prev_history()
        # send slack message only different from prev message
        if prev_messages != messages:
            send_slack_message(messages)
            # update message
            write_history(messages)


if __name__ == '__main__':
    print(f'executed: {datetime.now()}')
    crawl_chewy()
