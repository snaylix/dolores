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


def get_show_links_wiki(shows):
    '''
    Request wikipedia links for all TV Shows

    Parameters:
    shows = list of strings

    Returns:
    dictionary = dictionary
    '''

    dictionary = {}
    url = 'https://en.wikipedia.org/wiki/List_of_serial_drama_television_series'
    response = requests.get(url)
    html = response.text
    with open('_RES/data/wikipedia_overview_html.txt', 'w') as text_file:
        print(html, file=text_file)
    for show in shows:
        pattern = f'(?i)\/wiki\/{show}(?:_\(tv_series\))?'
        dictionary[show] = 'https://en.wikipedia.org'\
                           + re.findall(pattern, html)[0]
    return dictionary


def get_show_links_imdb(shows):
    '''
    Request imdb links for all TV Shows

    Parameters:
    shows = list of strings

    Returns:
    dictionary = dictionary
    '''

    dictionary = {}
    url = 'https://www.imdb.com/chart/toptv'
    response = requests.get(url)
    html = response.text
    with open('_RES/data/imdb_overview_html.txt', 'w') as text_file:
        print(html, file=text_file)
    for index, show in enumerate(shows):
        show = show.replace('_', ' ')
        print(show)
        pattern = f'<a href="\/title(.+)"\ntitle=".+" >{show}'
        if show == 'The Sopranos':
            pattern = f'<a href="\/title(.+)"\ntitle=".+" >Die Sopranos'
        show = show.replace(' ', '_')
        dictionary[show] = 'https://www.imdb.com/title'\
                           + re.findall(pattern, html)[0]
    return dictionary


def make_soup(link_to_show):
    '''
    Request Wikipedia page of TV Show and saves it into BeautifulSoup object

    Parameters:
    link_to_show = string

    Returns:
    soup = BeautifulSoup object
    '''

    response = requests.get(link_to_show)
    html = response.text
    soup = BeautifulSoup(html, features='lxml')
    return soup


def build_show_df(soup, show_index, show, df):
    '''
    takes Beautiful Soup object, adds info for TV show to shows_df

    Parameters:
    show = BeautifulSoup object

    Returns:
    df = dataframe
    '''

    title = soup.body.find(class_='summary').text
    genre = soup.body.find(class_='category').text
    cast = soup.body.find(class_='attendee').text
    link_wiki = SHOW_LINKS_WIKI[show]
    link_imdb = SHOW_LINKS_IMDB[show]
    df = df.append({'title': title,
                    'genre': genre,
                    'cast': cast,
                    'link_wiki': link_wiki,
                    'link_imdb': link_imdb
                    }, ignore_index=True)
    return df


TV_SHOWS = [
            'The Wire',
            'The Sopranos',
            'Breaking Bad',
            'Game of Thrones',
            'Fargo',
            'Twin Peaks',
            'Mad Men',
            'Deadwood',
            'Six Feet Under',
            'True Detective',
            'House'
            ]
TV_SHOWS_UNDERSCORE = format_show_names(TV_SHOWS)
SHOW_LINKS_WIKI = get_show_links_wiki(TV_SHOWS_UNDERSCORE)
SHOW_LINKS_IMDB = get_show_links_imdb(TV_SHOWS_UNDERSCORE)
SHOW_INDEX = 0
SHOW_DF = pd.DataFrame()
for (show, show_link) in SHOW_LINKS_WIKI.items():
    directory_path = f'_RES/data/{show}'
    file_name = f'{directory_path}/{show}_show.csv'
    soup = make_soup(show_link)
    SHOW_DF = build_show_df(soup, SHOW_INDEX, show, SHOW_DF)
    SHOW_INDEX += 1
SHOW_DF.head()
SHOW_DF.to_csv('_RES/data/Dolores_TV_Shows.csv', encoding='utf-8')
