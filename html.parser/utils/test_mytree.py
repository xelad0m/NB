"""
Сравнение скорости парсинга HTML
$ python test_mytree.py

Number of parse loops per page:  10
No   Parser                   Total time (s)    Avg time (s)     Memory for tree (Kb)
--------------------------------------------------------------------------------
https://www.youtube.com/
1   mytree (DOM)                   0.105          0.010         2320.8
2   lxml etree (SAX)               0.111          0.011            0.1
3   bs4+lxml (DOM)                 0.215          0.022         2106.1
4   html5lib (SAX)                 0.654          0.065            0.1
https://wikipedia.org/
1   lxml etree (SAX)               0.030          0.003            0.1
2   mytree (DOM)                   0.187          0.019          718.8
3   bs4+lxml (DOM)                 0.343          0.034          193.1
4   html5lib (SAX)                 0.613          0.061            0.1
https://9gag.com/
1   lxml etree (SAX)               0.007          0.001            0.1
2   mytree (DOM)                   0.014          0.001          104.6
3   bs4+lxml (DOM)                 0.032          0.003          132.1
4   html5lib (SAX)                 0.072          0.007            0.1
--------------------------------------------------------------------------------
Total:
1   lxml etree (SAX)               0.148          0.015            0.2
2   mytree (DOM)                   0.306          0.031         3144.2
3   bs4+lxml (DOM)                 0.590          0.059         2431.3
4   html5lib (SAX)                 1.340          0.134            0.4

*) lxml выигрывает т.к. (SAX) 
   - узлы документа не являются поддеревьями
   - ничего не хранится в памяти
**) html5lib - любопытно, чем он занимается столько времени, используя lxml.etree

"""


from mytree import TreeBuilder as tb
from bs4 import BeautifulSoup as bs
from lxml import etree as et

import html5lib

import requests
import time

from pympler import asizeof

N = 10
URLs = ['https://www.youtube.com/', 
        'https://wikipedia.org/',
        'https://9gag.com/']


def _bs(data):
    return bs(data, 'lxml')

parsers = {'bs4+lxml (DOM)': _bs, 'lxml etree (SAX)': et.HTML, 'html5lib (SAX)': html5lib.parse, 'mytree (DOM)': tb}

def evaluate(report):
    for url in URLs:
        headers = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                   'Accept-Encoding': 'identity'}                   # to recieve not compressed html
        try:
            r = requests.get(url=url, headers=headers)
        except:
            print(url, ' - connection problems...')
        if r.status_code == 200:
            for name, parser in parsers.items():
                t = time.perf_counter()
                for i in range(N):
                    etree = parser(r.text)
                m = asizeof.asizeof(etree)
                ts = time.perf_counter()
                report.append({'url': url, 'name': name, 'total': ts - t, 'average': (ts - t) / N, 'memory': m / 1024})
        else:
            for name, parser in parsers.items():
                report.append({'url': url, 'name': name, 'total': 'n/a', 'average': 'n/a', 'memory': 'n/a'})    
        
    return report

def report(report):
    print('Number of parse loops per page: ', N)
    print("No   Parser                   Total time (s)    Avg time (s)     Memory for tree (Kb)")
    print('-'*80)   
    report_template = "{}   {:<20}      {:>10.3f}     {:>10.3f}     {:>10.1f}"
    # total sum
    for parser_name, parser in parsers.items():
        rep_slice = [x for x in report if x['name'] == parser_name]
        report.append({'url': 'Total', 'name': parser_name, 
                       'total': sum([x['total'] for x in rep_slice]), 
                       'average': sum([x['average'] for x in rep_slice]),                                                                          
                       'memory': sum([x['memory'] for x in rep_slice])                                                   
                       })
    # print cases
    for url in URLs:
        print(url)
        for pos, case in enumerate(sorted([x for x in report if x['url'] == url], 
                                          key=lambda x: x.get('total'))):
            print(report_template.format(pos+1, case['name'], case['total'], case['average'], case['memory']))
    # print total
    print('-'*80)
    print('Total:')
    for pos, case in enumerate(sorted([x for x in report if x['url'] == 'Total'], 
                                          key=lambda x: x.get('total'))):
            print(report_template.format(pos+1, case['name'], case['total'], case['average'], case['memory']))


if __name__ == '__main__':

    # Test code
    report(evaluate([]))

    # Profiling code
    
    # import cProfile, pstats, io
    # r = requests.get("https://www.youtube.com/").text
    # for name, parser in parsers.items():
    #     with cProfile.Profile() as pr:
    #         print(name)
    #         pr.enable()
    #         parser(r)
    #         pr.disable()
    #         s = io.StringIO()
    #         sortby = pstats.SortKey.CUMULATIVE  # CALLS PCALLS CUMULATIVE
    #         ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    #         ps.print_stats(10)  # 10% списка
    #         print(s.getvalue())
