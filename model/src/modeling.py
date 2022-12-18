import logging
import pyspark
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit, TrainValidationSplitModel
from config import Config
from utils import (
    calculate_rmse,
    saved_model_exists,
)
from data_processing import (
    prepare_for_training,
    load_data,
)

def get_model_trainer(train_ratio=0.8):
    rf = RandomForestRegressor()
   
    paramGrid = ParamGridBuilder()\
        .addGrid(rf.numTrees, [2, 3, 4, 5]) \
        .addGrid(rf.maxDepth, [5, 6, 7, 8]) \
        .build()

    return TrainValidationSplit(
        estimator=rf,
        estimatorParamMaps=paramGrid,
        evaluator=RegressionEvaluator(),
        trainRatio=train_ratio,
    )

def is_model_improved(new_model, test, hdfs_url, old_model_path):
    model_path = f'{hdfs_url}/{old_model_path}'

    pred_df = new_model.transform(test) \
        .select('label', 'prediction')

    new_rmse = calculate_rmse(pred_df, 'label', 'prediction')
    logging.critical(f'New RMSE: {new_rmse}')

    if not saved_model_exists(model_path):
        return 0
    
    old_model = TrainValidationSplitModel.load(model_path)
    old_pred_df = old_model.transform(test) \
        .select('label', 'prediction')
    old_rmse = calculate_rmse(old_pred_df, 'label', 'prediction')
    logging.critical(f'Old RMSE: {old_rmse}')

    return 1 if new_rmse < old_rmse else -1

def training_job():
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

    df = load_data(spark_session, config.hdfs_url, config.traffic_count_data_saving_path)

    train, test  = prepare_for_training(df, train_ratio=0.8)
    
    model = get_model_trainer(train_ratio=0.8).fit(train)

    is_improved = is_model_improved(model, test, config.hdfs_url, config.traffic_best_model_saving_path)
    model_path = f'{config.hdfs_url}/{config.traffic_best_model_saving_path}'
    if is_improved == 0:
        logging.critical(f'No saved model found. Saving first model to: {model_path}')
        model.save(model_path)
    elif is_improved > 0:
        logging.critical(f'Rewriting best model: {model_path}')
        model.write().overwrite().save(model_path)

    spark_session.stop()
