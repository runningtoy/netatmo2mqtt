# netatmo2mqtt

Get the public weaether measures from  NetAtmo  and send it to your MQTT broker -> based on [https://github.com/seblucas/netatmo2mqtt](https://github.com/seblucas/netatmo2mqtt)

publish to sepearte topics for each value under ```netatmo\``` 

you need to change the coordinates in Line 154 -> ```getNetAtmoPublicWeather(accessToken, lat_ne,lon_ne,lat_sw,lon_sw)```

----------------------------

# Why yet another tool around NetAtmo API

I tried many other open source tools on github but I did not find a perfect fit for me.

The main reason is security : most of the tools I reviewed are still asking for `client_id`, `client_secret` (perfectly normal) but also for your username / password and that's not acceptable for me. It's also forbidden by [NetAtmo guidelines](https://dev.netatmo.com/resources/technical/guides/developerguidelines).

The other reason is that the thermostat is synchronized [only every hour](https://dev.netatmo.com/resources/technical/guides/ratelimits) so simply using [getthermostatsdata](https://dev.netatmo.com/resources/technical/reference/thermostat/getthermostatsdata) was not enough for me (make a graph with a measure every hour is not very precise). So I finally used [getmeasure](https://dev.netatmo.com/resources/technical/reference/common/getmeasure) in addition to provide all the missing detail with a measure every 10 minutes (like on the website).

Update 2019-01-27 : I replaced `getthermostatsdata` (which is being [deprecated](https://dev.netatmo.com/resources/technical/reference/deprecated) by Netatmo) by `homesdata`.

So I build mine :(.

# Usage

## Prerequisite

You simply need Python3 (never tested with Python2.7) and the only dependencies are `requests` (to access the api) and `paho-mqtt` (for MQTT broker interaction) so this line should be enough  :

```bash
pip3 install paho-mqtt requests
```

## Getting your refresh token

First you'll have to [create your app in the NetAtmo website](https://dev.netatmo.com/myaccount/createanapp) and then you can use curl on a server you trust to get your refresh token :

```bash
 curl -d 'grant_type=password&client_id=<CLIENT_ID>&client_secret=<CLIENT_SECRET>&username=<USERNAME>&password=<PASSWORD>&scope=read_thermostat' 'https://api.netatmo.net/oauth2/token'
```

Make sure to add a leading space to this command to avoid keeping this line in your shell history.

About the scope : for this program you only need to be allowed to read thermostat values, you can read the [API documentation](https://dev.netatmo.com/resources/technical/guides/authentication/clientcredentials) if you need anything else.

## Using the script

Easy, first try a dry-run command :

```bash
./netatmo2MQTT.py -c '<CLIENT_ID>' -a '<CLIENT_SECRET>' -r '<REFRESH_TOKEN>' -n -v
```

and then a real command to add to your crontab :

```bash
./netatmo2MQTT.py -c '<CLIENT_ID>' -a '<CLIENT_SECRET>' -r '<REFRESH_TOKEN>'
```

The secrets can also be set with environment variables, see the help for more detail.

## Help

```bash
seb@minus ~/src/netatmo2mqtt (git)-[master] # ./netatmo2MQTT.py --help
usage: netatmo2MQTT.py [-h] -a NACLIENTSECRET -c NACLIENTID -r NAREFRESHTOKEN [-u UPDATEDREFRESHFILENAME] [-t TOPIC] [-T TOPIC] [-v]

Read current temperature and setpoint from NetAtmo API and send them to a MQTT broker.

options:
  -h, --help            show this help message and exit
  -a NACLIENTSECRET, --client-secret NACLIENTSECRET
                        NetAtmo Client Secret / Can also be read from NETATMO_CLIENT_SECRET env var. (default: None)
  -c NACLIENTID, --client-id NACLIENTID
                        NetAtmo Client ID / Can also be read from NETATMO_CLIENT_ID en var. (default: None)
  -r NAREFRESHTOKEN, --refresh-token NAREFRESHTOKEN
                        NetAtmo Refresh Token / Can also be read from NETATMO_REFRESH_TOKEN en var. (default: None)
    -m HOST, --mqtt-host HOST
                        Specify the MQTT host to connect to. (default: 127.0.0.1)
  -n, --dry-run         No data will be sent to the MQTT broker. (default: False)
  -u UPDATEDREFRESHFILENAME, --updated-refresh UPDATEDREFRESHFILENAME
                        The file where the last refresh token coming from NetAtmo API will be saved (default: /tmp/netatmo_last_refresh)
  -t TOPIC, --topic TOPIC
                        The MQTT topic on which to publish the message (if it was a success). (default: sensor/mainroom)
  -T TOPIC, --topic-error TOPIC
                        The MQTT topic on which to publish the message (if it wasn't a success). (default: error/sensor/mainroom)
  -v, --verbose         Enable debug messages. (default: False)
```

## Other things to know

I personaly use cron to start this program 

# License

This program is licenced with GNU GENERAL PUBLIC LICENSE version 3 by Free Software Foundation, Inc.

