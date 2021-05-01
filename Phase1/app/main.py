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

from topic import Topic

# convert ymal load to dict
class DictAsMember(dict):
    def __getattr__(self, name):
        value = self[name]
        if isinstance(value, dict):
            value = DictAsMember(value)
        if isinstance(value, list):
            newlist =[]
            for i in value:
                if isinstance(i, dict):
                    newlist.append(DictAsMember(i))
                else:
                    newlist.append(i)
            return newlist
        return value

if __name__ == '__main__':

    logging.getLogger().setLevel(logging.INFO)

    # Check the env variables
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is None:
        logging.error('The env GOOGLE_APPLICATION_CREDENTIALS is null')
        sys.exit(-1)
    if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
        logging.error('The env GOOGLE_CLOUD_PROJECT is null')
        sys.exit(-1)

    # Read the config schema
    try:
        with open('configschema.json', 'r') as cs:
            schemaobject = yaml.safe_load(cs)
    except IOError as e:
        logging.error('Cannot open the config schema file: {}'.format(e))
        sys.exit(-1)

    # Read the config file
    try:
        with open('config{}config.yml'.format(os.path.sep)) as ymlfile:
            configyml = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except IOError as e:
        logging.error('Cannot open the config file: {}'.format(e))
        sys.exit(-1)

    # Validate the config file
    try:
        jsonschema.validate(configyml, schemaobject)
    except Exception as e:
        logging.error(
            'An exception occurred while validating the config file\n{}'.format(e))
        sys.exit(-1)

    # Convert config to dict
    config = DictAsMember(configyml)

    # Create all topics
    topics = {}
    for topic in config.topics:
        topics[topic.input_filename]  = Topic(
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

    # Check whether raw_files_dir is an existing directory or not
    if not os.path.isdir(config.raw_files_dir):
        logging.error('Can not find raw_files_dir: {}'.format(
            config.raw_files_dir))
        sys.exit(-1)

    # Create the archive_files_dir if it is not exist
    arcivedir = config.archive_files_dir
    try:
        os.makedirs(arcivedir, exist_ok=True)
    except Exception as e:
        logging.error('Can not create archive_files_dir: {}\n{}'.format(
            config.archive_files_dir),e)
        sys.exit(-1)

    while True:
        rawfiles = glob.glob(config.raw_files_dir + os.path.sep + '*.tar.gz')
        logging.info('Scan all raw files :{}'.format(rawfiles))
        for targzfile in rawfiles:
            # Read all tar.gz files
            with tarfile.open(targzfile, 'r:gz') as tar:
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
            filename = os.path.basename(targzfile)
            dest = os.path.join(arcivedir, filename)
            shutil.move(targzfile, dest)
        logging.info(f'Waiting the next scan ...')
        time.sleep(60)
