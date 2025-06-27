# BSD License
# 
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
import xarray


def _format_value(value):
    """Format a value for CDL output"""
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, (int, float)):
        if np.isnan(value):
            return "NaN"
        return str(value)
    elif isinstance(value, bool):
        return str(int(value))
    else:
        return str(value)


def _format_data_array(data, max_items_per_line=8):
    """Format a data array for CDL output"""
    if data.size == 0:
        return ""
    
    # Flatten the array and convert to list
    flat_data = data.ravel()
    
    # Format each value
    formatted_values = []
    for val in flat_data:
        if np.isnan(val):
            formatted_values.append("NaN")
        elif isinstance(val, (int, float)):
            formatted_values.append(str(val))
        else:
            formatted_values.append(str(val))
    
    # Split into lines
    lines = []
    for i in range(0, len(formatted_values), max_items_per_line):
        line_values = formatted_values[i:i + max_items_per_line]
        lines.append(", ".join(line_values))
    
    return ",\n    ".join(lines)


def _get_dtype_string(dtype):
    """Convert numpy dtype to CDL dtype string"""
    dtype_str = str(dtype)
    if dtype_str.startswith('float'):
        if dtype_str == 'float64':
            return 'double'
        else:
            return 'float'
    elif dtype_str.startswith('int'):
        if dtype_str == 'int64':
            return 'long'
        else:
            return 'int'
    elif dtype_str.startswith('uint'):
        return 'int'
    elif dtype_str == 'bool':
        return 'byte'
    elif dtype_str.startswith('str') or dtype_str.startswith('object'):
        return 'char'
    else:
        return 'float'  # default fallback


def dumps(ds: xarray.Dataset, name: str = "dataset") -> str:
    """Convert an xarray Dataset into a CDL string

    This is the reverse operation of `loads`. It converts an xarray Dataset
    back to the UCAR Common Data Language (CDL) format.

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset to convert to CDL format
    name : str, optional
        The name for the netCDF file in the CDL output, default is "dataset"

    Returns
    -------
    str
        The CDL representation of the dataset

    Examples
    --------
    >>> import xarray as xr
    >>> ds = xr.Dataset(
    ...     data_vars={'temp': (['lat', 'lon'], [[1, 2], [3, 4]])},
    ...     coords={'lat': [0, 1], 'lon': [0, 1]},
    ...     attrs={'title': 'Temperature data'}
    ... )
    >>> cdl = dumps(ds, "temperature")
    >>> print(cdl)
    netcdf temperature {
    dimensions:
        lat = 2;
        lon = 2;
    variables:
        float temp(lat, lon);
        float lat(lat);
        float lon(lon);
    // global attributes
        :title = "Temperature data";
    data:
        temp =
            1, 2,
            3, 4;
        lat = 0, 1;
        lon = 0, 1;
    }
    """
    lines = [f"netcdf {name} {{"]
    
    # Dimensions section
    lines.append("dimensions:")
    for dim in ds.dims:
        size = ds.sizes[dim]
        lines.append(f"    {dim} = {size};")
    
    # Variables section
    lines.append("variables:")
    
    # Add coordinate variables first
    for coord_name, coord_var in ds.coords.items():
        dtype_str = _get_dtype_string(coord_var.dtype)
        if coord_var.dims:
            dims_str = "(" + ", ".join(coord_var.dims) + ")"
        else:
            dims_str = ""
        lines.append(f"    {dtype_str} {coord_name}{dims_str};")
    
    # Add data variables
    for var_name, var in ds.data_vars.items():
        dtype_str = _get_dtype_string(var.dtype)
        if var.dims:
            dims_str = "(" + ", ".join(var.dims) + ")"
        else:
            dims_str = ""
        lines.append(f"    {dtype_str} {var_name}{dims_str};")
    
    # Variable attributes
    for var_name, var in ds.coords.items():
        for attr_name, attr_value in var.attrs.items():
            lines.append(f"        {var_name}:{attr_name} = {_format_value(attr_value)};")
    
    for var_name, var in ds.data_vars.items():
        for attr_name, attr_value in var.attrs.items():
            lines.append(f"        {var_name}:{attr_name} = {_format_value(attr_value)};")
    
    # Global attributes
    if ds.attrs:
        lines.append("    // global attributes")
        for attr_name, attr_value in ds.attrs.items():
            lines.append(f"        :{attr_name} = {_format_value(attr_value)};")
    
    # Data section
    lines.append("data:")
    
    # Add coordinate data
    for coord_name, coord_var in ds.coords.items():
        if coord_var.size > 0:
            data_str = _format_data_array(coord_var.values)
            lines.append(f"    {coord_name} = {data_str};")
    
    # Add variable data
    for var_name, var in ds.data_vars.items():
        if var.size > 0:
            data_str = _format_data_array(var.values)
            lines.append(f"    {var_name} = {data_str};")
    
    lines.append("}")
    
    return "\n".join(lines) 
