import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


def format_show_names(list_of_shows):
    '''
    Take list of TV Shows and replace spaces with underscores

    Parameters:
    list_of_shows = list of strings

    Returns:
    list_of_shows = list of strings
    '''

    list_of_shows = [show.replace(' ', '_') for show in list_of_shows]
    return list_of_shows


def get_show_links_imdb(show):
    '''
    Request imdb links for all TV Shows

    Parameters:
    shows = list of strings

    Returns:
    dictionary = dictionary
    '''

    file = open(f'_RES/data/{show}/{show}_imdb_links.txt', 'r')
    urls = file.readlines()
    dictionary = {'episode_no':[], 'title':[], 'imdb_rating':[], 'season':[]}
    episode_title_list = []
    episode_rating_list = []
    for index, url in enumerate(urls):
        episode_number = 1
        url = url.strip()
        response = requests.get(url)
        html = response.text
        season = index + 1
        with open(f'_RES/data/{show}/{show}_imdb_season{season}_html.txt', 'w') as text_file:
            print(html, file=text_file)
        print()
        pattern_title = 'itemprop="name">(.+)<\/a>'
        pattern_rating = 'class="ipl-rating-star__rating">(\d\.\d)<\/span>'
        for title in re.findall(pattern_title, html):
            if episode_number > 9:
                dictionary['episode_no'].append(int(str(season) + str(episode_number)))
            else:
                dictionary['episode_no'].append(int(str(season) + '0' + str(episode_number)))
            dictionary['title'].append(title)
            dictionary['season'].append(season)
            episode_number += 1
        for rating in re.findall(pattern_rating, html):
            dictionary['imdb_rating'].append(float(rating))
    print(f'{len(dictionary["episode_no"])}, {len(dictionary["title"])}, {len(dictionary["imdb_rating"])}, {len(dictionary["season"])}')
    df = pd.DataFrame.from_dict(dictionary)
    df.to_csv(f'_RES/data/{show}/{show}_Episodes.csv', encoding='utf-8')


TV_SHOWS = [
            'The Wire',
            'The Sopranos',
            # 'Breaking Bad',
            'Game of Thrones',
            'Fargo',
            'Twin Peaks',
            'Mad Men',
            'Deadwood',
            'Six Feet Under',
            'True Detective',
            # 'House'
            ]

TV_SHOWS_UNDERSCORE = format_show_names(TV_SHOWS)
for show in TV_SHOWS_UNDERSCORE:
    get_show_links_imdb(show)
    print(f'HTML for {show} saved')
