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
"""An Extended Backus-Naur (EBNF) grammar for the CDL format

This grammar can be used with the `lark`_ library to build a parser. lark is a
small pure python library with no dependencies so it is easy to install. Using a
pure python implementation will also allow us to generate lazily-loaded datasets
without interacting with the filesystem.

To learn more, see this `tutorial`_  on how to build a json parser.

.. _lark: https://github.com/lark-parser/lark
.. _tutorial: https://lark-parser.readthedocs.io/en/latest/json_tutorial.html

"""
grammar = r"""

// top level section
?netcdf: "netcdf" symbol* bracket
group: "group" ":" symbol bracket
?bracket: "{" (dimensions | variables | data | group)* "}"

// dimensions
dimensions: "dimensions" ":" [dimension_pair*]
dimension_pair: dim "=" dim_size ";"
?dim : CNAME
?dim_size: INT
    | "UNLIMITED"

// variables
variables: "variables" ":" [variable*]
?variable: (variable_decl | variable_attr)
?variable_decl: dtype symbol [var_dims] ";"
var_dims: "(" dim("," dim)* ")"
?variable_attr: [symbol] ":" symbol "=" value ";"
dtype: "float"  -> float
    | "double"  -> double
    | "int" -> int
    | "char"  -> char
    | "byte"  -> byte
    | "int64" -> int64

// data
data: "data" ":" [datum*]
datum: symbol "=" list ";"
list: data_value("," data_value)*
?data_value: value | "_"

// General purpose
?symbol: CNAME
?value: SIGNED_NUMBER -> num
    | ("NaN" | "NaNf") -> nan
    | ESCAPED_STRING  -> string

COMMENT: /\/\/.*/

%import common.CNAME
%import common.SIGNED_NUMBER
%import common.ESCAPED_STRING
%import common.INT
%import common.WS
%ignore WS
%ignore COMMENT
"""
