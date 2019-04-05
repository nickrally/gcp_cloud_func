import sys, os
from google.cloud import pubsub_v1

TOPIC_NAME           = os.getenv("TOPIC_NAME", "Nada")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "Nada")


if not sys.argv[1:]:
    print("You have to provide a subscription name as an argument")
    sys.exit(1)

sub_name = sys.argv[1]

topic             = f"projects/{GOOGLE_CLOUD_PROJECT}/topics/{TOPIC_NAME}"
subscription_name = f'projects/{GOOGLE_CLOUD_PROJECT}/subscriptions/{sub_name}'

subscriber = pubsub_v1.SubscriberClient()
subscriber.create_subscription(name=subscription_name, topic=topic)

print(f"created a subscription named: {sub_name}")

