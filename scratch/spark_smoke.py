from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

builder = (
    SparkSession.builder.appName("hadur-silver-practice")
    .master("local[*]")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .config("spark.sql.session.timeZone", "UTC")
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()

df = spark.read.format("delta").load("data/bronze/meridian_health/encounters")
print(df.count())  # expect 6484
df.printSchema()
