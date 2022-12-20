from pyspark.ml.tuning import TrainValidationSplitModel   
from pyspark.sql import functions as F

def saved_model_exists(path):
    try:
        TrainValidationSplitModel.load(path)
        return True
    except Exception:
        return False

def calculate_rmse(old_df, actual_column, prediction_column):
    RMSE = F.udf(lambda x, y: ((x - y) ** 2))
    old_df = old_df.withColumn(
        "RMSE", RMSE(F.col(actual_column), F.col(prediction_column))
    )
    rmse = old_df.select(F.avg('RMSE') ** 0.5).collect()
    rmse = rmse[0]['POWER(avg(RMSE), 0.5)']
    return rmse
