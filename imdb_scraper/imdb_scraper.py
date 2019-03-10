# -*- coding: utf-8 -*-
import sys
import os
from os.path import join
import requests
from lxml import html
import json

# Dir paths
WORKING_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = join(WORKING_DIR, 'files')

# File paths
MOVIES_PATH = join(FILES_DIR, 'movies.json')


class IDBM_urls:
    def __init__(self):
        """ Class to deal with the IDBM site urls
            while navigating through the movie searchs
        """
        self.main_url = 'https://www.imdb.com'
        self.first_search = self.main_url + '/search/title?count=250&start=1&title_type=feature&ref_=nv_wl_img_2'

    def join(self, append_url):
        """ Joins the append_url to the main url

            Returns a url string.
        """
        return self.main_url + append_url


def run():
    idbm = IDBM_urls()
    url = idbm.first_search

    movies_links = []

    while True:
        page = requests.get(url)
        results_page = html.fromstring(page.content)
        movies_links += results_page.xpath('//h3[@class="lister-item-header"]/a[starts-with(@href, "/title/")]/@href')

        next_page = results_page.xpath('//a[@class="lister-page-next ' +
                                       'next-page"]/@href')

        if not next_page or len(movies_links) >= 5000:
            break

        url = idbm.join(next_page[0])

    # Navigate through every movie link to get it's details
    movies = []
    for movie_link in movies_links:
        movie = {}
        movie_url = idbm.join(movie_link)
        movie_page = requests.get(movie_url)
        movie_html = html.fromstring(movie_page.content)

        title = movie_html.xpath('//div[@class="titleBar"]/div[@class="title_wrapper"]/h1/text()')
        title = title[0].replace('\xa0', '') if title else None
        originalTitle = movie_html.xpath('//div[@class="titleBar"]/div[@class="title_wrapper"]/div[@class="originalTitle"]/text()')
        originalTitle = originalTitle[0] if originalTitle else None
        userRating = movie_html.xpath('//span[@itemprop="ratingValue"]/text()')
        userRating = float(userRating[0]) if userRating else None
        directors_links = movie_html.xpath('//div[@class="credit_summary_item"][1]/a[contains(@href, "/name/")]/@href')
        movieDurationMinutes = movie_html.xpath('//div[@id="titleDetails"]/div[@class="txt-block"]/time/text()')
        movieDurationMinutes = movieDurationMinutes[0].replace(' min', '') if movieDurationMinutes else None
        genres = movie_html.xpath('//h4[@class="inline" and contains(text(), "Genre")]/following-sibling::a/text()')
        budget = movie_html.xpath('//div[@class="txt-block" and ./h4[@class="inline" and contains(text(), "Budget")]]/text()')
        budget = budget[1].replace(' ', '').replace('\n', '').replace(',', '') if budget else None

        # Get the directors informations
        directors = []
        for director_link in directors_links:
            director = {}
            director_url = idbm.join(director_link)
            director_page = requests.get(director_url)

            director_html = html.fromstring(director_page.content)

            directorName = director_html.xpath('//h1[@class="header"]/span[@class="itemprop"]/text()')[0]
            directorBio = ', '.join(director_html.xpath('//div[@id="name-bio-text"]/div[@class="name-trivia-bio-text"]/div[@class="inline"]/text()'))
            if ' HE ' in directorBio.upper() or ' HIS ' in directorBio.upper():
                directorGender = 'man'
            elif ' SHE ' in directorBio.upper() or ' HERS ' in directorBio.upper() or ' HER ' in directorBio.upper():
                directorGender = 'woman'
            else:
                directorGender = 'unknown'
            directorBirthPlace = director_html.xpath('//div[@id="name-born-info"]/a[contains(@href, "birth_place")]/text()')
            directorBirthPlace = directorBirthPlace[0] if directorBirthPlace else None

            # Build Director dictionary
            director['name'] = directorName
            director['gender'] = directorGender
            director['birth_place'] = directorBirthPlace

            directors.append(director)

        # Build movie dictionary
        movie['title'] = title
        movie['original_title'] = originalTitle
        movie['user_rating'] = userRating
        movie['duration_minutes'] = movieDurationMinutes
        movie['genre'] = genres
        movie['budget'] = budget
        movie['directors'] = directors

        movies.append(movie)

    # Write json file with the movies.
    with open(MOVIES_PATH, 'w', encoding='utf-8') as file:
        json.dump(movies, file, ensure_ascii=False)

    print('finite')

if __name__ == "__main__":
    run()
