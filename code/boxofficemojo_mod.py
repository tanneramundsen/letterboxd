import requests
from itertools import cycle
from bs4 import BeautifulSoup
import pandas as pd
import pickle

class BoxOfficeMojo(object):

    BASE_URL = "https://www.boxofficemojo.com"
    MOVIE_SEARCH_URLS = "https://www.boxofficemojo.com/search/?q=!!!"
    MOVIE_URLS = "https://www.boxofficemojo.com/movies/alphabetical.htm?letter=!!!&p=.htm"

    def __init__(self, movies_csv='../data/url_cleaned_movies_df.csv'):
        self.df = pd.read_csv(movies_csv)
        self.year_weekend_url = {}
        self.latest = None
        self.letters = ['NUM']
        for i in range(65,91):
            self.letters.append(chr(i))
        self.movie_url = []
        self.movie_earnings = []
        self.crawl_movie_urls()
        self.df.to_csv('movies_earnings.csv',index=False)
    
    def crawl_movie_urls(self):
        search_strings = list(self.df['movie_str_url'])
        for i,search_string in enumerate(search_strings):
            url = self.MOVIE_SEARCH_URLS.replace('!!!', str(search_string))
            print ("working on url: " + str(url))
            try:
                page = requests.get(url, timeout = 5)
                soup = BeautifulSoup(page.content, "html5lib")
                url, earnings = self.get_first_movie_data(soup)
                self.movie_url.append(url)
                self.movie_earnings.append(earnings)
            except:
                url = "N/A"
                earnings = None
                self.movie_url.append(url)
                self.movie_earnings.append(earnings)
            if i % 50 == 0:
                with open('./bom_data.pickle', 'wb') as handle:
                    pickle.dump(zip(self.movie_url,self.movie_earnings), handle)
        with open('./bom_data_final.pickle', 'wb') as handle:
            pickle.dump(zip(self.movie_url,self.movie_earnings), handle)
        self.df['url'] = self.movie_url
        self.df['movie_earnings'] = self.movie_earnings

    def get_first_movie_data(self, html):
        assert isinstance(html, BeautifulSoup)
        titleDivs = html.findAll('div', attrs={'class' : 'a-fixed-left-grid-col a-col-right'})

        final_movie_url = "N/A"
        final_movie_earnings = None
        if len(titleDivs) != 0:
            for div in titleDivs:
                final_movie_url = self.BASE_URL + div.find('a')['href']
                new_page = requests.get(final_movie_url, timeout = 5)
                new_html = BeautifulSoup(new_page.content, "html5lib")
                earnings = new_html.findAll('div', attrs={'class' : 'a-section a-spacing-none mojo-performance-summary-table'})
                if len(earnings) != 0:
                    monies = earnings[0].findAll('span', attrs={"class": "money"})
                    if len(monies) == 3:
                        final_movie_earnings = monies[2].text
                        print(final_movie_earnings)

                break

        return (final_movie_url, final_movie_earnings)         

   