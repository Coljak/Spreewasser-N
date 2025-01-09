# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */

# Authors:
# Michael Berg-Mohnicke <michael.berg@zalf.de>
#
# Maintainers:
# Currently maintained by the authors.
#
# This file is part of the MONICA model created at the Institute of
# Landscape Systems Analysis at the ZALF.
# Copyright (C: Leibniz Centre for Agricultural Landscape Research (ZALF)

import json
import os
from pathlib import Path
import sys
import time

# PATH_TO_SOIL_IO3 = Path(os.path.realpath(__file__)).parent.parent.parent.parent / "util/soil"

# if str(PATH_TO_SOIL_IO3) not in sys.path:
#     sys.path.insert(1, str(PATH_TO_SOIL_IO3))
# from . import soil_io3

#------------------------------------------------------------------------------

CACHE_REFS = False

OP_AVG = 0
OP_MEDIAN = 1
OP_SUM = 2
OP_MIN = 3
OP_MAX = 4
OP_FIRST = 5
OP_LAST = 6
OP_NONE = 7
OP_UNDEFINED_OP_ = 8


ORGAN_ROOT = 0
ORGAN_LEAF = 1
ORGAN_SHOOT = 2
ORGAN_FRUIT = 3
ORGAN_STRUCT = 4
ORGAN_SUGAR = 5
ORGAN_UNDEFINED_ORGAN_ = 6

#------------------------------------------------------------------------------
###### used in swn
def oid_is_organ(oid):
    return oid["organ"] != ORGAN_UNDEFINED_ORGAN_

#------------------------------------------------------------------------------

def oid_is_range(oid):
    return oid["fromLayer"] >= 0 \
        and oid["toLayer"] >= 0 #\
        #and oid["fromLayer"] < oid["toLayer"]

#------------------------------------------------------------------------------

def op_to_string(op):
    return {
        OP_AVG: "AVG",
        OP_MEDIAN: "MEDIAN",
        OP_SUM: "SUM",
        OP_MIN: "MIN",
        OP_MAX: "MAX",
        OP_FIRST: "FIRST",
        OP_LAST: "LAST",
        OP_NONE: "NONE",
        OP_UNDEFINED_OP_: "undef"
    }.get(op, "undef")

#------------------------------------------------------------------------------
### used in swn
def organ_to_string(organ):
    return {
        ORGAN_ROOT: "Root",
        ORGAN_LEAF: "Leaf",
        ORGAN_SHOOT: "Shoot",
        ORGAN_FRUIT: "Fruit",
        ORGAN_STRUCT: "Struct",
        ORGAN_SUGAR: "Sugar",
        ORGAN_UNDEFINED_ORGAN_: "undef"
    }.get(organ, "undef")

#------------------------------------------------------------------------------

def oid_to_string(oid, include_time_agg):
    oss = ""
    oss += "["
    oss += oid["name"]
    if oid_is_organ(oid):
        oss += ", " + organ_to_string(oid["organ"])
    elif oid_is_range(oid):
        oss += ", [" + str(oid["fromLayer"] + 1) + ", " + str(oid["toLayer"] + 1) \
        + (", " + op_to_string(oid["layerAggOp"]) if oid["layerAggOp"] != OP_NONE else "") \
        + "]"
    elif oid["fromLayer"] >= 0:
        oss += ", " + str(oid["fromLayer"] + 1)
    if include_time_agg:
        oss += ", " + op_to_string(oid["timeAggOp"])
    oss += "]"

    return oss

#------------------------------------------------------------------------------
# For CSV output of he results
def write_output_header_rows(output_ids,
                             include_header_row=True,
                             include_units_row=True,
                             include_time_agg=False):
    "write header rows"
    row1 = []
    row2 = []
    row3 = []
    row4 = []
    for oid in output_ids:
        from_layer = oid["fromLayer"]
        to_layer = oid["toLayer"]
        is_organ = oid_is_organ(oid)
        is_range = oid_is_range(oid) and oid["layerAggOp"] == OP_NONE
        if is_organ:
            # organ is being represented just by the value of fromLayer currently
            to_layer = from_layer = oid["organ"]
        elif is_range:
            from_layer += 1
            to_layer += 1     # display 1-indexed layer numbers to users
        else:
            to_layer = from_layer # for aggregated ranges, which aren't being displayed as range

        for i in range(from_layer, to_layer+1):
            str1 = ""
            if is_organ:
                str1 += (oid["name"] + "/" + organ_to_string(oid["organ"])) if len(oid["displayName"]) == 0 else oid["displayName"]
            elif is_range:
                str1 += (oid["name"] + "_" + str(i)) if len(oid["displayName"]) == 0 else oid["displayName"]
            else:
                str1 += oid["name"] if len(oid["displayName"]) == 0 else oid["displayName"]
            row1.append(str1)
            row4.append("j:" + oid["jsonInput"].replace("\"", ""))
            row3.append("m:" + oid_to_string(oid, include_time_agg))
            row2.append("[" + oid["unit"] + "]")

    out = []
    if include_header_row:
        out.append(row1)
    if include_units_row:
        out.append(row4)
    if include_time_agg:
        out.append(row3)
        out.append(row2)

    return out

