import os
import random
import string
import time

from locust import TaskSet, task, events, User

from kafka_client.AdditionalHandlers import additional_success_handler, additional_failure_handler
from kafka_client.KafkaClient import KafkaClient

WORK_DIR = os.path.dirname(__file__)

# read kafka brokers from config
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092").split(sep=",")

# read other environment variables
QUIET_MODE = True if os.getenv("QUIET_MODE", "true").lower() in ['1', 'true', 'yes'] else False
TASK_DELAY = int(os.getenv("TASK_DELAY", "0"))

# register additional logging handlers
if not QUIET_MODE:
    events.request_success += additional_success_handler
    events.request_failure += additional_failure_handler


class KafkaBehaviour(TaskSet):
    #generate rando mesage
    def random_message(self, min_length=32, max_length=128):
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randrange(min_length, max_length)))
    
    def timestamped_message(self):
        return f"{time.time() * 1000}:" + ("kafka" * 24)[:random.randint(32, 128)]

    @task
    def task1(self):
        self.client.send("in-topic", message=self.timestamped_message())

    @task
    def task2(self):
        self.client.send("in-topic", message=self.timestamped_message(), key="key")

class KafkaLocust(User):
    client = None
    tasks = [KafkaBehaviour]

    def __init__(self, *args, **kwargs):
        super(KafkaLocust, self).__init__(*args, **kwargs)
        if not KafkaLocust.client:
            KafkaLocust.client = KafkaClient(KAFKA_BROKERS)