# -*- coding: utf-8 -*-

'''
Created on Apr 18, 2017

@author: Semra
'''

from twython import Twython
import unicodedata
import re
import os
import time
import sqlite3
from datetime import datetime


def getTwitterAuth():
    TWITTER_APP_KEY = '' #APP KEY
    TWITTER_APP_KEY_SECRET = '' #SECRET KEY
    twitter = Twython(TWITTER_APP_KEY, TWITTER_APP_KEY_SECRET, oauth_version=2)
    ACCESS_TOKEN = twitter.obtain_access_token()
    return  Twython(TWITTER_APP_KEY, access_token=ACCESS_TOKEN)

def removeURL (str):
    #return str
    return re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', str, flags=re.MULTILINE)

def removeNewLine(str):
    return str.replace('\n', ' ')

def refineTweetText(tweettext):
    #turkish=u'âçğıİîöşüû'
    return removeNewLine(removeURL(unicodedata.normalize('NFKD', tweettext).replace(u'ı','i').encode('ascii','ignore')).lower())

def TweetText(tweet):
    if tweet['full_text'].startswith('RT @'):
        return refineTweetText(tweet['retweeted_status']['full_text'])
    else:
        return refineTweetText(tweet['full_text'])  

def tweetSplit(string):
    return string.replace('!',' !').replace('?'," ?").replace(':',' :').replace(',',' , ').replace('.','. ')

def converTime(timeFromTwitter):
    datetimeformat = datetime.strptime(timeFromTwitter, '%a %b %d %H:%M:%S +0000 %Y')
    return str(datetimeformat)+'.000'

def getConnection():
    return sqlite3.connect('',timeout=1) # DBPATH
    
def executeQuery(sql_str):
    conn = getConnection()
    c= conn.cursor()
    try:
        c.execute(sql_str)
        conn.commit()
        conn.close()
    except:
        print "\t[!!]ERROR: "+sql_str
        pass


def createKeywordDictionaies():
    word_dic={} #for single words
    sent_dic={} #for word groups
    c = getConnection().cursor()
    c.execute('select key_value, key_text from keyword')
    rows=c.fetchall()
    for row in rows:
        if ' ' in row[1] or len(row[1]) >= 5:
            sent_dic[row[1]]=row[0]
        else:    
            word_dic[row[1]]=row[0]
    return word_dic,sent_dic


def getDataFromTwitter(hashtag):
    tweetList=[]
    userList=[]
    mainList=[]    
    search_results = getTwitterAuth().search(q='#'+hashtag, count=1000, lang='tr', tweet_mode='extended')
    recoredTweets=getTweetIDs()
    for tweet in search_results['statuses']:
        tweet_id=str(tweet['id'])
        if tweet_id in recoredTweets:
            pass
        else:
            print 'NEW TWEET FOUND!'   
            tweetList.append({
                    'tweet_id':tweet_id,
                    'tweet_text':TweetText(tweet),
                    'lang':tweet['lang'],
                    'retweet_count':str(tweet['retweet_count']),
                    'like_count':str(tweet['favorite_count']),
                    'reply_count':'0'
                    })
            
            userList.append({
                'tweet_id':tweet_id,
                'username':str(tweet['user']['screen_name']),
                'followers_count':str(tweet['user']['followers_count']),
                'friends_count':str(tweet['user']['friends_count'])
                })
            
            mainList.append({
                'tweet_id':tweet_id,
                'geo_code':'1',
                'creation_time':converTime(tweet['created_at']),
                'search_key':hashtag
                })
    return tweetList, userList, mainList

def getTweetIDs():
    idList=[]
    tweet_ids=getConnection().cursor().execute('select tweet_id from tweets').fetchall()
    for tweet_id in tweet_ids:
        if tweet_id is not None:
            idList.append(str(tweet_id[0]))
    return idList


def fillTweets(hashtag):
    tweetList,userList, mainList=getDataFromTwitter(hashtag)
    tweetstr= 'insert into tweets values'
    userstr= 'insert into user_data values'
    mainstr= 'insert into main values'

    if len(tweetList) > 0 :

        print "[ ! ] Inserting tweets" 
        for tw in tweetList:
            tweetstr =tweetstr+ '("'+tw['tweet_id']+'", "'+tw['tweet_text'].replace("\"","'")+'", "'+tw['lang']+'", "'+tw['retweet_count']+'", "'+tw['like_count']+'", "'+tw['reply_count']+'"), '
        print tweetstr[:-2]
        executeQuery(tweetstr[:-2])
        print "\t[ ! ] Tweets Inserted" 


        print "[ ! ] Inserting users"
        for user in userList:
            userstr =  userstr+ '("'+user['tweet_id']+'", "'+user['username']+'", "'+user['followers_count']+'", "'+user['friends_count']+'"), '
        print userstr[:-2]
        executeQuery(userstr[:-2])
        print "\t[ ! ] Users Inserted" 


        print "[ ! ] Inserting Main"
        for item in mainList:
            mainstr = mainstr+ '("'+item['tweet_id']+'", "'+item['geo_code']+'", "'+item['creation_time']+'", "'+item['search_key']+'"), '
        print mainstr[:-2]
        executeQuery(mainstr[:-2])
        print "\t[ ! ] Main Inserted" 
    else:
        print "[!]NO NEW TWEETS"

def getTweets2Compare(hashtag):
    if hashtag =='All':
        tweetstr = "select t.tweet_id, t.tweet_text from  tweets as t inner join main as m on m.tweet_id = t.tweet_id"
    else:
        tweetstr = "select t.tweet_id, t.tweet_text from  tweets as t inner join main as m on m.tweet_id = t.tweet_id and m.search_key='"+hashtag+"'"
    c = getConnection().cursor()
    c.execute(tweetstr)
    return c.fetchall()


def compare(hashtag):
    word_dic,sent_dic = createKeywordDictionaies()
    tweetarr=getTweets2Compare(hashtag)
    for tweet_id, tweet_text in tweetarr:
        impression=0
        score = 0
        keywords = ''
        tweettextarr=tweet_text.replace('!',' !').replace('?'," ?").replace(':',' :').replace(',',' , ').replace('.','. ').split()
        for wg in sent_dic:
            if wg in tweet_text:
                score=score+sent_dic.get(wg)
                keywords=keywords+wg+', '
        for word in set(tweettextarr):
            try:
                score = score + word_dic.get(word)
                keywords=keywords+word+', '
            except:
                pass
        if score < 0:
            impression=2
        elif score > 0:
            impression = 1
        resultstr= "insert into result values ("+str(tweet_id)+","+str(impression)+","+str(score)+",'"+keywords[:-2]+"')"
        executeQuery(resultstr)

def getSearchKeys():
    c = getConnection().cursor()
    c.execute("select search_key from main group by search_key order by  search_key ASC")
    search_keys=['All']
    for sk in c.fetchall():
        search_keys.append(sk[0])
    return search_keys