#------------------------------------------------------------------------------

def write_output(output_ids, values, round_ids={}):
    "write actual output lines"
    out = []
    if len(values) > 0:
        for k in range(0, len(values[0])):
            i = 0
            row = []
            for oid in output_ids:
                oid_name = oid["displayName"] if len(oid["displayName"]) > 0 else oid["name"]
                j__ = values[i][k]
                if isinstance(j__, list):
                    for jv_ in j__:
                        row.append(round(jv_, round_ids[oid_name]) if oid_name in round_ids else jv_)
                else:
                    row.append(round(j__, round_ids[oid_name]) if oid_name in round_ids else j__)
                i += 1
            out.append(row)
    return out

#------------------------------------------------------------------------------

def write_output_obj(output_ids, values, round_ids={}):
    "write actual output lines"
    out = []
    for obj in values:
        row = []
        for oid in output_ids:
            oid_name = oid["displayName"] if len(oid["displayName"]) > 0 else oid["name"]
            j__ = obj.get(oid_name, "")
            if isinstance(j__, list):
                for jv_ in j__:
                    row.append(round(jv_, round_ids[oid_name]) if oid_name in round_ids else jv_)
            else:
                row.append(round(j__, round_ids[oid_name]) if oid_name in round_ids else j__)
        out.append(row)
    return out

#------------------------------------------------------------------------------

def is_absolute_path(p):
    "is absolute path"
    return p.startswith("/") \
        or (len(p) == 2 and p[1] == ":") \
        or (len(p) > 2 and p[1] == ":" \
            and (p[2] == "\\" \
                or p[2] == "/"))

#------------------------------------------------------------------------------





#------------------------------------------------------------------------------

def read_and_parse_json_file(path):
    with open(path) as f:
        return {"result": json.load(f), "errors": [], "success": True}
    return {"result": {},
            "errors": ["Error opening file with path : '" + path + "'!"],
            "success": False}

#------------------------------------------------------------------------------

def parse_json_string(jsonString):
    return {"result": json.loads(jsonString), "errors": [], "success": True}

#------------------------------------------------------------------------------

def is_string_type(j):
    return isinstance(j, str)

#------------------------------------------------------------------------------

def find_and_replace_references(root, j):
    sp = supported_patterns()

    success = True
    errors = []

    if isinstance(j, list) and len(j) > 0:

        arr = []
        array_is_reference_function = False

        if is_string_type(j[0]):
            if j[0] in sp:
                f = sp[j[0]]
                array_is_reference_function = True

                #check for nested function invocations in the arguments
                funcArr = []
                for i in j:
                    res = find_and_replace_references(root, i)
                    success = success and res["success"]
                    if not res["success"]:
                        for err in res["errors"]:
                            errors.append(err)
                    funcArr.append(res["result"])

                #invoke function
                jaes = f(root, funcArr)

                success = success and jaes["success"]
                if not jaes["success"]:
                    for err in jaes["errors"]:
                        errors.append(err)

                #if successful try to recurse into result for functions in result
                if jaes["success"]:
                    res = find_and_replace_references(root, jaes["result"])
                    success = success and res["success"]
                    if not res["success"]:
                        for err in res["errors"]:
                            errors.append(err)
                    return {"result": res["result"], "errors": errors, "success": len(errors) == 0}
                else:
                    return {"result": {}, "errors": errors, "success": len(errors) == 0}

        if not array_is_reference_function:
            for jv in j:
                res = find_and_replace_references(root, jv)
                success = success and res["success"]
                if not res["success"]:
                    for err in res["errors"]:
                        errors.append(err)
                arr.append(res["result"])

        return {"result": arr, "errors": errors, "success": len(errors) == 0}

    elif isinstance(j, dict):
        obj = {}

        for k, v in j.items():
            r = find_and_replace_references(root, v)
            success = success and r["success"]
            if not r["success"]:
                for e in r["errors"]:
                    errors.append(e)
            obj[k] = r["result"]

        return {"result": obj, "errors": errors, "success": len(errors) == 0}

    return {"result": j, "errors": errors, "success": len(errors) == 0}

#------------------------------------------------------------------------------

def print_possible_errors(errs, include_warnings=False):
    if not errs["success"]:
        for err in errs["errors"]:
            print(err)

    if include_warnings and "warnings" in errs:
        for war in errs["warnings"]:
            print(war)

    return errs["success"]


    