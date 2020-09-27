import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os


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
        if show == 'The Sopranos':
            pattern = f'<a href="\/title(.+)"\ntitle=".+" >Die Sopranos'
        elif show == 'House':
            pattern = f'<a href="\/title(.+)"\ntitle=".+" >House'
        else:
            pattern = f'<a href="\/title(.+)"\ntitle=".+" >{show}'
        show = show.replace(' ', '_')
        if show == 'Twin_Peaks':
            print(re.findall(pattern, html)[0])
        dictionary[show] = 'https://www.imdb.com/title'\
                           + re.findall(pattern, html)[0]
    return dictionary


def make_soup(show, link_to_show):
    '''
    Request Wikipedia page of TV Show and saves it into BeautifulSoup object

    Parameters:
    link_to_show = string

    Returns:
    soup = BeautifulSoup object
    '''

    response = requests.get(link_to_show)
    html = response.text
    if not os.path.exists(f'_RES/data/{show}'):
        os.makedirs(f'_RES/data/{show}')
    if 'imdb' in link_to_show:
        with open(f'_RES/data/{show}/{show}_imdb_html.txt', 'w') as text_file:
            print(html, file=text_file)
    if 'wiki' in link_to_show:
        with open(f'_RES/data/{show}/{show}_wiki_html.txt', 'w') as text_file:
            print(html, file=text_file)
    soup = BeautifulSoup(html, features='lxml')
    return soup


def build_show_df(soup, show_index, show, df):
    '''
    takes Beautiful Soup object, adds wikipedia info for TV show to shows_df

    Parameters:
    show = BeautifulSoup object

    Returns:
    df = dataframe
    '''


    title = soup.body.find(class_='summary').text
    genre = soup.body.find(class_='category').text
    genre = genre.replace('\n', ';')
    cast = soup.body.find(class_='attendee').text
    cast = cast.replace('\n', ';')
    link_wiki = SHOW_LINKS_WIKI[show]
    df.loc[show_index, 'title'] = title
    df.loc[show_index, 'genre'] = genre
    df.loc[show_index, 'cast'] = cast
    df.loc[show_index, 'link_wiki'] = link_wiki
    return df


def build_show_df_imdb(soup, show_index, show, df):
    '''
    takes Beautiful Soup object, adds imdb info for TV show to shows_df

    Parameters:
    show = BeautifulSoup object

    Returns:
    df = dataframe
    '''

    with open(f'_RES/data/{show}/{show}_imdb_links.txt', 'w') as text_file:
        for link in reversed(soup.find_all('a', {'href': re.compile(r'episodes\?season')})):
            print('https://www.imdb.com' + link.get('href'), file=text_file)
    imdb_rating = soup.body.find(class_='ratingValue').text
    imdb_rating = float(imdb_rating.replace('/10', ''))
    link_imdb = SHOW_LINKS_IMDB[show]
    df.loc[show_index, 'imdb_rating'] = imdb_rating
    df.loc[show_index, 'link_imdb'] = link_imdb
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
    soup = make_soup(show, show_link)
    SHOW_DF = build_show_df(soup, SHOW_INDEX, show, SHOW_DF)
    SHOW_INDEX += 1
    print(f'created wiki data for {SHOW_INDEX}/11 ({show})')
SHOW_INDEX = 0
for (show, show_link) in SHOW_LINKS_IMDB.items():
    soup = make_soup(show, show_link)
    SHOW_DF = build_show_df_imdb(soup, SHOW_INDEX, show, SHOW_DF)
    SHOW_INDEX += 1
    print(f'created imdb data for {SHOW_INDEX}/11 ({show})')
print('saving dataframe ...')
SHOW_DF.to_csv('_RES/data/Dolores_TV_Shows.csv', encoding='utf-8')
print('all done')
