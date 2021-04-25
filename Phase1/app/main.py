import yaml
import os
import glob
import tarfile
import sys
import logging
import shutil
import time

from topic import Topic

if __name__ == '__main__':
    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is None:
        print('the env GOOGLE_APPLICATION_CREDENTIALS is null')
        sys.exit(-1)

    if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
        print('the env GOOGLE_CLOUD_PROJECT is null')
        sys.exit(-1)

    logging.getLogger().setLevel(logging.INFO)
    try:
        with open("config.yml", "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except IOError as e:
        print('Cannot open the config file: {}'.format(e))
        sys.exit(1)

    topics= {}
    for topic in config['pubsub']['topics'].values():
        topics[topic["input_filename"]] = Topic(os.environ.get('GOOGLE_CLOUD_PROJECT'),topic["topic_id"],topic["schema_id"],topic["proto_path"],topic["input_filename"])

    arcivedir=config['pubsub']['archive_file_dir']
    if not os.path.exists(arcivedir):
        os.mkdir(arcivedir)

    
    while True:
        rawfiles=glob.glob(config['pubsub']['raw_file_dir']+'/*.tar.gz')
        logging.info(f"Scan all raw files :{rawfiles}")
        for targzfile in rawfiles:
            # process the file
            with tarfile.open(targzfile, "r:gz") as tar:
                for tarinfo in tar:
                    if tarinfo.isreg():
                        if tarinfo.name in topics:
                            logging.info(f"Read {tarinfo.name}.")
                            f = tar.extractfile(tarinfo.name)  
                            content = f.read().decode('utf-8', errors='ignore')
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                topics[tarinfo.name].publish(line)
            # move the processed file to archive
            shutil.move(targzfile,arcivedir)
        logging.info(f"Waiting the next scan ...")
        time.sleep(60)
            