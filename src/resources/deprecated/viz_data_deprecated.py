# Only for dev purposes

from datetime import datetime
from pathlib import Path
import json
import logging
from resources.utils.utils import log_header
from resources.spark_utils.delta_spark import initialize_spark
import pyspark.sql.functions as F
from delta import DeltaTable
from pyspark.sql.types import (
    StringType, 
    StructType, 
    StructField
)

config_path = Path("src/resources/utils/configs.json")

with config_path.open('r') as config_file:
    config = json.load(config_file)

bronze_layer_path = str(Path(config['paths']['bronze']))
silver_layer_path = str(Path(config['paths']['silver']))
golden_layer_path = str(Path(config['paths']['gold']))


_SCHEMA_RAW_DATA = StructType([
    StructField('id',             StringType(), False),
    StructField('name',           StringType(), True),
    StructField('brewery_type',   StringType(), True),
    StructField('address_1',      StringType(), True),
    StructField('address_2',      StringType(), True),
    StructField('address_3',      StringType(), True),
    StructField('city',           StringType(), True),
    StructField('state_province', StringType(), True),
    StructField('postal_code',    StringType(), True),
    StructField('country',        StringType(), True),
    StructField('longitude',      StringType(), True),
    StructField('latitude',       StringType(), True),
    StructField('phone',          StringType(), True),
    StructField('website_url',    StringType(), True),
    StructField('state',          StringType(), True),
    StructField('street',         StringType(), True),
])


def execute_viz_data_bronze():
    spark = initialize_spark()
    msg = "Bronze Data Viz"
    log_header(msg)
    try:
        df_bronze_data = spark \
            .read.schema(_SCHEMA_RAW_DATA).json(bronze_layer_path, multiLine=True)
        logging.info(f' [SUCCESS] | LOAD DATA FROM {bronze_layer_path}')
    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO LOAD DATA. ERROR: {str(e)}')
        raise

    df_bronze_data.printSchema()
    df_bronze_data.show()

    var_num_rows = df_bronze_data.count()

    logging.info(f' [BRONZE LAYERS | DATAFRAME HAS {var_num_rows} ROWS')

    spark.stop()

def execute_viz_data_silver():
    spark = initialize_spark()
    msg = "Silver Data Viz"
    log_header(msg)
    try:
        df_silver_data = DeltaTable.forPath(spark, silver_layer_path) \
            .toDF()
        logging.info(f' [SUCCESS] | LOAD DATA FROM {silver_layer_path}')

    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO LOAD DATA. ERROR: {str(e)}')
        raise

    df_silver_data.printSchema()
    df_silver_data.show()

    var_num_rows = df_silver_data.count()

    logging.info(f' [SILVER LAYERS | DATAFRAME HAS {var_num_rows} ROWS')

    spark.stop()

def execute_viz_data_gold():
    spark = initialize_spark()
    msg = "Gold Data Viz"
    log_header(msg)
    try:
        df_gold_data = DeltaTable.forPath(spark, golden_layer_path) \
            .toDF()
        logging.info(f' [SUCCESS] | LOAD DATA FROM {golden_layer_path}')

    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO LOAD DATA. ERROR: {str(e)}')
        raise

    df_gold_data.printSchema()
    df_gold_data_ordered = df_gold_data.orderBy(F.col("breweries_count").desc())
    df_gold_data_ordered.show()

    var_num_rows = df_gold_data.count()

    logging.info(f' [GOLD LAYERS | DATAFRAME HAS {var_num_rows} ROWS')

    spark.stop()

    
