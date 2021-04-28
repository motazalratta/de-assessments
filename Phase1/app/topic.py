import logging
import time
import threading

from google.api_core.exceptions import AlreadyExists,InvalidArgument
from google.cloud.pubsub import SchemaServiceClient,PublisherClient
from google.cloud import pubsub_v1
from google.pubsub_v1.types import Schema,Encoding

class Topic:
    def __init__(self, project_id, topic_id, schema_id, proto_path, input_filename,batch_publish, batch_max_messages,batch_max_bytes,batch_max_latency,batch_max_threads):
        self.project_id = project_id
        self.topic_id = topic_id        
        self.schema_id = schema_id
        self.proto_path = proto_path
        self.input_filename = input_filename
        
        self.batch_publish = batch_publish
        self.batch_max_messages = batch_max_messages
        self.batch_max_bytes = batch_max_bytes
        self.batch_max_latency = batch_max_latency

        batch_settings = pubsub_v1.types.BatchSettings(
            max_messages=batch_max_messages, 
            max_bytes=batch_max_bytes,
            max_latency=batch_max_latency,
        )
        

        self.open_threads=0
        self.batch_max_threads = batch_max_threads

        if self.batch_publish:
            self.publisher_client = PublisherClient(batch_settings)
        else:
            self.publisher_client = PublisherClient()

        self.topic_path = self.publisher_client.topic_path(project_id, topic_id)

        # create the topic
        self.create_proto_schema()
        self.create_topic_with_schema()

    def create_proto_schema(self):
        project_path = f"projects/{self.project_id}"

        # Read a protobuf schema file as a string.
        with open(self.proto_path, "rb") as f:
            proto_source = f.read().decode("utf-8")

        schema_client = SchemaServiceClient()
        schema_path = schema_client.schema_path(self.project_id, self.schema_id)
        schema = Schema(
            name=schema_path, type_=Schema.Type.PROTOCOL_BUFFER, definition=proto_source
        )

        try:
            result = schema_client.create_schema(
                request={"parent": project_path, "schema": schema, "schema_id": self.schema_id}
            )
            logging.info(f"Created a schema using a protobuf schema file:\n{result}")
        except AlreadyExists:
            logging.info(f"{self.schema_id} schema already exists.")

    def create_topic_with_schema(self):
        topic_path = self.publisher_client.topic_path(self.project_id, self.topic_id)

        schema_client = SchemaServiceClient()
        schema_path = schema_client.schema_path(self.project_id, self.schema_id)

        try:
            response = self.publisher_client.create_topic(
                request={
                    "name": topic_path,
                    "schema_settings": {"schema": schema_path, "encoding": Encoding.JSON},
                }
            )
            logging.info(f"Created a topic:\n{response}")

        except AlreadyExists:
            logging.info(f"{self.topic_id} topic already exists.")
    
    def publish(self,json_string):
        data = str(json_string).encode("utf-8")
        if self.batch_publish:
            future = self.publisher_client.publish(self.topic_path, data)
            future.add_done_callback(self.callback)
            while threading.active_count()>self.batch_max_threads:
                logging.info(f"The open threads {threading.active_count()} > {self.batch_max_threads} => waiting 2 seconds")
                time.sleep(2)
        else:
            future = self.publisher_client.publish(self.topic_path, data)
            logging.info(f"Published message ID: {future.result()}")

    def callback(self,future):
        logging.debug(f"Published message ID: {future.result()}")


