# Phase1 - Publisher

A small python application that reads all input files (waits for new files to appear) and publishes the data to Google Pub/Sub

## Key Points
- Configurable: reads all inputs from config.yml
    + input/output path folders
    + batch_settings (e.g. max_messages)
    + array of topics
        * topic id
        * schema id
        * protobuf path
        * input filename (the expected json file name in input tar.gz)
- Creates topics-schema and topics if they do not exist
- Supports batch publish

## Activity Diagram
![ActivityDiagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/motazalratta/de-assessments/main/Phase1/ActivityDiagram.iuml)

## Installation

Build docker image

```sh
sudo docker build -t phase1:v1 .
```

## Usage
I created two topics: <br>
transaction (batch publish)<br>
location (sequential publish)

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

## pytest
```sh
$ pytest --verbose
================================================================= test session starts =================================================================
platform linux -- Python 3.8.5, pytest-4.6.11, py-1.10.0, pluggy-0.13.1 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/motaz/repo/de-assessments/Phase1/app
plugins: forked-1.3.0, requests-mock-1.8.0, timeout-1.4.2, xdist-1.34.0
collected 7 items

main_test.py::test_not_required_args_provided PASSED                                                                                            [ 14%]
main_test.py::test_env_variable_not_set PASSED                                                                                                  [ 28%]
main_test.py::test_input_file_path_invalid PASSED                                                                                               [ 42%]
main_test.py::test_invalid_input_file_missing_archive_dir PASSED                                                                                [ 57%]
main_test.py::test_invalid_input_file_missing_raw_dir PASSED                                                                                    [ 71%]
main_test.py::test_valid_input_file_with_unfound_pathes PASSED                                                                                  [ 85%]
main_test.py::test_valid_input_file_with_valid_config PASSED                                                                                    [100%]

============================================================== 7 passed in 14.16 seconds ==============================================================
```
