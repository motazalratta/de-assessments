import yaml
import os
import glob
import tarfile
import sys
import logging
import shutil
import time
import threading

from topic import Topic

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is None:
        print('the env GOOGLE_APPLICATION_CREDENTIALS is null')
        sys.exit(-1)

    if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
        print('the env GOOGLE_CLOUD_PROJECT is null')
        sys.exit(-1)

    try:
        with open("config/config.yml", "r") as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    except IOError as e:
        print('Cannot open the config file: {}'.format(e))
        sys.exit(1)

    batch_max_messages = config['pubsub']["batch_settings"]["max_messages"]
    batch_max_bytes    = config['pubsub']["batch_settings"]["max_bytes"]
    batch_max_latency  = config['pubsub']["batch_settings"]["max_latency"]
    batch_max_threads  = config['pubsub']["batch_settings"]["max_threads"]
    
    topics= {}
    for topic in config['pubsub']['topics'].values():
        topics[topic["input_filename"]] = Topic(os.environ.get('GOOGLE_CLOUD_PROJECT'),topic["topic_id"],
                                                topic["schema_id"],topic["proto_path"],topic["input_filename"],
                                                topic["batch_publish"], batch_max_messages, batch_max_bytes, batch_max_latency,batch_max_threads
                                                )

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
                    line_counter=0
                    if tarinfo.isreg():
                        if tarinfo.name in topics:
                            logging.info(f"Read {tarinfo.name}.")
                            f = tar.extractfile(tarinfo.name)  
                            content = f.read().decode('utf-8', errors='ignore')
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if line:
                                    logging.info(f"file={tarinfo.name};line={line_counter};threads_count={threading.active_count()}")
                                    topics[tarinfo.name].publish(line)
                                line_counter=line_counter+1
            # move the processed file to archive
            filename = os.path.basename(targzfile)
            dest = os.path.join(arcivedir,filename)
            shutil.move(targzfile,dest)
        logging.info(f"Waiting the next scan ...")
        time.sleep(60)
            