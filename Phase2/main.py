import argparse
import json
import logging
import sys
import random

import apache_beam as beam
import pandas as pd
import flat_table as ft

from apache_beam.io import ReadFromText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam import pvalue
from apache_beam import PTransform
from datetime import datetime

class JobOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            "--input_topic",
            type=str,
            help="The Cloud Pub/Sub topic to read from."
        )
        parser.add_argument(
            "--bigquery_table",
            type=str,
            help="Bigquery Table to write raw salesforce data",
        )
        parser.add_argument(
            "--bigquery_deadletter_table",
            type=str,
            help="Bigquery Table to write deadletters",
        )

class AddTimestamps(beam.DoFn):
    def process(self, element, publish_time=beam.DoFn.TimestampParam):
        logging.getLogger().setLevel(logging.INFO)
        try:
            payload = json.loads(element.decode("utf-8"))
            payload.update({"md_publishtime":datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
            payload.update({"md_inserttime":"AUTO"})
            yield payload
        except (ValueError, AttributeError) as e:
            logging.info(f"[Invalid Data] ({e}) - {element}")
            pass

class Normalization(beam.DoFn):
    BAD_TAG = 'BAD_NORMALIZATION_TAG'
    GOOD_TAG = 'GOOD_NORMALIZATION_TAG'

    def process(self, element):
        logging.getLogger().setLevel(logging.INFO)
        dataframe = ft.normalize(pd.DataFrame([element]))
        dataframe.columns = dataframe.columns.str.replace('.', '_')
        if dataframe.isnull().values.any():
            yield pvalue.TaggedOutput(self.BAD_TAG, element)  
        else:
            yield pvalue.TaggedOutput(self.GOOD_TAG, dataframe.to_dict(orient='records'))  

class BadRecordEncapsulation(beam.DoFn):
    def build_db_row(self, line, note):
        return  { 'datetime': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f") ,
                  'problematicrow': json.dumps(line),
                  'note' : note
                } 
    def process(self, element, note):
        if type(element) is tuple:
                if len(element)>1:
                    yield self.build_db_row(element[1],note + " tablename: " + element[0])
                else:
                    yield self.build_db_row(element[1],note)
        else: 
            yield self.build_db_row(element,note)

class WriteDeadLetterToBQ(PTransform):
    def __init__(self, options, error_note):
        self.options = options
        self.error_note = error_note

    def expand(self, pcoll):
        return (
            pcoll
            | "BadRecordEncapsulation" >> beam.ParDo(BadRecordEncapsulation(),self.error_note)
            | "BadRecordWriteToBQ" >> beam.io.WriteToBigQuery(self.options.bigquery_deadletter_table,
                                                              write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                                                              insert_retry_strategy=beam.io.gcp.bigquery_tools.RetryStrategy.RETRY_ON_TRANSIENT_ERROR
                                                             )
        )

def run(argv):
    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args()
    pipeline_options = PipelineOptions(pipeline_args, save_main_session=True, streaming=True)
    options = pipeline_options.view_as(JobOptions)

    def flatten_list(elements):
        for line in elements:
            # remove the index column which added by pandas
            dic=json.loads(json.dumps(line))
            dic.pop('index', None)
            yield dic

    with beam.Pipeline(options=pipeline_options) as pipeline:
        records = (
               pipeline
                | "ReadPubSubMessages" >> beam.io.ReadFromPubSub(topic=options.input_topic)
                | "AddTimestamps" >> beam.ParDo(AddTimestamps())
                )
        
        normalized_records_result = (records | beam.ParDo(Normalization()).with_outputs(Normalization.BAD_TAG,Normalization.GOOD_TAG))     

        normalized_bad_records = (normalized_records_result[Normalization.BAD_TAG] 
                                   | "NormalizedWriteDeadLetterToBQ" >> WriteDeadLetterToBQ(options,"Couldn't do the normaliztion")
                                 )
        normalized_good_records = (normalized_records_result[Normalization.GOOD_TAG] 
                                   | "FlattenList" >> beam.FlatMap(flatten_list)
                                   | "WriteToBigQuery" >> beam.io.WriteToBigQuery(options.bigquery_table,
                                                                                  write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                                                                                  insert_retry_strategy=beam.io.gcp.bigquery_tools.RetryStrategy.RETRY_ON_TRANSIENT_ERROR
                                                                                 )
                                  )
        
        (normalized_good_records[beam.io.gcp.bigquery.BigQueryWriteFn.FAILED_ROWS]
             | 'LoadWriteDeadLetterToBQ' >>  WriteDeadLetterToBQ(options,"Couldn't write to the main table")
        )

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run(sys.argv)