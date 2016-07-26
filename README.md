# Local Env Setup (vagrant)


```
vagrant box add precise64 http://files.vagrantup.com/precise64.box
```

```
vagrant up --provision
vagrant ssh
//password: vagrant
```

```
$ telnet 192.168.36.12 8181
```


# Own Mac?

## Dependencies:

* Python V >= __2.7

## Server

```
$ python server.py
```

Clients

```
$ telnet 127.0.0.1 8181
```