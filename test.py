import requests
from bs4 import BeautifulSoup
import pandas as pd

res = requests.get('https://jp.residentadvisor.net/reviews.aspx?format=single')
soup = BeautifulSoup(res.text, 'html.parser')
text = [i.get_text() for i in soup.select('h1')]
print(text)

text = pd.Series(text)
print(text)

drop_idx = [0, 1]
text = text.drop(drop_idx)

album = pd.Series()
cols = ['col1', 'col2']
df = pd.DataFrame(index=[], columns=list('AB'))

b = len(text.index)
b = b//2 -1
for i in range(0,b,2):
    tmp = pd.Series([text.iloc[i],text.iloc[i+1]], index = df.columns)
    df =  df.append(tmp, ignore_index=True)

    b = len(text.index)