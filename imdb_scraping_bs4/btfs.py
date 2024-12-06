from bs4 import BeautifulSoup
import requests
import pandas as pd

default_url = "https://www.imdb.com/"
def main():
    url = "https://www.imdb.com/search/title/?title_type=feature&user_rating=8,10&num_votes=1000,2147483647&sort=num_votes,desc"
    html = getHtml(url)
    soup = BeautifulSoup(html,'html.parser')
    list = soup.select('.ipc-metadata-list > li',limit=100)
    links = []
    for ele in list:
        a = ele.select('a')
        sub_url = a[0].get('href')
        sub_html = getHtml(default_url+sub_url)
        soup2 = BeautifulSoup(sub_html,'html.parser')
        genres = soup2.select('.ipc-chip.ipc-chip--on-baseAlt > .ipc-chip__text')
        list_genre = [genre.text for genre in genres]

        noteImdb = soup2.select('div[data-testid="hero-rating-bar__aggregate-rating__score"]')[0]
        noteImdb = noteImdb
        [date,annee,duree] = soup2.select('ul.sc-ec65ba05-2.joVhBE > li')
        film = {}
        film['titre'] = soup2.title.text.replace(' - IMDb',"")
        film['date'] = date.text
        film['duree'] = duree.text
        film['note'] = noteImdb.text
        film['genres'] = list_genre
        links.append(film)
        print(film)
    if len(links) > 0:
        make_csv(links)
        
def getHtml(url):
    # Ajouter un User-Agent dans les en-têtes
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        html = response.text
        print(html)
        # soup = BeautifulSoup(html,'html.parser')
        return html
    else:
        print(f"Erreur : {response.status_code}")

def make_csv(obj,filename="default_csv.csv"):

    df = pd.DataFrame(obj)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
main()