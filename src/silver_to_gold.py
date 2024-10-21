from datetime import datetime
from pathlib import Path
import json
import logging
from resources.utils.monitor import TaskMonitor
from resources.spark_utils.delta_spark import initialize_spark
import pyspark.sql.functions as F
from delta import DeltaTable


config_path = Path("src/resources/utils/configs.json")

with config_path.open('r') as config_file:
    config = json.load(config_file)

silver_layer_path = str(Path(config['paths']['silver']))
golden_layer_path = str(Path(config['paths']['gold']))

time_update_gold = 'last_updated_gold'
agregation_name = 'breweries_count'

def gold_table(spark):
    (
        DeltaTable.createIfNotExists(spark)
        .tableName("brewery_type_location")
        .location(golden_layer_path)
        .addColumn("brewery_type", "string")
        .addColumn("country", "string")
        .addColumn("state", "string")
        .addColumn("city", "string")
        .addColumn(agregation_name, "int")
        .addColumn(time_update_gold, "TIMESTAMP")
        .location(golden_layer_path)
        .execute()
    )
    
def gold_modelling(df):
   df = df.select(
       'brewery_type',
       'country',
       'state',
       'city'
    ) \
    .groupBy('brewery_type', 'country', 'state', 'city').count() \
    .withColumnRenamed('count', agregation_name) \
    .withColumn(agregation_name, F.col(agregation_name).cast("int"))
   
   return df


def execute_silver_to_gold():
    
    spark = initialize_spark()

    monitor_gold = TaskMonitor("silver_to_gold")
    monitor_gold.start()
    try:
        df_silver_data = DeltaTable.forPath(spark, silver_layer_path) \
            .toDF()
        logging.info(f' [SUCCESS] | LOAD DATA FROM {silver_layer_path}')

    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO LOAD DATA. ERROR: {str(e)}')
        raise
    
    try:
        gold_table(spark)
        logging.info(f'[SUCCESS] | CREATED GOLD TABLE IN {golden_layer_path}')

    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO CREATE GOLD TABLE. ERROR: {str(e)}')
        raise

    time_load = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    df_gold_data = gold_modelling(df_silver_data) \
        .withColumn(
            time_update_gold, F.lit(time_load).cast('timestamp')
        )
        

    try:
        # save into gold_layer
        df_gold_data.write \
            .format('delta') \
            .mode('overwrite') \
            .save(golden_layer_path)
        logging.info(f' [SUCCESS] | SAVE DATA INTO {golden_layer_path}')
        
    except Exception as e:
        logging.error(f'[ERROR] | FAILED TO SAVE DATA. ERROR: {str(e)}')
        raise
    
    monitor_gold.finish()
    spark.stop()


if __name__ == "__main__":
    execute_silver_to_gold()