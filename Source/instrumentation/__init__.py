# This package provides an API to store instrumentation data related to
# execution of a method call. The implementation uses aws x-ray sdk to inject
# the data into aws x-ray service.
#
# For more information refer to https://github.com/aws/aws-xray-sdk-python

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from collections import namedtuple
import numbers

# Named Tuple to store instrumentation data.
#
# Searchable data is dictionary of key, value pairs and key is used to search
# the instrumentation records in destination repository of such records. These
# records are stored as annotations in x-ray service.
#
# Non-searchable data stores additional instrumentation data as a dictionary
# where key is used to identify the named metadata and value is a dictionary
# of metadata key, value pairs. These records are stored as metadata
# in x-ray service
Record = namedtuple('InstrumentationRecord', ['searchable', 'non_searchable'], defaults=(None, None))


def configure(app, service_name):
    """
    Configure XRay Middleware for the Flask Service.

    :type app: flask.Flask
    :param app: Flask app
    :type service_name: string
    :param service_name: Service name identifies the originator of
    instrumentation data in aws x-ray
    """
    xray_recorder.configure(sampling=False,
                            service=service_name,
                            plugins=('EC2Plugin',))
    XRayMiddleware(app, xray_recorder)


def record(recorder=None, subsegment=None):
    """
    This is intended to be used as a decorator for the method call that
    is being instrumented. This decorator allows for instrumentation data
    handling in one centralized place so that multiple calls to collect
    instrumentation data is avoided. This way, the cross cutting concern of
    instrumenting the method call is delegated to a recorder function rather
    than separate calls to record data proliferated throughout the method.

    :type recorder function(response, options)
    :param recorder: A function that is passed the response object from
    method call and options dictionary that contains the method arguments.
    The function must return an instance of InstrumentationRecord
    :type subsegment string
    :param subsegment optional - start a new subsegment to record
    instrumentation data. See xray_recorder.begin_subsegment(...) for
    more details.
    :return: decorator
    """
    def wrapper_outer(f):

        def wrapper(*arg, **kwargs):
            try:
                if subsegment is not None:
                    xray_recorder.begin_subsegment(subsegment)
                result = f(*arg, **kwargs)
                if recorder:
                    data = recorder(result, kwargs)
                    if isinstance(data, Record):
                        __record_data__(data.searchable, True)
                        __record_data__(data.non_searchable, False)
                return result
            except Exception as error:
                __record_error__(error)
            finally:
                if subsegment is not None:
                    xray_recorder.end_subsegment()
        return wrapper

    return wrapper_outer


def current_trace_id():
    return xray_recorder.current_segment().trace_id


def current_segment_id():
    return xray_recorder.current_segment().id


def record_data(key, value, searchable):
    """
    This method is used to collect instrumentation data. Data is stored in
    current subsegment if there is one activae, otherwise it is stored in
    the segment.

    :type key: string
    :param key: identifier for instrumentation data
    :type value: str, bool or number when searchable is True. When searcable
    is False, an instance of dict
    :param value: instrumentation data
    :type searchable: bool
    :param searchable: whether key for instrumentation data can be
    used to search in aws x-ray
    """
    __assert_type__(key, value, searchable)
    segment = xray_recorder.current_segment()
    subsegment = xray_recorder.current_subsegment()
    span = subsegment if subsegment is not None else segment
    if searchable:
        span.put_annotation(key, value)
    else:
        span.put_metadata(key, value)


SEARCHABLE_TYPE_MSG = 'searchable value must be a string, number or bool'
NON_SEARCHABLE_TYPE_MSG = 'non-searchable value must be a dictionary'


def __assert_type__(key, value, searchable):
    if type(key) != str:
        raise ValueError('key must be a string')
    if searchable:
        if (type(value) not in [str, bool]) & (not isinstance(value, numbers.Number)):
            raise ValueError(SEARCHABLE_TYPE_MSG)
    else:
        if type(value) != dict:
            raise ValueError(NON_SEARCHABLE_TYPE_MSG)


def __record_data__(data, searchable):
    if data is None:
        return
    for key, value in data.items():
        record_data(key, value, searchable)


def __record_error__(error):
    record_data('instrumentation_error', True, True)
    detail = {'message': error.__repr__()}
    record_data('instrumentation_error_detail', detail, False)
