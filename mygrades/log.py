file = open('myon.txt').read()
from bs4 import BeautifulSoup


soup = BeautifulSoup(file,'html.parser')

trs = soup.find_all("tr")
for tr in trs:
    fname =tr.find_all('a')[0].text.strip()
    lname = tr.find_all('a')[1].text.strip()
    previous = tr.find('div',attrs={'class':'pc-previous-label'}).text.strip()
    print(fname,lname,previous)