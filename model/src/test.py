# while True:
#     pass

import pyspark
from pyspark.sql import SparkSession, functions as F
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import LinearRegression
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit
from config import Config

def load_data_from_hdfs(spark_session, hdfs_url, path, header=True):
    data = spark_session.read.csv(
        f'{hdfs_url}/{path}',
        header=header,
    )

    return data

def convert_to_df(data, spark_session):
    data_rdd = spark_session.sparkContext.parallelize(data)
    data_df = spark_session.read.json(data_rdd)

    return data_df

config = Config()


spark_conf = pyspark.SparkConf()
spark_conf.setAll(
    [
        ('spark.master', config.spark_master_url),
        ('spark.app.name', 'model-testing'),
        ('spark.submit.deployMode', 'client'),
        ('spark.driver.host', config.spark_driver_host),
        ('dfs.block.size', config.hdfs_block_size),
        ('spark.sql.sources.partitionOverwriteMode', 'dynamic'),
    ]
)
spark_session = SparkSession.builder \
        .config(conf=spark_conf) \
        .getOrCreate()


if __name__ == '__main__':
    data_df = load_data_from_hdfs(spark_session, config.hdfs_url, config.data_saving_path)
    data_df.show()
    # df = convert_to_df(data, spark_session)
    # df = spark_session.read.options(header='True', inferSchema='True', delimiter=',') \
    #     .csv( f'{config.hdfs_url}/{config.data_saving_path}') \
    #     .drop('id') \
    #     .drop('city_name') \
    #     .withColumn('hour', F.date_format(F.col('date'), 'k')) \
    #     .drop('date') \
    #     .drop('weather_type') \
    #     .drop('wind_direction') \

    # train, test = df.randomSplit([0.9, 0.1], seed=12345)

    # lr = LinearRegression(maxIter=10)

    # paramGrid = ParamGridBuilder()\
    #     .addGrid(lr.regParam, [0.1, 0.01]) \
    #     .addGrid(lr.fitIntercept, [False, True])\
    #     .addGrid(lr.elasticNetParam, [0.0, 0.5, 1.0])\
    #     .build()

    # tvs = TrainValidationSplit(estimator=lr,
    #     estimatorParamMaps=paramGrid,
    #     evaluator=RegressionEvaluator(),
    #     trainRatio=0.8)

    # model = tvs.fit(train)

    # model.transform(test) \
    #     .show()
    #df.show()
    #data = range(10)
    #dist_data = spark_session.sparkContext.parallelize(data)

    #print(dist_data.reduce(lambda a, b: a+b))
    spark_session.stop()