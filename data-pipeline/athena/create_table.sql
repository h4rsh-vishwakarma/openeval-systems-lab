-- Point LOCATION at the uploaded Parquet prefix. Run MSCK REPAIR TABLE after upload.
CREATE EXTERNAL TABLE IF NOT EXISTS openeval_trades (
  event_id string,
  parsed_at timestamp,
  price double,
  quantity int
)
PARTITIONED BY (symbol string, year int, month int)
STORED AS PARQUET
LOCATION 's3://REPLACE_BUCKET/trades/';
