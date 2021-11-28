# Simulation Export Formats

* (HDF5)[https://www.hdfgroup.org/solutions/hdf5] is a high-performance data management and storage suite.
  It supports multidimensional arrays, data attributes and a kind of file system hierarchy.
  Moreover, it features high-performance IO and many data compression algorithms.
  These features permit to serialise efficiently numerical data objects.
  HDF5 is well known in Python, thanks to the (H5py)[https://www.h5py.org] library which plugs HDF5 with Python and NumPy.
* (I/O with NumPy)[https://numpy.org/doc/stable/user/basics.io.html]
  NumPy provides low level functions.
* JSON can be used to serialise numerical data objects in text format.  However, it will be
  inefficient to save large double-format float array in text.  A solution is to pack the data in a
  blob string.  But in comparison to HDF5, JSON is not well suited for this purpose.
* CSV is another well known solution to store row-column data.  But in comparison to JSON, CSV is not suited to serialise complex data.
