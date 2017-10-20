#!/usr/bin/env python
import sys
import re
import requests
import subprocess
import argparse

re_link_pl = re.compile(
    r'.*?hotstar\.com/tv/(?!/).*/[0-9].*/episodes/([0-9].*)/[0-9].*')
re_link_se = re.compile(
    r'.*?hotstar.com/tv/(?!/).*?/([0-9].*)/seasons/season-([0-9]+)')


def get_playlist_links(playlist_id):
    url = 'http://search.hotstar.com/AVS/besc?action=SearchContents&appVersi' \
          'on=5.0.40&channel=PCTV&maxResult=10000&moreFilters=series:'\
          + playlist_id \
          + '%3B&query=*&searchOrder=last_broadcast_date+desc,year+desc,titl' \
            'e+asc&startIndex=0&type=EPISODE'
    request = requests.get(url)
    request.raise_for_status()
    json_obj = request.json()
    if json_obj['resultCode'] != 'OK':
        return []
    return ['http://www.hotstar.com/%s' % x['contentId']
            for x in json_obj['resultObj']['response']['docs']]


def get_season_links(season):
    url = 'http://account.hotstar.com/AVS/besc?action=GetArrayContentList&a' \
          'ppVersion=5.0.40&categoryId=' + str(season) + '&channel=PCTV'
    request = requests.get(url)
    request.raise_for_status()
    json_obj = request.json()
    ep = []
    for x in json_obj['resultObj']['contentList']:
        y = x['episodeNumber']
        ep.append(y)
    return [['http://www.hotstar.com/%s' % x['contentId']
            for x in json_obj['resultObj']['contentList']], ep]


def download_by_number(link, episode):
    print('Downloading Episode : ' + str(episode))
    command = 'youtube-dl -o ' + "Episode-" + str(episode) + " " + link
    subprocess.call(command, shell=True)


def download_by_title(link):
    print('Downloading ' + link)
    command = 'youtube-dl ' + link
    subprocess.call(command, shell=True)


def download_many(links, ep):
    for i in range(len(links)):
        if(args['save'] == 'number'):
            download_by_number(links[i], ep[i])
        else:
            download_by_title(links[i])


def get_season(series, offset):
    url = 'https://account.hotstar.com/AVS/besc?action=GetCatalogueTree&appV' \
          'ersion=5.0.40&categoryId=%s&channel=PCTV' % series
    resp = requests.get(url)
    data = resp.json()
    cat_list = data['resultObj']['categoryList'][0]['categoryList']
    season_obj = cat_list[offset]
    return int(season_obj['categoryId'])


def main():
    
    parser = argparse.ArgumentParser(description='Hotstar Downloader Usage')
    parser.add_argument('-s','--save', help='Save video by title or number.[default is title]', default='title', choices=['title', 'number'])
    parser.add_argument('-u','--url', help='provide url of playlist or season', required=True)
    
    global args
    args = vars(parser.parse_args())

    link = args['url']
    links = []
    ep = []
    match_se = re_link_se.match(link)
    if match_se:
        series, offset = map(int, match_se.groups())
        try:
            final_season = get_season(series, offset)
        except IndexError:
            final_season = series + offset - 1
        result = get_season_links(final_season)
        links += result[0]
        ep += result[1]

    match_pl = re_link_pl.match(link)
    if match_pl:
        playlist_id = match_pl.groups()[0]
        links += get_playlist_links(playlist_id)
    if not links:
        print('Not a season or playlist, trying to download the link directly.')
        download(link)
    else:
        download_many(links, ep)


if __name__ == '__main__':
    main()
