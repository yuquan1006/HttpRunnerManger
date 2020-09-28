# encoding: utf-8

"""
Built-in dependent functions used in YAML/JSON testcases.
"""

import datetime
import json
import os
import random
import re
import string
import time
import filetype

from httprunner.compat import basestring, builtin_str, integer_types, str
from httprunner.exceptions import ParamsError
from requests_toolbelt import MultipartEncoder

PWD = os.getcwd()

""" built-in functions
"""
def gen_random_string(str_len):
    """ generate random string with specified length
    """
    return ''.join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len))

def get_timestamp(str_len=13):
    """ get timestamp string, length can only between 0 and 16
    """
    if isinstance(str_len, integer_types) and 0 < str_len < 17:
        return builtin_str(time.time()).replace(".", "")[:str_len]

    raise ParamsError("timestamp length can only between 0 and 16.")

def get_current_date(fmt="%Y-%m-%d",day=0):
    """ get current date, default format is %Y-%m-%d
    """
    return (datetime.datetime.now()+datetime.timedelta(days=day)).strftime(fmt)

# 1.5.8版本的不用
#def multipart_encoder(field_name, file_path, file_type=None, file_headers=None):
   # if not os.path.isabs(file_path):
       # file_path = os.path.join(os.getcwd(), file_path)

    #filename = os.path.basename(file_path)
   # with open(file_path, 'rb') as f:
       # fields = {
           # field_name: (filename, f.read(), file_type)
       # }

    #return MultipartEncoder(fields)

#def multipart_content_type(multipart_encoder):
   # return multipart_encoder.content_type


# 使用2.0版本的
def multipart_encoder(**kwargs):
    """ initialize MultipartEncoder with uploading fields.
    """
    def get_filetype(file_path):
        file_type = filetype.guess(file_path)
        if file_type:
            return file_type.mime
        else:
            return "text/html"

    fields_dict = {}
    for key, value in kwargs.items():

        if os.path.isabs(value):
            _file_path = value
            is_file = True
        else:
            global PWD
            _file_path = os.path.join(PWD, value)
            is_file = os.path.isfile(_file_path)

        if is_file:
            filename = os.path.basename(_file_path)
            with open(_file_path, 'rb') as f:
                mime_type = get_filetype(_file_path)
                fields_dict[key] = (filename, f.read(), mime_type)
        else:
            fields_dict[key] = value

    return MultipartEncoder(fields=fields_dict)

def multipart_content_type(multipart_encoder):
    """ prepare Content-Type for request headers
    """
    return multipart_encoder.content_type

""" built-in comparators
"""
def equals(check_value, expect_value):
    assert check_value == expect_value

def less_than(check_value, expect_value):
    assert check_value < expect_value

def less_than_or_equals(check_value, expect_value):
    assert check_value <= expect_value

def greater_than(check_value, expect_value):
    assert check_value > expect_value

def greater_than_or_equals(check_value, expect_value):
    assert check_value >= expect_value

def not_equals(check_value, expect_value):
    assert check_value != expect_value

def string_equals(check_value, expect_value):
    assert builtin_str(check_value) == builtin_str(expect_value)

def length_equals(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) == expect_value

def length_greater_than(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) > expect_value

def length_greater_than_or_equals(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) >= expect_value

def length_less_than(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) < expect_value

def length_less_than_or_equals(check_value, expect_value):
    assert isinstance(expect_value, integer_types)
    assert len(check_value) <= expect_value

def contains(check_value, expect_value):
    assert isinstance(check_value, (list, tuple, dict, basestring))
    assert expect_value in check_value

def contained_by(check_value, expect_value):
    assert isinstance(expect_value, (list, tuple, dict, basestring))
    assert check_value in expect_value

def type_match(check_value, expect_value):
    def get_type(name):
        if isinstance(name, type):
            return name
        elif isinstance(name, basestring):
            try:
                return __builtins__[name]
            except KeyError:
                raise ValueError(name)
        else:
            raise ValueError(name)

    assert isinstance(check_value, get_type(expect_value))

def regex_match(check_value, expect_value):
    assert isinstance(expect_value, basestring)
    assert isinstance(check_value, basestring)
    assert re.match(expect_value, check_value)

def startswith(check_value, expect_value):
    assert builtin_str(check_value).startswith(builtin_str(expect_value))

def endswith(check_value, expect_value):
    assert builtin_str(check_value).endswith(builtin_str(expect_value))

""" built-in hooks
"""
def setup_hook_prepare_kwargs(request):
    if request["method"] == "POST":
        content_type = request.get("headers", {}).get("content-type")
        if content_type and "data" in request:
            # if request content-type is application/json, request data should be dumped
            if content_type.startswith("application/json") and isinstance(request["data"], (dict, list)):
                request["data"] = json.dumps(request["data"])

            if isinstance(request["data"], str):
                request["data"] = request["data"].encode('utf-8')

def sleep_N_secs(n_secs):
    """ sleep n seconds
    """
    time.sleep(n_secs)
