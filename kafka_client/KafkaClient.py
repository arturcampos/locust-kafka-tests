import logging
import time
import sys
import six

from kafka import KafkaProducer
from locust import events

if sys.version_info >= (3, 12 , 0):
    sys.modules['kafka.vendor.six.moves'] = six.moves


class KafkaClient:

    def __init__(self, kafka_brokers=None):
        print("creating message sender with params: " + str(locals()))

        if kafka_brokers is None:
            kafka_brokers = ['localhost:9092']
        self.producer = KafkaProducer(bootstrap_servers=kafka_brokers)

    def __handle_success(self, *arguments, **kwargs):
        end_time = time.time()
        elapsed_time = int((end_time - kwargs["start_time"]) * 1000)
        try:
            record_metadata = kwargs["future"].get(timeout=1)

            request_data = dict(request_type="ENQUEUE",
                                name=record_metadata.topic,
                                response_time=elapsed_time,
                                response_length=record_metadata.serialized_value_size)

            self.__fire_success(**request_data)
        except Exception as ex:
            print("Logging the exception : {0}".format(ex))
            raise  # ??

    def __handle_failure(self, *arguments, **kwargs):
        print("failure " + str(locals()))
        end_time = time.time()
        elapsed_time = int((end_time - kwargs["start_time"]) * 1000)

        request_data = dict(request_type="ENQUEUE", name=kwargs["topic"], response_time=elapsed_time,
                            exception=arguments[0])

        self.__fire_failure(**request_data)

    #@events.request_failure.add_listener
    def __fire_failure(self, **kwargs):
        events.request.fire(**kwargs)
        #logging.warning("Failure: {0}".format(kwargs))

    #@events.request_success.add_listener
    def __fire_success(self, **kwargs):
        events.request.fire(**kwargs)
        #logging.info("Success: {0}".format(kwargs))

    def send(self, topic, key=None, message=None):
        start_time = time.time()
        future = self.producer.send(topic, key=key.encode() if key else None,
                                    value=message.encode() if message else None)
        future.add_callback(self.__handle_success, start_time=start_time, future=future)
        future.add_errback(self.__handle_failure, start_time=start_time, topic=topic)

    def finalize(self):
        print("flushing the messages")
        self.producer.flush(timeout=5)
        print("flushing finished")