# Upcoming Events from https://www.python.org/events/python-events
import re
import requests
import argparse

URL = 'https://www.python.org/events/python-events'

def get_event_page(debug=False):
    """ Обращается к нужной странице. Возвращает 
    код страницы в формате текста, либо False, если 
    сервер не ответил"""
    
    headers = {'Accept-Encoding': 'identity'}                   # to recieve not compressed html
    r = requests.get(url=URL, headers=headers)
    r.raw.decode_content = True
    if r.status_code == 200:
        if debug:
            print(r.headers, '\n')
        return r.text
    else:
        return False

def parse_event_page(html, parser=0):
    """ Находит и разбирает то место в html коде,
    где содержатся данные о предстоящих событиях.
    По умолчанию используются регулярные выражения. 
    Может также разобрать код внешним парсером bs4 lxml или mytree."""

    # Регулярные выражения для разбора нужного куска кода страницы
    regex = {'table': '<ul class="list-recent-events menu">(?:[\W\w\S\s\na-zA-Z0-9а-яА-ЯёЁ]*?)<\/ul>',  # () - match, with ?: not goes to result
            'event': '<li>([\W\w\S\s\na-zA-Z0-9а-яА-ЯёЁ]*?)</li>',
            'date': '<time datetime="(?:.*?)">(.*?)<span class="say-no-more">(.*?)</span>(.*?)<\/time>',
            'title': '<h3 class="event-title"><a href="(?:.*?)">(.*?)<\/a><\/h3>',              
            'loc': '<span class="event-location">(.*?)</span>'}

    events = []
    
    if parser == 1:
        try:
            from bs4 import BeautifulSoup as bs
        except ModuleNotFoundError as err:
            print('External parser not found (%s), using re...' % err)
            parser=0
        else:
            page = bs(html, 'lxml')
            block = page.find('ul', {'class': 'list-recent-events menu'})
            recs = block.find_all('li')

            events = []
            for rec in recs:
                title = rec.find('h3').text 
                date = rec.find('time').text
                loc = rec.find('span', {'class': 'event-location'}).text
                events.append({'date': date, 'title': title, 'loc':loc})
            print('(bs4 lxlm parser)')

    if parser == 2:
        try:
            from utils.mytree import TreeBuilder as tb
        except ModuleNotFoundError as err:
            print('External parser not found (%s), using re...' % err)
            parser=0
        else:
            page = tb(html)
            block = page.find('ul', {'class': 'list-recent-events menu'})
            recs = block.find_all('li')

            events = []
            for rec in recs:
                title = rec.find('h3').text() 
                date = rec.find('time').text()
                loc = rec.find('span', {'class': 'event-location'}).text()
                events.append({'date': date, 'title': title, 'loc':loc})
            print('(mytree html parser)')

    if parser == 0:
        event_block = re.findall(regex['table'], html)[0]
        for li in re.findall(regex['event'], event_block):
            date = ' '. join( list(map(str.strip, re.findall(regex['date'], li)[0]))).replace(' &ndash; ', '-').strip()
            title = re.findall(regex['title'], li)[0].replace('&amp;', '&').replace('&#39;', "'").strip()
            loc = re.findall(regex['loc'], li)[0]
            events.append({'date': date, 'title': title, 'loc':loc})
        print('(re parser)')
    return events

def print_result(event_list, length=0):
    """ Выводит результат разбора кода страницы в отформатированном виде """

    print('Recent events from https://www.python.org/:\n')
    if length == 0: length = len(event_list)
    for n, e in enumerate(event_list):
        if n == length: break
        print ('{:>35} - {} ({})'.format(e['date'], e['title'], e['loc']))

if __name__ == '__main__':
    """ Обработка аргументов командной строки, запуск приложения с аргументами командной строки """

    argparser = argparse.ArgumentParser(
                        description='Just prints the list of upcoming events from https://www.python.org/.')
    argparser.add_argument('-n', metavar='N', type=int, default=0,
                        help='number of the events to output (default: all)')       # '-n' - means optional arg
    argparser.add_argument('-p', metavar='N', type=int, default=0,
                        help='''1 - use bs4 lxml parser
                                2 - use mytree html parser
                                0 - default no parser, use re''')                           
    argparser.add_argument('-d', action="store_true",                               # 'store_true' - enable type of arg
                        help='additional info about connection')                           

    args = argparser.parse_args()
    events = get_event_page(args.d)
    if events:
        print_result(parse_event_page(events, args.p), args.n)
    else:
        print('connection problems...')