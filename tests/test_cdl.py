# BSD License
# 
# Copyright (c) 2019, The Allen Institute for Artificial Intelligence
# Copyright (c) 2025, Noah D. Brenowitz
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import numpy as np
import lark
import xarray as xr
from xarray_cdl.parser import grammar as parser
from xarray_cdl.generate import DatasetVisitor
from xarray_cdl import loads, dumps
import pytest


def test_loads_with_coord():
    ds = loads(
    """
    netcdf Some Data {
    dimensions:
        time = 3;
        x = 4;
    variables:
        long time(time);
        float a(time, x);
    }
    """
    )

def test_get_data():

    ds = loads(
        """
    netcdf Some Data {
    dimensions:
        time = 3;
        x = 4;
    variables:
        int time(time);
        int b;
        double a(time, x);
            a:_FillValue = 0;
            a:foo = "bar";
    // a comment

    :global_attr = 1;

    data:
        time = 1,2,3;
        b = 3;
    }
    """
    )

    assert ds["a"].dims == ("time", "x")
    assert np.all(np.isnan(ds["a"]))
    assert ds["time"].values.tolist() == [1, 2, 3]
    assert ds.a.foo == "bar"
    assert ds.b.item() == 3
    assert ds.global_attr == 1


def test_dumps_basic():
    """Test basic dumps functionality"""
    ds = xr.Dataset(
        data_vars={'temp': (['lat', 'lon'], [[1.0, 2.0], [3.0, 4.0]])},
        coords={'lat': [0, 1], 'lon': [0, 1]},
        attrs={'title': 'Temperature data'}
    )
    
    cdl = dumps(ds, "temperature")
    
    # Check that the CDL contains expected elements
    assert "netcdf temperature {" in cdl
    assert "dimensions:" in cdl
    assert "lat = 2;" in cdl
    assert "lon = 2;" in cdl
    assert "variables:" in cdl
    assert "double temp(lat, lon);" in cdl
    assert "long lat(lat);" in cdl
    assert "long lon(lon);" in cdl
    assert ":title = \"Temperature data\";" in cdl
    assert "data:" in cdl
    assert "temp =" in cdl


@pytest.mark.parametrize('dtype', ['f4', 'f8', 'i4', 'i8'])
def test_dumps_loads_roundtrip(dtype):
    """Test that dumps and loads are inverse operations"""
    # Create a simple dataset
    temp_data = np.array([[1, 2, 3], [4, 5, 6]], dtype=dtype)
    ds = xr.Dataset(
        data_vars={
            'temperature': (['time', 'lat'], temp_data),
            'pressure': (['time'], [1013, 1014])
        },
        coords={
            'time': [0, 1],
            'lat': [0, 1, 2]
        },
        attrs={
            'title': 'Test dataset',
            'version': 1.0
        }
    )
    
    # Add some variable attributes
    ds.temperature.attrs['units'] = 'celsius'
    ds.pressure.attrs['units'] = 'hPa'
    
    # Convert to CDL and back
    cdl = dumps(ds, "test")
    ds_roundtrip = loads(cdl)
    
    # Check that the datasets are equivalent
    xr.testing.assert_equal(ds, ds_roundtrip)

    for v in ds.data_vars:
        assert ds[v].dtype == ds_roundtrip[v].dtype


def test_dumps_with_nan():
    """Test dumps handles NaN values correctly"""
    ds = xr.Dataset(
        data_vars={'data': (['x'], [1.0, np.nan, 3.0])},
        coords={'x': [0, 1, 2]},
        attrs={'has_nan': True}
    )
    
    cdl = dumps(ds, "nan_test")
    
    # Check that NaN is properly formatted
    assert "NaN" in cdl
    assert "1.0, NaN, 3.0;" in cdl


def test_dumps_empty_dataset():
    """Test dumps with an empty dataset"""
    ds = xr.Dataset()
    cdl = dumps(ds, "empty")
    
    assert "netcdf empty {" in cdl
    assert "dimensions:" in cdl
    assert "variables:" in cdl
    assert "data:" in cdl


def test_dumps_scalar_variable():
    """Test dumps with scalar variables"""
    ds = xr.Dataset(
        data_vars={'scalar': 42},
        attrs={'description': 'A scalar value'}
    )
    
    cdl = dumps(ds, "scalar_test")
    
    assert "long scalar;" in cdl
    assert "scalar = 42;" in cdl


def test_lark():

    cdl_parser = lark.Lark(parser, start="dimensions")
    print(cdl_parser.parse("dimensions: a = 1; b=3;"))

    cdl_parser = lark.Lark(parser, start="variables")
    print(cdl_parser.parse("variables: float a(x,y); int b(y); int c;"))

    cdl_parser = lark.Lark(parser, start="variables")
    print(cdl_parser.parse("variables: float a(x,y); a:someAttr = 0; int b(y);"))

    cdl_parser = lark.Lark(parser, start="value")
    print(cdl_parser.parse("NaN"))

    cdl_parser = lark.Lark(parser, start="datum")
    print(cdl_parser.parse("time =  1, 2, 3;"))

    cdl_parser = lark.Lark(parser, start="netcdf")
    tree = cdl_parser.parse(
        """
    netcdf Some Data {
    dimensions:
        time = 3;
        x = 4;
    variables:
        int time(time);
        double a(time, x);
            a:_FillValue = 0;

    data:
        time = 1,2,3;
    }
    """
    )
    print(tree)

    tree = cdl_parser.parse(
        """
    netcdf Some Data {
    dimensions:
        time = 3;
        x = 4;
    variables:
        int time(time);
        double a(time, x);
            a:_FillValue = 0;

    data:
        time = 1,2,3;
        x = 1,2,3,4;
    group: SubGroup {
        dimensions:
            time = 1;
        variables:
            int time(time);
    }
    }
    """
    )
    print(tree.pretty())


def test_parse_data_value():
    cdl_parser = lark.Lark(parser, start="variable_decl")
    tree = cdl_parser.parse("float a(x,y);")
    v = DatasetVisitor()
    v.visit(tree)
    assert v._variable_dtype["a"] == np.float32
    assert v._variable_dims["a"] == ["x", "y"]


def test_Visitor():
    cdl_parser = lark.Lark(parser, start="netcdf")
    cdl = """netcdf Some Data {
    dimensions:
        time = 3;
        x = 4;
    variables:
        int time(time);
        double a(time, x);
            a:_FillValue = 0;
            time:somefun = NaN;

    data:
        time = 1,2,3;
    }"""
    tree = cdl_parser.parse(cdl)
    v = DatasetVisitor()
    v.visit(tree)
    assert v._dims == {"time": 3, "x": 4}

    assert v._variable_attrs["a"] == {"_FillValue": 0}
    assert np.isnan(v._variable_attrs["time"]["somefun"])
