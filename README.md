# distribute_tweet_per_lang

A toy program for heavy Twitter users (ツイ廃) who speak multiple languages. This program tries to detect which language you tweeted in one (source) account, and distribute that tweet to respective language if defined.

## Usage
```
usage: distribute_tweet_per_lang.py [-h] [-l JSON_with_lang_expressions] [-v]
                                    [-i] [-d]
                                    config_file

Detect the language of latest tweet(s) and distribute to appropriate (and
separate) account.

positional arguments:
  config_file           Name of the JSON file with required configurations.

optional arguments:
  -h, --help            show this help message and exit
  -l JSON_with_lang_expressions, --lang JSON_with_lang_expressions
                        Name of the JSON file with expressions for different
                        languages
  -v, --verbose
  -i, --init            Simply store the latest tweet ID, no forwarding
  -d, --dry             Dry run, do not actually post the tweets
```


