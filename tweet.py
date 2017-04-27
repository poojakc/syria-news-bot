import feedparser, random, tweepy, sys, os
from urlparse import urlparse, parse_qs
import csv
from local_settings import *

''' CONFIGURATION '''
debug = True
keyword = 'syria'
hashtag = '#AssadOnceSaid'
maximum_retries = 200
max_file_len = 10
csv_top_sites = 'topsites.csv'
already_tweet_file = 'already_tweeted.txt'
url_feed = 'https://news.google.com/news?cf=all&hl=en&pz=1&q=%s&output=rss' % (keyword)
d = feedparser.parse(url_feed)
url_from_feed = []
temp_url_feed = []
top_site = []
quotes = [
    'Syria is geographically and politically in the middle of the Middle East.',
    'Worry does not mean fear, but readiness for the confrontation.',
    'I am Syrian, I was made in Syria, I have to live in Syria and die in Syria.',
    'As far as we are concerned, we Syria have not changed.',
    'The problem is not the occupation, but how people deal with it.',
    'We, in Syria, our point of view stems from our experience.',
    'Armies are not only for offensives.',
    'When we analyze this war in a materialistic way & ask when is it going to end it means that we do not see the endgame.',
    'If you want to go towards democracy, the first thing is to involve the people in decision making, not to make it.',
    'Worry does not mean fear, but readiness for the confrontation.',
    'Despite the ethnic diversity within each nation, the social fabric of the region by and large is one.',
    'Hizbullah is not a militia.',
    'You cannot reform your society or institution without opening your mind.',
    'No doubt that the US is a super-power capable of conquering a relatively small country but is it able to control it?',
    'America is interested in re-arranging the region as it sees fit.',
    'But the issue has to do with land, which is our land.',
    'It should be known that Israel is based on treachery.',
    'Syria is stable because you have to be closely linked to the beliefs of the people. This is the core issue.',
    'The logical thing is to implement the Arab Defense Agreement.',
    'We are dealing with treachery and threats, which accompanied the establishment of Israel.',
    'None of us and none of the Arabs trust Israel.',
    'I am not a puppet. I was not made by the West to go to the West or to any other country.',
    'No government in the world kills its people, unless it is led by a crazy person.',
    'To resign would be to flee.',
    'No solution can be reached with terror except by striking it with an iron fist.',
    'The fighting was started by terrorists, not the military crackdown on peaceful protesters.',
    'All those massacred civilians actually loved me.',
    'Who can say whether Syria has instituted enough reform?',
    'We have to fight terrorism for the country to heal.',
    'What we are facing is a conspiracy of sedition, division and destruction of our homeland.',
    'We will not be lenient. We will be forgiving only for those who renounce terrorism.',
    'This crisis is not an internal crisis. It is an external war carried out by internal elements.',
    'The masks have fallen and the international role in the Syrian events is now obvious.',
    'If we dont feel the pain that squeezes our hearts, as I felt it, for the cruel scenes then we are not human beings.'
    ]

#print [field for field in d]

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def process(quotes):
    sep4 = ' - '
    rest4 = quotes.split(sep4, 1)[0]
    sep5 = ' ...'
    rest5 = rest4.split(sep5, 1)[0]
    sep6 = ' | '
    rest6 = rest5.split(sep6, 1)[0]
    return rest6

def add_id_to_file(tweet):
    with open(already_tweet_file, 'a') as file:
        file.write(str(tweet) + "\n")

def duplicate_check(tweet):
    found = 0
    with open(already_tweet_file, 'r') as file:
        for line in file:
            if tweet in line:
                found = 1
    return found

if __name__ == "__main__":
    # setup API
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)
    # get data from item
    for item in d['items']:
        parsed = urlparse(item['link'])
        url = parse_qs(parsed.query)['url'][0]
        domain = urlparse(parse_qs(parsed.query)['url'][0]).netloc
        url_from_feed.append([url, domain])

    # open top site on csv and load it to list
    with open(csv_top_sites, 'r') as f:
        reader = [row for row in csv.reader(f.read().splitlines())]
        top_site_rule = list(reader)

    # checking top site in csv file.
    for site_rule in top_site_rule:
        for url_check in url_from_feed:
            if url_check[1] in site_rule[2]:
                top_site.append(url_check)
                if debug: print "%s -> %s on %s on row %s matched!" % (url_check[1], site_rule[2], csv_top_sites, site_rule[0])
    if debug: print top_site

    # check file if full delete
    if file_len(already_tweet_file) >= max_file_len:
        print "%s is full, deleting and creating new one" % (already_tweet_file)
        os.remove(already_tweet_file)
        try:
            file = open(already_tweet_file, 'r')
        except IOError:
            file = open(already_tweet_file, 'w')

    tweet_successfull = False
    cnt = 0
    while 1:
        try:
            cnt +=1
            if tweet_successfull:
                break
            if maximum_retries <= cnt:
                print "%d Maximum retries reached..." % (maximum_retries)
                break
            # choose random link and tweet
            link = process(random.choice(top_site)[0])
            status = process(random.choice(quotes))
            # appending tweet with status and link
            tweet = status +" "+ hashtag+" "+link
            if duplicate_check(status) == 0 and duplicate_check(link) == 0 and duplicate_check(tweet) == 0:
                add_id_to_file(tweet)
                api.update_status(tweet)
                print "%s posted successfully!" % (tweet)
                tweet_successfull = True
            else:
                print('tweet already tweeted')
                pass
        except KeyboardInterrupt:
            print "Interrupted!"
            sys.exit(1)
        except Exception, e:
            print e
            print tweet
            pass
