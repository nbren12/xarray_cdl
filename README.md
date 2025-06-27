# Xarray CDL

This library is a pure python implementation of `ncgen` that is capable of
generating xarray Datasets from CDL files. This is useful for testing and
reading CDL file stored as plain text.

## Installation

```
pip install https://github.com/nbren12/xarray_cdl/archive/main.tar.gz
```

## Usage
```python
>>> from xarray_cdl import loads, dumps
>>> s = """
...     netcdf example {   // example of CDL notation
...     dimensions:
...         lon = 3 ;
...         lat = 8 ;
...     variables:
...         float rh(lon, lat) ;
...             rh:units = "percent" ;
...             rh:long_name = "Relative humidity" ;
...     // global attributes
...         :title = "Simple example, lacks some conventions" ;
...     data:
...     rh =
...         2, 3, 5, 7, 11, 13, 17, 19,
...         23, 29, 31, 37, 41, 43, 47, 53,
...         59, 61, 67, 71, 73, 79, 83, 89 ;
...     }
...     """
>>> ds = loads(s)
>>> ds
<xarray.Dataset> Size: 96B
Dimensions:  (lon: 3, lat: 8)
Dimensions without coordinates: lon, lat
Data variables:
    rh       (lon, lat) float32 96B ...
Attributes:
    title:    Simple example, lacks some conventions
>>> print(dumps(ds))
netcdf dataset {
dimensions:
    lon = 3;
    lat = 8;
variables:
    float rh(lon, lat);
        rh:units = "percent";
        rh:long_name = "Relative humidity";
    // global attributes
        :title = "Simple example, lacks some conventions";
data:
    rh = 2.0, 3.0, 5.0, 7.0, 11.0, 13.0, 17.0, 19.0,
    23.0, 29.0, 31.0, 37.0, 41.0, 43.0, 47.0, 53.0,
    59.0, 61.0, 67.0, 71.0, 73.0, 79.0, 83.0, 89.0;
}
```

## Attribution

This code was adapted from the [Allen Institute for Artificial Intelligence's fv3net repository](https://github.com/ai2cm/fv3net/tree/master/external/vcm/vcm/cdl). The original CDL parser implementation was developed by the Allen Institute and is used here under the BSD license.
