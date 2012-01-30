-- HOWTO:
-- mysql -uroot -p < DB_CREATE.sql

CREATE DATABASE monlog;
USE monlog;
CREATE USER 'monlog'@'localhost' IDENTIFIED BY 'monlog123';
GRANT CREATE,ALTER TABLE,DELETE,SELECT,UPDATE,INSERT ON monlog.* TO 'monlog';