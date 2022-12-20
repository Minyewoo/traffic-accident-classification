from pyspark.ml.tuning import TrainValidationSplitModel   
from pyspark.sql import functions as F

def saved_model_exists(path):
    try:
        TrainValidationSplitModel.load(path)
        return True
    except Exception:
        return False
