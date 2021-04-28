# Phase1 - Publisher

A small python application reads all input files (and wait the new file to come) and publishes the data to Google Pub/Sub

## Keu Points:
- Configurable: reads all input from config.yml
    + input/output path folders
    + batch_settings (e.g. max_messages)
    + array of topic
        * topic id
        * schema id
        * protobuf path
        * input filename (the expected json file name in input tar.gz)
- Creates topics-schema and topics if they are not exist
- Supports batch publish

## Installation

Build docker image

```sh
sudo docker build -t phase1:v1 .
```

## Execute
I created two topics transaction (batch publish) and location (sequential publish)

#### config.yml
```yaml
pubsub:
    raw_file_dir: ../input/
    archive_file_dir: ../archive/

    batch_settings:
        max_messages: 10
        max_bytes: 1024 
        max_latency: 2 # second
        max_threads: 100
    topics:
        transaction:
            topic_id: transaction
            schema_id: transaction_schema
            batch_publish: True
            proto_path: ./schemas/transaction_schema.proto
            input_filename: transactions.json
        location:
            topic_id: location
            schema_id: location_schema
            batch_publish: False
            proto_path: ./schemas/location_schema.proto
            input_filename: locations.json
```
created docker image
```sh
sudo docker run \
-e GOOGLE_CLOUD_PROJECT="<ProjectID>" \
-e GOOGLE_APPLICATION_CREDENTIALS=/app/config/googlecloud.key.file.json \
-v $(pwd)/config/:/app/config/ \
-v $(pwd)/input/:/input/ \
-v $(pwd)/archive/:/archive/ \
phase1:v1
```

## Possible Imporvments
- Config input error handling  
- pytest
