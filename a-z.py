#%%
import requests
import os 
import json
import bs4
import pandas as pd
#%%
r = requests.get('https://www.cancer.gov/about-cancer/treatment/drugs')
soup = bs4.BeautifulSoup(r.content, 'lxml')
#%%
df = pd.DataFrame(columns=['drug', 'link'])
a_z = soup.find_all('ul', 'no-bullets')
for alpha in a_z:
    drugs = alpha.find_all('li')
    for drug in drugs:
        drug = drug.find('a')
        if drug is not None:
            df = df.append(pd.DataFrame({'drug': [drug.text.replace('"', '')], 'link': [drug['href']]}), ignore_index=True)
df.to_csv('drug_list.csv', index=False)
# %%
