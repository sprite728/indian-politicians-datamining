import csv
import ipdb
from pymongo import MongoClient
from twython import Twython, TwythonRateLimitError
from secret import *
from constants import *
import time
"""
====================================================================================
        Get all the Twitter accounts
====================================================================================
"""

client = MongoClient(HOST, PORT)
db = client.india

# obj = next(cursor, None)

cursor = db.politicians.find()
# twitters = {}

for p in cursor:
    twitter_account = p.get('p_Twitter', None)
    if twitter_account != '' and twitter_account != None and twitter_account != 'No':
        # print twitter_account
        twitter_account = twitter_account.replace("https://twitter.com/", "")
        cleaned_twitter_accounts = twitter_account.split()

        # p["cleaned_twitter_accounts"] = cleaned_twitter_accounts
        db.politicians.update(
            { '_id': p.get('_id')}, # update criteria
            { '$set' : { 'cleaned_twitters': cleaned_twitter_accounts} } #update action
        )

        # See MongoDB Update Operator 
        # http://docs.mongodb.org/manual/reference/operator/update/#id1
        

        # For testing, only get the first account
        cleaned_twitter_account = cleaned_twitter_accounts[0]
        print cleaned_twitter_account
        # twitters.append(cleaned_twitter_account)
        # twitters[p.get('')]


"""
====================================================================================
        Twitter -- 
====================================================================================
    
    Note
    1. Since we will only read public information from Twitter and won't need users 
        to authorize anything, we would only need to use OAuth2 rather than OAuth1

    Process:
    + Construct A Graph from the Twitter accounts we have
    + Output the Graph to GML format
    + Read and visualize the Graph by R (igraph) library, or maybe I could directly 
      visualize it in python?


    Process - Construct A Graph From Twitter
    + Loop thorugh all the politicians who has a Twitter account
    + Fetch the followers information from his/her Twitter account
        + if excceed Twitter rate limit
            - wait until the reset time, restart
            (Q: the reset time is the server time on Twitter, but the current time is the time
                on my machine, there must be a difference)

"""
twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
# twitter.search(q='python')

# Only fetches the politicians who has at least one twitter account
cursor = db.politicians.find(
        { 
            "cleaned_twitters": {"$exists": True }, 
            "twitter_followers_obj": {"$exists": False }
        }
    )


for p_obj in cursor:
    print p_obj.get("p_Name of elected MP")
    t_names = p_obj.get("cleaned_twitters", None)

    # For now, only use the first twtter name
    t_name = t_names[0]

    try:
        # ipdb.set_trace()
        obj_followers = twitter.get_followers_list(screen_name=t_name)
    
    # except:
    #     # success = False
    #     while success == False:
    #         try:
    #             obj_followers = twitter.get_followers_list(screen_name=t_name)
    #             success = True
    #         except:
    #             if int(twitter.get_lastfunction_header('x-rate-limit-remaining')) == 0:
    #                 print 'Rate limit reset time: ' + twitter.get_lastfunction_header('x-rate-limit-reset')
    #                 print 'Rate limit remaining: ' + twitter.get_lastfunction_header('x-rate-limit-remaining')
    #                 time.sleep(60)

    #     # obj_followers = obj_followers.get("users", None)
        print "... get followers"
        
        # print len(obj_friends) 
        if len(obj_friends) > 3000:
            print "... Warning, this user has more than 3000 followers."
        else: 
            print "success"

        #Note, need to check how to parse mutliple pages
        update_msg = db.politicians.update(
            { "_id": p_obj["_id"]},
            { "$set": {"twitter_followers_obj": obj_followers } }
        )
        print "... update_msg: "

        
    except TwythonRateLimitError:
        print "... rate limit error exception"
        reset_time = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
        remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
        
        print '... reset_time: ' + str(reset_time)
        print '... remaining: ' + str(remaining)

        if int(remaining) == 0:
            print 'remaining == 0'

            passed_reset_time = False
            while passed_reset_time == False:
                if (reset_time + 60) < time.time():
                    passed_reset_time = True
                else:
                    print time.ctime(int(reset_time))
                    print time.ctime(time.time()) + " (current time)"
                    print "sleep"
                    time.sleep(5)
    except Exception as ex:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print message 

        # cursor.rewind()
