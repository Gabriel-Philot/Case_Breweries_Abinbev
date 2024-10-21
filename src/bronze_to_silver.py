from datetime import datetime
from pathlib import Path
import json
import logging
from resources.utils.monitor import TaskMonitor
from resources.spark_utils.delta_spark import initialize_spark
import pyspark.sql.functions as F
from pyspark.sql.types import (
    StringType, 
    FloatType, 
    StructType, 
    StructField
)


config_path = Path("src/resources/utils/configs.json")

with config_path.open('r') as config_file:
    config = json.load(config_file)
bronze_layer_path = str(Path(config['paths']['bronze']))
silver_layer_path = str(Path(config['paths']['silver']))


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


def adjusting_column_types(df):
    """
    Adjusts the column types and sanitizes data in the given DataFrame.

    This function casts various columns in the DataFrame to specific types, 
    such as converting 'id' to IntegerType and 'latitude' and 'longitude' 
    to FloatType after replacing commas with periods. It also ensures that 
    'latitude' and 'longitude' are within valid ranges, setting them to 0.0 
    if they exceed the allowed boundaries.

    Parameters:
        df (DataFrame): Input DataFrame with columns to be adjusted.

    Returns:
        DataFrame: A new DataFrame with adjusted column types and sanitized data.
    """
    df_adjusted_type = df \
        .withColumn('id', F.col('id').cast(StringType())) \
        .withColumn('name', F.col('name').cast(StringType())) \
        .withColumn('brewery_type', F.col('brewery_type').cast(StringType())) \
        .withColumn('address_1', F.col('address_1').cast(StringType())) \
        .withColumn('address_2', F.col('address_2').cast(StringType())) \
        .withColumn('address_3', F.col('address_3').cast(StringType())) \
        .withColumn('city', F.col('city').cast(StringType())) \
        .withColumn('postal_code', F.col('postal_code').cast(StringType())) \
        .withColumn('country', F.col('country').cast(StringType())) \
        .withColumn(
            'latitude', F.regexp_replace('latitude', ',', '.').cast(FloatType())
        ) \
        .withColumn(
            'latitude', F.when(
                (F.col('latitude') > 90) | (F.col('latitude') < -90), 0.0
            ).otherwise(F.col('latitude'))
        ) \
        .withColumn(
            'longitude', F.regexp_replace('longitude', ',', '.').cast(FloatType())
        ) \
        .withColumn(
            'longitude', F.when(
                (F.col('longitude') > 180) | (F.col('longitude') < -180), 0.0
            ).otherwise(F.col('longitude'))
        ) \
        .withColumn('phone', F.col('phone').cast(StringType())) \
        .withColumn('website_url', F.col('website_url').cast(StringType())) \
        .withColumn('state', F.col('state').cast(StringType())) \
        .withColumn('street', F.col('street').cast(StringType()))

    return df_adjusted_type


def clean_columns_for_silver(df):
    """
    Cleans specific text columns in the DataFrame by:
    - Removing extra spaces
    - Converting text to lowercase
    - Removing special characters

    Args:
        df (DataFrame): The Spark DataFrame.

    Returns:
        DataFrame: A DataFrame with cleaned columns.
    """
    columns_to_clean = ['address_1', 'address_2', 'address_3', 'city', 
                        'country', 'state', 'street']
    
    for column in columns_to_clean:
        df = df.withColumn(
            column,
            F.lower(F.trim(F.regexp_replace(F.col(column), '[^a-zA-Z0-9 ]', '')))
        )
    
    return df


def execute_bronze_to_silver():
    
    spark = initialize_spark()

    monitor_silver = TaskMonitor("bronze_to_silver")
    monitor_silver.start()
    try:
        df_raw_data = spark \
            .read.schema(_SCHEMA_RAW_DATA).json(bronze_layer_path, multiLine=True)
        logging.info(f' [SUCCESS] | LOAD DATA FROM {bronze_layer_path}')
    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO LOAD DATA. ERROR: {str(e)}')
        raise
    
    # After reviewing, 'state_province' is identical to 'state', so we can drop it.
    df_raw_data = df_raw_data.drop('state_province')

    df_silver = adjusting_column_types(df_raw_data)
    df_silver = clean_columns_for_silver(df_silver)

    # adding 'last_updated_silver'
    time_load = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    df_silver = df_silver \
        .withColumn(
                'last_updated_silver', F.lit(time_load).cast('timestamp')
        ).distinct() # removing duplicates
    

    try:
        # save into silver_layer
        df_silver.write \
            .format('delta') \
            .mode('overwrite') \
            .option('path', silver_layer_path) \
            .partitionBy('country') \
            .save()

        logging.info(f'[SUCCESS] | SAVE DATA INTO {silver_layer_path}')
    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO SAVE DATA INTO. ERROR: {str(e)}')
        raise

    monitor_silver.finish()

    # Stop the Spark session
    spark.stop()


if __name__ == '__main__':
    execute_bronze_to_silver()