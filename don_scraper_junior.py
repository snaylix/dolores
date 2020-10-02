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


def get_imdb_season_data(show):
    '''
    Request imdb links for all TV Shows

    Parameters:
    shows = list of strings

    Returns:
    df = pandas DataFrame
    '''

    global DF_ALL_EPISODES
    file = open(f'_RES/data/{show}/{show}_imdb_links.txt', 'r')
    urls = file.readlines()
    file.close()
    dictionary = {'episode_no': [], 'title': [], 'imdb_rating': [], 'season': [], 'airdate': []}
    for index, url in enumerate(urls):
        episode_number = 1
        url = url.strip()
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, features='lxml')
        season = index + 1
        with open(f'_RES/data/{show}/{show}_imdb_season{season}_html.txt', 'w') as text_file:
            print(html, file=text_file)
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
            dictionary['imdb_rating'].append(rating)
        for airdate in soup.find_all("div", class_="airdate"):
            dictionary['airdate'].append(airdate.text.replace('\n            ', '').replace('\n    ', ''))
        missing_values = len(dictionary["episode_no"]) - len(dictionary["imdb_rating"])
        print(f'ratings NaNs in season {season}: {missing_values}')
        for i in range(missing_values):
            dictionary['imdb_rating'].append('NaN')
    print('HTML saved')
    df = pd.DataFrame.from_dict(dictionary)
    for key in dictionary:
        print(f'{len(dictionary[key])}/{len(df.index)} {key} data')
    df.to_csv(f'_RES/data/{show}/{show}_Episodes.csv', encoding='utf-8')
    return df


def get_wiki_season_links(show, df):
    '''
    Request wikipedia links for show's seasons

    Parameters:
    show = strings
    df = pandas DataFrame

    Returns:
    -
    '''

    file = open(f'_RES/data/{show}/{show}_wiki_html.txt', 'r')
    html = file.read()
    file.close()
    number_of_seasons = df['season'].max()
    print(f'{number_of_seasons} seasons in total')
    with open(f'_RES/data/{show}/{show}_wiki_links.txt', 'w') as text_file:
        for i in range(1, number_of_seasons+1):
            pattern = f'href="(\/wiki\/{show}_\(season_{i}\))"'
            if re.findall(pattern, html) != []:
                print('https://en.wikipedia.org' + re.findall(pattern, html)[0], file=text_file)


def get_wiki_season_data(show):
    '''
    Request imdb links for all TV Shows

    Parameters:
    shows = list of strings

    Returns:
    -
    '''

    global DF_ALL_EPISODES
    file = open(f'_RES/data/{show}/{show}_wiki_links.txt', 'r')
    urls = file.readlines()
    file.close()
    if (urls != []) and (len(urls) != 1):
        print('working with indidvidual season pages')
        list_of_seasons = False
    else:
        urls = [f'https://en.wikipedia.org/wiki/List_of_{show}_episodes']
        print('working with list of seasons')
        list_of_seasons = True
    dictionary = {'viewers': []}
    for index, url in enumerate(urls):
        url = url.strip()
        response = requests.get(url)
        html = response.text
        season = index + 1
        with open(f'_RES/data/{show}/{show}_wiki_season{season}_html.txt', 'w') as text_file:
            print(html, file=text_file)
        soup = BeautifulSoup(html, features='lxml')
        for soup in soup.find_all("tr", class_="vevent"):
            pattern_viewer = 'style="text-align:center">(\d+.\d+)<sup'
            viewer_per_episode = re.findall(pattern_viewer, str(soup))
            pattern_viewer = 'Movie'
            is_movie = re.findall(pattern_viewer, str(soup))
            pattern_viewer = '>\d+<hr'
            is_split_episode = re.findall(pattern_viewer, str(soup))
            if (viewer_per_episode != []) and (is_movie == []):
                dictionary['viewers'].append(viewer_per_episode[0])
                if is_split_episode != []:
                    dictionary['viewers'].append(viewer_per_episode[0])
            elif list_of_seasons is True:
                pattern_viewer_los_nan = '>N\/A<'
                viewer_per_episode = re.findall(pattern_viewer_los_nan, str(soup))
                if (viewer_per_episode != []) and (is_movie == []):
                    dictionary['viewers'].append('NaN')
            else:
                dictionary['viewers'].append('NaN')
    df = pd.read_csv(f'_RES/data/{show}/{show}_Episodes.csv', index_col=0)
    print(f'Viewer data for {len(dictionary["viewers"])} / {len(df.index)} episodes')
    df['viewers'] = dictionary['viewers']
    df['show_title'] = show.replace('_', ' ')
    df.to_csv(f'_RES/data/{show}/{show}_Episodes.csv', encoding='utf-8')
    print(f'DataFrame for {show} saved')
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
            'House',
            'Dexter'
            ]


TV_SHOWS_UNDERSCORE = format_show_names(TV_SHOWS)
DF_ALL_EPISODES = pd.DataFrame(columns=['episode_no', 'title', 'imdb_rating', 'season', 'airdate', 'viewers', 'show_title'])
for show in TV_SHOWS_UNDERSCORE:
    print(f'~~// {show} \\\~~')
    DF_SHOW = get_imdb_season_data(show)
    get_wiki_season_links(show, DF_SHOW)
    DF_SHOW = get_wiki_season_data(show)
    DF_ALL_EPISODES = DF_ALL_EPISODES.append(DF_SHOW, ignore_index=True)
    print()
DF_ALL_EPISODES.to_csv('_RES/data/Dolores_All_Episodes.csv', encoding='utf-8')
