# Architecture

CSV ingestion → unique-key validation → schema profiling → key alignment → cell comparison → business rules → Excel evidence.

The source is the denominator for key match rate. Matched keys do not imply matching values. Null equals null; numeric tolerance is absolute. Schema differences are reported separately. Duplicate or null keys stop processing rather than silently multiplying rows. The engine is in-memory and has not been benchmarked at enterprise scale. CSV types are inferred; normalize identifiers and dates upstream. No corporate code or data is included.
