import os, sys
from google.cloud import pubsub_v1
import time
import json
from random import randint
from helpers.chronuti import TimeStamp

GH_PAYLOAD_TOPIC     = os.getenv("TOPIC_NAME", "melon")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "Nada")

##########################################################################################################

def main(args):
    if len(args) != 3:
        print("you must supply a count of messages and an interval value (floating point number) and an initial sequence number")
        sys.exit(1)
    limit = int(args[0])
    sub_generous_nap = float(args[1])
    start_number = int(args[2])

    topic = f"projects/{GOOGLE_CLOUD_PROJECT}/topics/{GH_PAYLOAD_TOPIC}"

    publisher = pubsub_v1.PublisherClient()

    for ix in range(limit):
        gh_pr = augmentGithubPayload(start_number + ix)
        message = {
            "message-id"  : randint(1, 5000000),
            "timestamp"   : TimeStamp.now().asISOString(),
            "installation": { "id": 635843, "node_id": "MDIzOkludGVncmF0aW9uSW5zdGFsbGF0aW9uNjM1ODQz" },
            "payload"     : gh_pr
        }
        future = publisher.publish(topic, json.dumps(message).encode())
        try:
            result = future.result()
            print("%s: %s" % (ix, result))
        except:
            print("unable to get future result for publish action")

        time.sleep(sub_generous_nap)

##########################################################################################################

def read_json():
    with open("github-payload-example.json") as f:
        content = f.read()
    return json.loads(content)

def augmentGithubPayload(number):
    payload = read_json()
    payload['number' ]= number
    cruft, _ = payload['pull_request']['url'].rsplit('/', 1)
    payload['pull_request']['url'] = "%s/%s" % (cruft, number)
    payload['pull_request']['number'] = number
    return payload

##########################################################################################################
##########################################################################################################

if __name__ == "__main__":
    main(sys.argv[1:])