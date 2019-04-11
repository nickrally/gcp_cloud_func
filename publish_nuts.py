#
# publish_nuts.py - create payloads for the walnut topic that are thinly wrapped items representing PullRequest items to be created in Rally
#                   take 2 args, total_number_of_items_to_publish and cadence value in seconds (floatable, ie., 2.5 or 0.004)
#
#
'''
https://google-cloud.readthedocs.io/en/latest/pubsub/publisher/api/client.html
topic (str) – The topic to publish messages to.
data (bytes) – A bytestring representing the message body. This must be a bytestring.
attrs (Mapping[str, str]) – A dictionary of attributes to be sent as metadata. (These may be text strings or byte strings.)
'''

import os, sys
from google.cloud import pubsub_v1
import time
import json
from random import randint

TOPIC_NAME           = os.getenv("TOPIC_NAME", "walnut")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "Nada")

##########################################################################################################

def read_json():
    #content = None
    with open("ghpr-min.json") as f:
        content = f.read()
    return json.loads(content)

def manufactureRallyPullRequest(index):
    raw = read_json()
    fake_item = str(1500 + int(index))
    raw['ExternalFormattedId'] = fake_item
    raw['Url'] = raw['Url'].replace('1347', fake_item)
    return raw

##########################################################################################################

def main(args):
    if len(args) != 2:
        print("you must supply a count of messages and an interval value (floating point number)")
        sys.exit(1)
    limit = int(args[0])
    sub_generous_nap = float(args[1])

    topic = f"projects/{GOOGLE_CLOUD_PROJECT}/topics/{TOPIC_NAME}"

    publisher = pubsub_v1.PublisherClient()

    for i in range(limit):
        rally_pull_request = manufactureRallyPullRequest(i+1)
        message = {'PullRequest'     : rally_pull_request,
                   'SubscriptionID'  : 209,
                   'APIKey'          : os.getenv('APIKEY', None),
                   'GHMsgID'         : randint(1, 20000000),
                  }
        future = publisher.publish(topic, json.dumps(message).encode())
        try:
            result = future.result()
            print("%s: %s" % (i, result))
        except:
            print("unable to get future result for publish action")

        time.sleep(sub_generous_nap)

##########################################################################################################
##########################################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])

