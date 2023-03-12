## ХТМЛ-парсер

На примере парсинга последний событий сайта https://www.python.org/
 
- парсинг bs4
- полурукописный парсер
- парсинг регулярными выражениями

### Установка


    ./install.sh

Добавляет алиас в `~/.bashrc`

В системном питоне должен быть установлен `requests` (как-то так, в зависимости от дистрибутива)

    sudo apt-get install python3-module-requests

### Использование

    ➜  ~ ue
    (mytree html parser)
    Recent events from https://www.python.org/:

            26 Sept. – 28 Sept.  2022 - 9th Conference of Scientific Python Latinamerica (Salta, Argentina)
             30 Sept. – 02 Oct.  2022 - PyConEs - Granada ()
              10 Oct. – 13 Oct.  2022 - PyCon MEA @ Global DevSlam 2022 (Dubai, UAE)
              13 Oct. – 14 Oct.  2022 - PyCon ZA 2022 (Durban, South Africa)
              13 Oct. – 15 Oct.  2022 - PyCon Ghana 2022 (Accra, Ghana)
              14 Oct. – 16 Oct.  2022 - PyCon JP 2022 (Ariake, Koto City, Tokyo 135-0063, Japan)
    ➜  ~ 

### Сравним

Распарсим 10 раз главные страницы youtube, wikipedia, 9gag.

```
➜  python ./utils/test_mytree.py 
...
```

No|Parser|Total time (s)|Avg time (s)|Memory for tree (Kb)
:---|:---|:---:|:---:|:---:
1|lxml etree (SAX)|0.159|0.016|0.2
2|mytree (DOM)|0.298|0.030|3070.7
3|bs4+lxml (DOM)|0.575|0.058|2350.2
4|html5lib (SAX)|1.322|0.132|0.4
