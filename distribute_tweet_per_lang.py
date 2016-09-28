# -*- coding: utf-8 -*-

import argparse
import json
import re
import sys

import langdetect
import tweepy


if(__name__ == '__main__'):
    parser = argparse.ArgumentParser(description='Detect the language of latest tweet(s) and distribute to appropriate (and separate) account. ')
    parser.add_argument('config_file', type=str, help="Name of the JSON file with required configurations. ")
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-i', '--init', action="store_true")
    args = parser.parse_args()
    with open(args.config_file, 'r') as fd:
        config_data = json.load(fd)

    CONSUMER_KEY = config_data["consumer_key"]
    CONSUMER_SECRET = config_data["consumer_secret"]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    if(args.verbose):
        print("consumer_key: " + CONSUMER_KEY + "\nconsumer_secret: "+ CONSUMER_SECRET)
    ACCESS_TOKEN = config_data["src_account"]["access_token"]
    ACCESS_SECRET = config_data["src_account"]["access_secret"]
    if(args.verbose):
        print("src account_ID: " + config_data["src_account"]["account_name"])
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)
    if(args.init):
        results = api.user_timeline(screen_name=config_data["src_account"]["account_name"])
        if(args.verbose):
            print("INIT MODE -- last ID: " + str(results[0].id))
    else:
        results = api.user_timeline(screen_name=config_data["src_account"]["account_name"], since_id=int(config_data["last_id"]))
    # update the latest tweet ID.
    try:
        config_data["last_id"] = results[0].id
    except IndexError:
        sys.exit()
    if(args.init):
        sys.exit()
    results.reverse()
    if(args.verbose):
        print("=== Obtained Tweets since last run ===")
        for result in results:
            print(str(result.id) + "\t" + langdetect.detect(result.text) + "\t" + result.text)
    for result in results:
        if(re.search('^@', result.text)):
            if(args.verbose):
                print("Ignored because it is a reply: \t" + result.text)
            continue
        try:
            dst_access_token  = config_data[langdetect.detect(result.text)]["access_token"]
            dst_access_secret = config_data[langdetect.detect(result.text)]["access_secret"]
            auth.set_access_token(dst_access_token, dst_access_secret)
            api_dst = tweepy.API(auth)
            api.update_status(status=result.text)
            if(args.verbose):
                print("TWEET POSTED ("+ langdetect.detect(result.text) +"): \t" + result.text)
        except KeyError:
            if(args.verbose):
                print("Ignored because it is a specified language ("+ langdetect.detect(result.text) +"): \t" + result.text)
            continue

    with open(args.config_file, 'w') as fd:
        json.dump(config_data, fd, sort_keys=True, indent=4)

