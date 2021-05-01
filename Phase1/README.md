# Phase1 - Publisher

A small python application that reads all input files (waits for new files to arriave) and publishes the data to Google Pub/Sub

## Key Points:
- Configurable: reads all inputs from config.yml
    + input/output path folders
    + batch_settings (e.g. max_messages)
    + array of topics
        * topic id
        * schema id
        * protobuf path
        * input filename (the expected json file name in input tar.gz)
- Creates topics-schema and topics if they are not exist
- Supports batch publish

## Activity Diagram
![your-UML-diagram-name](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/motazalratta/de-assessments/main/Phase1/ActivityDiagram.iuml)

## Installation

Build docker image

```sh
sudo docker build -t phase1:v1 .
```

## Usage
I created two topics transaction (batch publish) and location (sequential publish)

#### config.yml
```yaml
# the folder which contains the raw files
raw_files_dir: "../input/"
# the raw files will be moved to archive_files_dir after processing
archive_files_dir: "../archive/"

# the batch publish settings
batch_settings:
  max_bytes: 1024
  max_latency: 2 # second
  max_messages: 10
  max_threads: 100

# list of topics 
topics:
- topic_id: location
  schema_id: location_schema
  proto_path: "./schemas/location_schema.proto"
  batch_publish: false
  input_filename: locations.json
- topic_id: transaction 
  schema_id: transaction_schema
  proto_path: "./schemas/transaction_schema.proto"
  batch_publish: true
  input_filename: transactions.json
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
- pytest