"""
====================================================================================
        Fetch Followers Ids from Twitter, not user objects
====================================================================================
"""


cursor = db.politicians.find(
    {
        "cleaned_twitters": {"$exists": True},
        "twitter_followers_ids_temp_success_flag": {"$exists": False}
    }
)

# Initial Error Prevention
try:
    followers_ids_obj = twitter.get_followers_ids(screen_name="sprite728")
except:
    pass

completed = False
while not completed:
    p = next(cursor, None)
    if p:
        print p.get("p_Name of elected MP")
        t_names = p.get("cleaned_twitters", None)
        t_name = t_names[0]

        got_all_the_followers_of_a_politician = False
        default_cursor = -1
        while not got_all_the_followers_of_a_politician:
            if int(twitter.get_lastfunction_header('x-rate-limit-remaining')) != 0:
                followers_ids_obj = twitter.get_followers_ids(screen_name=t_name, cursor=default_cursor)
                followers_ids = followers_ids_obj.get("ids", None)

                # Push new ids to the document
                db.politicians.update(
                    {
                        "_id": p["_id"]
                    },
                    {
                        "$push": { 
                            "twitter_followers_ids": { "$each": followers_ids }
                        }
                    }
                )

                next_cursor = int(followers_ids_obj.get("next_cursor"))
                if int(followers_ids_obj.get("next_cursor")) != 0:
                    default_cursor = next_cursor
                    print "... finish this 5000 batch, continue ..."
                else:
                    default_cursor = -1

                    db.politicians.update(
                        { "_id": p["_id"] },
                        { "$set": {"twitter_followers_ids_temp_success_flag": True}}
                    )
                    got_all_the_followers_of_a_politician = True
                    print "... completed"
            else:
                # remaining == 0
                print "... exceed rate limit "
                reset_time = int(twitter.get_lastfunction_header('x-rate-limit-reset'))
                remaining = int(twitter.get_lastfunction_header('x-rate-limit-remaining'))
                
                print '... reset_time: ' + str(reset_time)
                print '... remaining: ' + str(remaining)

                if int(remaining) == 0:
                    print 'remaining == 0'

                    passed_reset_time = False
                    while passed_reset_time == False:
                        if (reset_time + 60) < time.time():
                            passed_reset_time = True
                        else:
                            print time.ctime(int(reset_time))
                            print time.ctime(time.time()) + " (current time)"
                            print "sleep"
                            time.sleep(15)  
    else:
        completed = True
        print "=== DONE ==="





"""
====================================================================================
        Get Twitter User information
====================================================================================
"""

cursor = db.politicians.find(
        { 
            "twitter_followers_obj": {"$exists": True},
            "cleaned_twitters": {"$exists": True },
            "twitter_user_info": {"$exists": False}
        }
    )

for p in cursor:
    t_names = p.get("cleaned_twitters", None)

    # For now, only use the first twtter name
    t_name = t_names[0]

    twitter_user_info = twitter.show_user(screen_name=t_name)
    db.politicians.update(
        { "_id": p["_id"]},
        { "$set": {"twitter_user_info": twitter_user_info } }
    )

"""
====================================================================================
        Construct GML based on the Twitter followers
====================================================================================
"""
import networkx as nx
import matplotlib.pyplot as plt

cursor = db.politicians.find(
        { 
            "twitter_followers_obj": {"$exists": True},
            "cleaned_twitters": {"$exists": True }
        }
    )

G = nx.Graph()


for p in cursor:
    t_names = p.get("cleaned_twitters", None)
    t_name = t_names[0]

    G.add_node(t_name, color=1)

    followers_obj = p.get("twitter_followers_obj", None)
    followers = followers_obj.get("users", None) #followers is a list
    for follower in followers: #follower is a dict
        follower_name = follower.get("screen_name")
        G.add_node(follower_name, color=0.25)
        G.add_edge(t_name, folower_name)



nx.draw(G)
plt.show()



