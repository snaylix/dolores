import requests
# from bs4 import BeautifulSoup
import re


def get_show_links(shows):
    """
    Request links for all TV Shows

    Parameters: shows = list of strings
    Returns: all_shows_links = list of strings
    """
    all_shows_links = []
    url = f'https://en.wikipedia.org/wiki/List_of_serial_drama_television_series'
    response = requests.get(url)
    html = response.text
    for show in shows:
        show = show.replace(" ", "_")
        pattern = f'(?i)\/wiki\/{show}(?:_\(tv_series\))?'
        all_shows_links.append('https://en.wikipedia.org/'
                               + re.findall(pattern, html)[0])
    return all_shows_links

def create_show_structure(show, link_to_show):
    """
    loops through all TV shows and creates folders and empty CSVs
    """


TV_SHOWS = [
            'The Wire',
            'The Sopranos',
            'Breaking Bad',
            'Game of Thrones',
            'Fargo',
            'Twin Peaks',
            'The Sopranos',
            'Mad Men',
            'Deadwood',
            'Six Feet Under',
            'True Detective',
            'Lost',
            'House'
            ]

ALL_SHOWS_LINKS = get_show_links(TV_SHOWS)


for id, show in enumerate(TV_SHOWS):
    id += 1
    directory_path = f'_RES/data/{show}'
    file_name = f'{directory_path}/{id}_{show}.csv'
    # soup = make_soup(show)
    # all_links = create_song_list(soup)
    # lyrics = download_songs(all_links)
    # save_all_lyrics_in_file(lyrics)
    # TEXT_CORPUS.append(lyrics)
