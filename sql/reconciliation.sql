-- DuckDB example; run from repository root.
CREATE OR REPLACE VIEW source_data AS SELECT * FROM read_csv_auto('data/source.csv');
CREATE OR REPLACE VIEW target_data AS SELECT * FROM read_csv_auto('data/target.csv');
SELECT coalesce(a.id,b.id) AS id,
CASE WHEN a.id IS NULL THEN 'target_only' WHEN b.id IS NULL THEN 'source_only'
WHEN a.amount IS DISTINCT FROM b.amount OR a.category IS DISTINCT FROM b.category THEN 'different'
ELSE 'equal' END AS status
FROM source_data a FULL OUTER JOIN target_data b ON a.id=b.id;
