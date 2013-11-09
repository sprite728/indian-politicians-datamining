from pymongo import MongoClient
from twython import Twython, TwythonRateLimitError
import time

HOST = 'localhost'
PORT = 27017

client = MongoClient(HOST, PORT)

db = client.india

cursor = db.politicians.find(
    spec={
        "cleaned_twitters": {"$exists": True},
        "twitter_followers_ids_temp_success_flag": {"$exists": False}
    },
    timeout = False
)

print "start"
# Initial Error Prevention
try:
    followers_ids_obj = twitter.get_followers_ids(screen_name="sprite728")
except:
    pass

completed = False
while not completed:
    p = next(cursor, None)
    try:
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
    except:
        print "error: " + p.get("p_Name of elected MP")
        