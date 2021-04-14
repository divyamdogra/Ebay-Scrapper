import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from multiprocessing import Process, Queue, Pool, Manager
import threading
import sys

startTime = time.time()
qcount = 0
products = []  # List to store name of the product
prices = []  # List to store price of the product
ratings = []  # List to store ratings of the product

links = []
no_pages = 7


def get_data(pageNo, q):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r = requests.get(url + "&_sacat=0&_pgn=" + str(pageNo), headers=headers)  # , proxies=proxies)
    print(r)
    content = r.content
    soup = BeautifulSoup(content)
    # print(soup.encode('utf-8')) # uncomment this in case there is some non UTF-8 character in the content and
    # you get error

    for d in soup.findAll('div', attrs={'class': 's-item__info clearfix'}):
        name = d.find('h3', attrs={'class': 's-item__title'})

        price = d.find('span', attrs={'class': 's-item__price'})
        rating = d.find('span', attrs={'class': 'clipped'})
        links = d.find('a', attrs={'class': 's-item__link'})
        all = []

        if name is not None:
            all.append(name.text)
        else:
            all.append("unknown-product")

        if price is not None:
            all.append(price.text)
        else:
            all.append('$0')

        if rating is not None:
            all.append(rating.text)
        else:
            all.append('-1')

        if links is not None:
            all.append(links.get('href'))
        else:
            all.append('-1')

        q.put(all)
        # print("---------------------------------------------------------------")


results = []
if __name__ == "__main__":
    m = Manager()
    q = m.Queue()  # use this manager Queue instead of multiprocessing Queue as that causes error
    p = {}
    a = []
    url_str = input("Enter the product category you want to search for: ")
    url = []

    # Hacky fix
    words = url_str.split()
    var = len(words)

    if var == 1:
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=" + words[0]
        print(url)
    if var == 2:
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=" + words[0] + "+" + words[1]
        print(url)
    elif var == 3:
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=" + words[0] + "+" + words[1] + "+" + words[2]
        print(url)
    elif var == 4:
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=" + words[0] + "+" + words[1] + "+" + words[2] + "+" + words[3]
        print(url)
    elif var == 5:
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=" + words[0] + "+" + words[1] + "+" + words[2] + "+" + words[3] + "+" + words[
            4]
        print(url)


    for i in range(1, no_pages):

        print("starting thread: ", i)

        p[i] = threading.Thread(target=get_data, args=(i, q))
        p[i].start()

    for i in range(1, no_pages):
        p[i].join()

    while q.empty() is not True:
        qcount = qcount + 1
        queue_top = q.get()
        products.append(queue_top[0])

        prices.append(queue_top[1])
        ratings.append(queue_top[2])
        links.append(queue_top[3])

    print("total time taken: ", str(time.time() - startTime), " qcount: ", qcount)
    # print(q.get())
    df = pd.DataFrame({'Product_Name': products,'Price': prices, 'Ratings': ratings, 'Product_Link': links})
    print(df)
    df.to_csv('products_10.csv', index=False, encoding='utf-8')   #saving csv file

