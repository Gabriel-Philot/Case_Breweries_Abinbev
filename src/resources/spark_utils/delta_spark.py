import pyspark
from pyspark.sql import SparkSession
from delta.pip_utils import configure_spark_with_delta_pip

# Get the version of PySpark
pyspark_version = pyspark.__version__

def initialize_spark(app_name: str = 'Airflow-PySparkDelta'):
    """
    Function to initialize a Spark session with Delta Lake.

    Args:
        app_name (str): Name of the Spark application. Defaults to 'Airflow-PySparkDelta'.

    Returns:
        SparkSession: Configured SparkSession object.
    """

    # Display initialization message
    print('=' * 120)
    print(f'{"STARTING SPARK".center(120, "=")}')
    print('=' * 120)

    # Spark session configuration with Delta Lake support
    spark = (SparkSession
             .builder
             .appName(app_name)
             .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension')
             .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog')
             .enableHiveSupport()
             )

    # Configure Delta Lake with Spark
    spark = configure_spark_with_delta_pip(spark).getOrCreate()

    # Set log level and number of shuffle partitions
    spark.sparkContext.setLogLevel('ERROR')
    spark.conf.set("spark.sql.shuffle.partitions", 8)

    # Display version information
    delta_version_info = 'Version = 3.1.0'
    pyspark_version_info = f'PySpark Version = {pyspark_version}'
    
    print('SPARK | DELTA | INITIALIZED')
    print(f'{pyspark_version_info} {delta_version_info}')

    return spark