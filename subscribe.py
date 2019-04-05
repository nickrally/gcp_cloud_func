import os
from google.cloud import pubsub_v1

TOPIC_NAME           = os.getenv("TOPIC_NAME", "Nada")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "Nada")
SUBSCRIPTION_NAME    = os.getenv("SUBSCRIPTION_NAME", "Nada")

topic             = f"projects/{GOOGLE_CLOUD_PROJECT}/topics/{TOPIC_NAME}"
subscription_name = f'projects/{GOOGLE_CLOUD_PROJECT}/subscriptions/{SUBSCRIPTION_NAME}'

subscriber = pubsub_v1.SubscriberClient()

def callback(message):
    print(message.data)
    message.ack()

future = subscriber.subscribe(subscription_name, callback)

try:
    stuff = future.result()
    print("Here is what i got for the subscribe result: %s" % stuff)
except KeyboardInterrupt:
    future.cancel()
    print("Subscriber action cancelled")
