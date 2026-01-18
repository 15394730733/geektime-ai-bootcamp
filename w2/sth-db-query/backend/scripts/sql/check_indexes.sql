-- 检查并创建缺失的索引
USE test_db;

-- 检查 database_metadata 的索引
SELECT 'database_metadata 索引:' AS info;
SHOW INDEX FROM database_metadata;

-- 检查 query_history 的索引
SELECT 'query_history 索引:' AS info;
SHOW INDEX FROM query_history;

-- 检查 database_connections 的索引
SELECT 'database_connections 索引:' AS info;
SHOW INDEX FROM database_connections;
