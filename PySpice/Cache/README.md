# Cache Libraries

* http://www.grantjenks.com/docs/diskcache/index.html#comparisons

## Key-Value Stores

* [dbm](https://docs.python.org/3/library/dbm.html) is part of Python’s standard library and implements a generic interface to variants of the DBM database — dbm.gnu or dbm.ndbm. If none of these modules is installed, the slow-but-simple dbm.dumb is used.
* [shelve](https://docs.python.org/3/library/shelve.html)  is part of Python’s standard library and implements a “shelf” as a persistent, dictionary-like object. The difference with “dbm” databases is that the values can be anything that the pickle module can handle.
* [sqlitedict](https://github.com/RaRe-Technologies/sqlitedict)  is a lightweight wrapper around Python’s sqlite3 database with a simple, Pythonic dict-like interface and support for multi-thread access. Keys are arbitrary strings, values arbitrary pickle-able objects.
* [pickleDB](https://pythonhosted.org/pickleDB) is a lightweight and simple key-value store. It is built upon Python’s simplejson module and was inspired by Redis. It is licensed with the BSD three-clause license.

## Caching Libraries

* [joblib.Memory](https://joblib.readthedocs.io/en/latest/memory.html) provides caching functions and works by explicitly saving the inputs and outputs to files. It is designed to work with non-hashable and potentially large input and output data types such as numpy arrays.
* [klepto](https://pypi.org/project/klepto) extends Python’s lru_cache to utilize different keymaps and alternate caching algorithms, such as lfu_cache and mru_cache. Klepto uses a simple dictionary-sytle interface for all caches and archives.

