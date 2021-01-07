## Elasticsearch v7.x

You can go to Elasticsearch's website and download the appropriate
elastic search.

    https://www.elastic.co/start

Specific instructions for your operating system

+ [Install Elasticsearch on Linux with Debian Package](https://www.elastic.co/guide/en/elasticsearch/reference/current/deb.html)
+ [Installing Elasticsearch on Windows with `.zip`](https://www.elastic.co/guide/en/elasticsearch/reference/current/zip-windows.html)
+ Installing Elasticsearch on macOS with [MacPorts](https://www.macports.org/)
    + `sudo port install elasticsearch`

Elasticsearch can be run locally. By default it runs port 9200 of localhost (e.g. http://localhost:9200/).


### Managing Elasticsearch on Debian/Ubuntu

Elasticsearch is setup up for `systemd`. Beloew are common
`systemctl` commands for working with the elasticsearch service.

If you want manual restart just do `daemon-reload`, then use the 
usual `systemctl` start and stop verbs with elasticsearch.service.

```shell
    sudo systemctl daemon-reload
    sudo systemctl enable elasticsearch.service
```

Checking to see if Elasticsearch is running.

```shell
    sudo systemctl status elasticsearch.service
```

Starting Elasticsearch

```shell
    sudo systemctl start elasticsearch.service
```

Stopping Elasticsearch

```shell
    sudo systemctl stop elasticsearch.service
```

To remove elasticsearch from auto start use the usually systemd
disable.

```shell
    sudo systemctl disable elasticsearch.service
```


### Manage Elasticsearch on macOS with MacPorts

MacPorts includes a version of Elasticsearch that will
work with Observatory.

Installing Elasticsearch server and client. 

```shell
    sudo port install elasticsearch
```

You can manage your Elasticsearch service with the ports command.

If you are using MacPorts you can start elasticsearch
with

```
    sudo port load elasticsearch
```

and stop it with

```
    sudo port unload elasticsearch
```

If you need to restart Elasticsearch you can use the reload option.

```
    sudo port reload elasticsearch
```

