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
>>> from xarray_cdl import loads
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
>>> loads(s)
<xarray.Dataset> Size: 192B
Dimensions:  (lon: 3, lat: 8)
Dimensions without coordinates: lon, lat
Data variables:
    rh       (lon, lat) float64 192B ...
Attributes:
    title:    Simple example, lacks some conventions
```
