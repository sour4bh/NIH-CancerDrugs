#%%
import pandas as pd
import requests
from requests.exceptions import ConnectionError, RetryError
import os
import re
import bs4
import json
import time
from tqdm import tqdm
import random
#%%
txt = lambda elem: elem.text.replace('\n', '').strip()



def exctract_meta(soup):
    meta = {}
    for m in soup.find_all('div', 'two-columns brand-fda'):
        meta[m.find('div', 'column1').text] = m.find('div', 'column2').text
    return {'meta_data' : meta}

def extract_text(soup):
    content = {'text': []}    
    stack = []
    level = 1
    pointer = content
    prev_elem = None
    
    for elem in soup.children:
        tag = str(elem.name)
        pointer = content
        if re.match('h[2-6]', tag):
            diff = int(tag[-1]) - level
            if diff:
                if diff < 0:
                    for i in range(abs(diff)):
                        stack.pop()
                    stack.pop()
                    stack.append(txt(elem))
                    prev_elem = elem
                if diff > 0:
                    for i in range(abs(diff)):
                        stack.append(txt(elem))
                        prev_elem = elem
                level += diff
            else:
                stack.pop()
                stack.append(txt(elem))

            for point in stack:
                try:
                    pointer = pointer[point]
                except KeyError:
                    pointer[point] = {'text' : []}
                    pointer = pointer[point]

        elif str(type(elem)) == '<class \'bs4.element.Tag\'>' and str(elem.name) == 'p':
            for point in stack:
                pointer = pointer[point]
            pointer['text'].append(txt(elem))
            prev_elem = elem

        elif len(stack) and str(type(elem)) == '<class \'bs4.element.Tag\'>' and str(elem.name) == 'ul':
            for point in stack:
                pointer = pointer[point]
            lis = []
            for li in elem.find_all('li'):
                lis.append(li.get_text().replace('\n', ' '))
            if prev_elem.name == 'p':
                try:
                    pointer['text'].pop()
                except IndexError:
                    pass
                pointer['text'].append({txt(prev_elem) : lis})
            elif prev_elem.name[0] == 'h':
                pointer['text'].append(lis)
            prev_elem = elem
    return content

url = lambda link: 'https://www.cancer.gov' + link
#%%
drugs = pd.read_csv('drug_list.csv')

def get_rand_drug(done, drugs):
    drug, link = drugs.iloc[0]
    choice = 0
    while drug + '.json' in done:
        choice = random.choice(range(len(drugs)))
        drug, link = drugs.iloc[choice]
    return drug, link, choice

while True:
    try:
        done = os.listdir('data/')
        if len(done) == len(drugs):
            print('done')
            break
        else:
            print('Done', len(done), 'out of', len(drugs))
            drug, link, i= get_rand_drug(done, drugs)
            print('choosing', i, ':', drug)
            r = requests.get(url(link))
            soup = bs4.BeautifulSoup(r.content, 'lxml')
            with open(f'data/{drug}.json', 'w') as f:
                content = {**exctract_meta(soup), **extract_text(soup.find('div', 'accordion'))}
                # print(content['text'])
                json.dump(content, f)
                time.sleep(5)
            print('done')
    except (RetryError, ConnectionError):
        print('waiting 30 seconds..')
        time.sleep(30)
        continue
# %%


# %%
