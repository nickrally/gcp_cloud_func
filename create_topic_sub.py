#
# publish_nuts.py - Publish JSON objects representing a basic PullRequest set of attributes/values that can be used to create a Rally PullRequest item
#
USAGE = """
publish_nuts.py <topic_name> <number_of_nuts>
"""

import os, sys
from google.cloud import pubsub_v1

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "Nada")

args = sys.argv[1:]
if not args:
    print("you need to supply topic name")
    sys.exit(1)

topic_name = args.pop(0)
if args:
    sub_name = args.pop(0)
else:
    sub_name = None

topic = f"projects/{GOOGLE_CLOUD_PROJECT}/topics/{topic_name}"

publisher = pubsub_v1.PublisherClient()
result = publisher.create_topic(topic)
print(result)
print("Created Pub/Sub topic: %s of type %s" % (topic_name, type(result)))

if sub_name:
    subscription_name = f'projects/{GOOGLE_CLOUD_PROJECT}/subscriptions/{sub_name}'
    subscriber = pubsub_v1.SubscriberClient()
    result = subscriber.create_subscription(name=subscription_name, topic=topic)
    print(result)
    print("Created Pub/Sub subscription: %s of type %s" % (sub_name, type(result)))
