####################################################################################################

from pathlib import Path
import pickle
# import sha

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from SimulateCircuit import simulate_circuit

from diskcache import Cache

####################################################################################################

analysis = simulate_circuit()

directory = Path('simulation-cache')
cache = Cache(directory)
print(cache.directory)
cache['key'] = analysis
cache.close()

####################################################################################################

# data = pickle.dumps(analysis)

# import codecs
# import os
# hex_name = codecs.encode(os.urandom(16), 'hex').decode('utf-8')
#   '688641106aa7371cf922696cff3e7646'

# with open('simulation-cache/fd/40/d3fe94030bf7d085fc1843946f29.val', 'rb') as fh:
#     data = pickle.load(fh)
#     print(data)

####################################################################################################

# /tmp/diskcache-f_zbph_0/cache.db

# simulation-cache/
# simulation-cache/fd
# simulation-cache/fd/40
# simulation-cache/fd/40/d3fe94030bf7d085fc1843946f29.val
# simulation-cache/cache.db

# PRAGMA foreign_keys=OFF;
# BEGIN TRANSACTION;
# CREATE TABLE Settings ( key TEXT NOT NULL UNIQUE, value);
# INSERT INTO Settings VALUES('count',1);
# INSERT INTO Settings VALUES('size',969750);
# INSERT INTO Settings VALUES('hits',0);
# INSERT INTO Settings VALUES('misses',0);
# INSERT INTO Settings VALUES('statistics',0);
# INSERT INTO Settings VALUES('tag_index',0);
# INSERT INTO Settings VALUES('eviction_policy','least-recently-stored');
# INSERT INTO Settings VALUES('size_limit',1073741824);
# INSERT INTO Settings VALUES('cull_limit',10);
# INSERT INTO Settings VALUES('sqlite_auto_vacuum',1);
# INSERT INTO Settings VALUES('sqlite_cache_size',8192);
# INSERT INTO Settings VALUES('sqlite_journal_mode','wal');
# INSERT INTO Settings VALUES('sqlite_mmap_size',67108864);
# INSERT INTO Settings VALUES('sqlite_synchronous',1);
# INSERT INTO Settings VALUES('disk_min_file_size',32768);
# INSERT INTO Settings VALUES('disk_pickle_protocol',5);
# CREATE TABLE Cache ( rowid INTEGER PRIMARY KEY, key BLOB, raw INTEGER, store_time REAL, expire_time REAL, access_time REAL, access_count INTEGER DEFAULT 0, tag BLOB, size INTEGER DEFAULT 0, mode INTEGER DEFAULT 0, filename TEXT, value BLOB);
# INSERT INTO Cache VALUES(1,'key',1,1637861477.2621181011,NULL,1637861477.2621181011,0,NULL,969750,4,'fd/40/d3fe94030bf7d085fc1843946f29.val',NULL);
# CREATE UNIQUE INDEX Cache_key_raw ON Cache(key, raw);
# CREATE INDEX Cache_expire_time ON Cache (expire_time);
# CREATE INDEX Cache_store_time ON Cache (store_time);
# CREATE TRIGGER Settings_count_insert AFTER INSERT ON Cache FOR EACH ROW BEGIN UPDATE Settings SET value = value + 1 WHERE key = "count"; END;
# CREATE TRIGGER Settings_count_delete AFTER DELETE ON Cache FOR EACH ROW BEGIN UPDATE Settings SET value = value - 1 WHERE key = "count"; END;
# CREATE TRIGGER Settings_size_insert AFTER INSERT ON Cache FOR EACH ROW BEGIN UPDATE Settings SET value = value + NEW.size WHERE key = "size"; END;
# CREATE TRIGGER Settings_size_update AFTER UPDATE ON Cache FOR EACH ROW BEGIN UPDATE Settings SET value = value + NEW.size - OLD.size WHERE key = "size"; END;
# CREATE TRIGGER Settings_size_delete AFTER DELETE ON Cache FOR EACH ROW BEGIN UPDATE Settings SET value = value - OLD.size WHERE key = "size"; END;
# COMMIT;
