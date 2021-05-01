import argparse
import glob
import jsonschema
import logging
import os
import shutil
import sys
import tarfile
import threading
import time
import yaml

from ymlvalidatorloader import YmlValidatorLoader
from topic import Topic


def parse_args(arg_input=None):
    parser = argparse.ArgumentParser(
        description='get path of schema and yml file.')
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument('--schema ', metavar='path_to_schema', dest='path_to_schema',
                               help='path to schema', required=True)
    required_named.add_argument('--ymlfile', metavar='path_to_yml_config', dest='path_to_yml_config',
                               help='path to yml', required=True)
    return parser.parse_args(arg_input)


if __name__ == '__main__':
    args = parse_args()
    logging.getLogger().setLevel(logging.INFO)

    # Check the env variables
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is None:
        logging.error('The env GOOGLE_APPLICATION_CREDENTIALS is null')
        sys.exit(3)
    if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
        logging.error('The env GOOGLE_CLOUD_PROJECT is null')
        sys.exit(3)

    # Read the config schema
    if not os.path.exists(args.path_to_schema):
        logging.error('schema file does not exist')
        sys.exit(4)
    if not os.path.exists(args.path_to_yml_config):
        logging.error('yml file does not exist')
        sys.exit(4)

    try:
        v = YmlValidatorLoader(args.path_to_schema, args.path_to_yml_config)
        v.validate()
    except Exception as e:
        logging.error(
            'An exception occurred while validating the config file\n{}'.format(e))
        sys.exit(5)

    config = v.yml_file_object
    # Check whether raw_files_dir is an existing directory or not
    if not os.path.isdir(config.raw_files_dir):
        logging.error('Can not find raw_files_dir: {}'.format(
            config.raw_files_dir))
        sys.exit(6)

    # Create the archive_files_dir if it is not exist
    arcive_dir = config.archive_files_dir
    try:
        os.makedirs(arcive_dir, exist_ok=True)
    except Exception as e:
        logging.error('Can not create archive_files_dir: {}\n{}'.format(
            config.archive_files_dir), e)
        sys.exit(7)

# Create all topics
    topics = {}
    for topic in config.topics:
        topics[topic.input_filename] = Topic(
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            topic_id=topic.topic_id,
            schema_id=topic.schema_id,
            proto_path=topic.proto_path,
            input_filename=topic.input_filename,
            batch_publish=topic.batch_publish,

            batch_max_messages=config.batch_settings.max_messages,
            batch_max_bytes=config.batch_settings.max_bytes,
            batch_max_latency=config.batch_settings.max_latency,
            batch_max_threads=config.batch_settings.max_threads
        )

while True:
    raw_files = glob.glob(config.raw_files_dir + os.path.sep + '*.tar.gz')
    logging.info('Scan all raw files :{}'.format(raw_files))
    for targz_file in raw_files:
        # Read all tar.gz files
        with tarfile.open(targz_file, 'r:gz') as tar:
            for tarinfo in tar:
                line_counter = 0
                # Read the files inside tar.gz without decompressing
                if tarinfo.isreg():
                    if tarinfo.name in topics:
                        logging.info(f'Read {tarinfo.name}.')
                        f = tar.extractfile(tarinfo.name)
                        content = f.read().decode('utf-8', errors='ignore')
                        lines = content.split('\n')
                        # Publish line by line
                        for i, line in enumerate(lines):
                            if line:
                                logging.info(
                                    f'file={tarinfo.name};line={line_counter};threads_count={threading.active_count()}')
                                topics[tarinfo.name].publish(line)
                            line_counter = line_counter+1
        # Move the processed file to archive folder
        file_name = os.path.basename(targz_file)
        dest = os.path.join(arcivedir, file_name)
        shutil.move(targz_file, dest)
    logging.info(f'Waiting the next scan ...')
    time.sleep(60)
