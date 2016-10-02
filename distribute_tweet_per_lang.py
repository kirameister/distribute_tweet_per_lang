# -*- coding: utf-8 -*-

import argparse
import codecs
import json
import re
import sys

import langdetect
import tweepy


def manual_lang_detection(text: str, lang_data):
    return_set = set()
    if(len(lang_data) == 0):
        return(return_set)
    for lang in lang_data:
        for expression in lang_data[lang]:
            if(re.search(expression, text)):
                return_set.add(lang)
    return(return_set)


if(__name__ == '__main__'):
    parser = argparse.ArgumentParser(description='Detect the language of latest tweet(s) and distribute to appropriate (and separate) account. ')
    parser.add_argument('config_file', type=str, help="Name of the JSON file with required configurations. ")
    parser.add_argument('-l', '--lang', type=str, help="Name of the JSON file with expressions for different languages")
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('-i', '--init', action="store_true")
    args = parser.parse_args()
    # loading configs..
    with open(args.config_file, 'r') as fd:
        config_data = json.load(fd)
    CONSUMER_KEY = config_data["consumer_key"]
    CONSUMER_SECRET = config_data["consumer_secret"]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    if(args.verbose):
        print("consumer_key: " + CONSUMER_KEY + "\nconsumer_secret: "+ CONSUMER_SECRET)
    lang_data = []
    if(args.lang):
        if(args.verbose):
            print("language file: " + args.lang)
        with codecs.open(args.lang, 'r', 'utf-8') as fd:
            lang_data = json.load(fd)
    # Retrieving tweets from src account..
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
        print("=== No result obtained, perhaps no updated tweet from the last run? ===")
        sys.exit()
    if(args.init):
        sys.exit()
    results.reverse()
    if(args.verbose):
        print("=== Obtained Tweets since last run ===")
        for result in results:
            languages = langdetect.detect_langs(result.text)
            print(str(result.id) + "\t" + str(languages) + "\t" + result.text)
    if(args.verbose):
        print("=== Start forwarding the tweets.. ===")
    for result in results:
        if(re.search('^@', result.text)):
            if(args.verbose):
                print("Ignored because it is a reply: \t" + result.text)
            continue
        predicted_lang_set = set()
        # manual prediction comes here..
        predicted_lang_set |= manual_lang_detection(result.text, lang_data)
        if(args.verbose and predicted_lang_set):
            print("Predicted langs by manual patterns: " + str(manual_lang_detection(result.text, lang_data)))
        # following is automatic detection..
        predicted_langs = langdetect.detect_langs(result.text)
        for i,lang_value in enumerate(predicted_langs):
            predicted_lang_set.add(re.sub(':.*$', '', str(lang_value)))
        for lang in predicted_lang_set:
            try:
                dst_access_token  = config_data[lang]["access_token"]
                dst_access_secret = config_data[lang]["access_secret"]
                auth.set_access_token(dst_access_token, dst_access_secret)
                api_dst = tweepy.API(auth)
                #api.update_status(status=result.text)
                if(args.verbose):
                    print("TWEET POSTED ("+ lang +"): \t" + result.text)
            except KeyError:
                if(args.verbose):
                    print("Ignored because it is not one of those specified languages ("+ lang +"): \t" + result.text)
                continue

#    with open(args.config_file, 'w') as fd:
#        json.dump(config_data, fd, sort_keys=True, indent=4)

