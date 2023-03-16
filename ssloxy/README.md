## Минимальный вариант SSL/TLS termination proxy

```
usage: ssloxy.py [-h] [-a ADDR] [-p PORT] [-b BADDR] [-s BPORT] [-t] command

Simple SSL/TLS termination proxy to single backend non-SSL service

positional arguments:
  command               start|stop

options:
  -h, --help            show this help message and exit
  -a ADDR, --addr ADDR  SSL proxy host (dafault: localhost)
  -p PORT, --port PORT  SSL proxy port (dafault: 8443)
  -b BADDR, --baddr BADDR
                        Backend host (dafault: localhost)
  -s BPORT, --bport BPORT
                        Backend port (dafault: 8000)
  -t, --test            Use self-signed certificate from ./cert
```

По два потока на каждого клиента: один читает из клиента и пишет в бэкенд-сервис, другой читает из бэкенд-сервиса и пишет в клиента.


1. Тестовый сертификат
```
openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout ./cert/server.key -out ./cert/server.crt
```

2. Запуск прокси
```
python ssloxy.py start -t > /dev/null 2>&1 &
```

3. В разных консолях:
- сервис бэкенда
```
$ ncat -lk localhost 8000
```
- сервис клиента
```
$ openssl s_client -connect localhost:8443
...
> hello
```
или 
```
$ ncat --ssl localhost 8443
> hello
```
4. Остановка прокси
```
python ssloxy.py stop -t
```
