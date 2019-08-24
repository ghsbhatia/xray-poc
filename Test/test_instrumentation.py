# This module provides unittests for instrumentation package that provides
# a simplified API for aws x-ray service.
#
# For more information refer to https://github.com/aws/aws-xray-sdk-python

import instrumentation
import pytest
from flask import Flask
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core.models.segment import Segment
from aws_xray_sdk.core.models.subsegment import Subsegment
from unittest.mock import patch, call, Mock


# app is a Flask instance that is available within all the test cases.
@pytest.fixture(autouse=True)
def app():
    yield Flask('test')


@patch.object(XRayMiddleware, '__init__')
@patch.object(xray_recorder, 'configure', autospec=True)
def test_configure(mock_configure, mock_middleware):
    """
    Test to ensure that x-ray middleware for flask service is configured.

    :type mock_configure: unittest.mock.MagicMock
    :param mock_configure: mock object for xray_recorder configure method
    :type mock_middleware: unittest.mock.MagicMock
    :param mock_middleware: mock object for XRayMiddleware __init__ method
    """
    mock_middleware.return_value = None
    instrumentation.configure(app, 'test-service')
    mock_configure.assert_called_with(sampling=False,
                                      service='test-service',
                                      plugins=('EC2Plugin',))
    mock_middleware.assert_called_with(app, xray_recorder)


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
def test_record_searchable_data_segment(mock_current_subsegment,
                                        mock_current_segment):
    """
    Test to ensure that x-ray sdk put_annotation call is invoked on
    the current segment.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment:
    mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """
    mock_segment = Mock(spec=Segment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = None
    instrumentation.record_data('k1', 'v1', True)
    mock_segment.put_annotation.assert_called_with('k1', 'v1')


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
def test_record_nonsearchable_data_segment(mock_current_subsegment,
                                           mock_current_segment):
    """
    Test to ensure that x-ray sdk put_metadata call is invoked on
    the current segment.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment:
    mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """
    mock_segment = Mock(spec=Segment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = None
    instrumentation.record_data('m1', {'foo': 'bar'}, False)
    mock_segment.put_metadata.assert_called_with('m1', {'foo': 'bar'})


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
def test_record_searchable_data_subsegment(mock_current_subsegment,
                                           mock_current_segment):
    """
    Test to ensure that x-ray sdk put_annotation call is invoked on
    the current subsegment.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment:
    mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """
    mock_segment = Mock(spec=Segment)
    mock_subsegment = Mock(spec=Subsegment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = mock_subsegment
    instrumentation.record_data('k1', 'v1', True)
    mock_subsegment.put_annotation.assert_called_with('k1', 'v1')


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
def test_record_nonsearchable_data_subsegment(mock_current_subsegment,
                                              mock_current_segment):
    """
    Test to ensure that x-ray sdk put_metadata call is invoked on
    the current subsegment.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment:
    mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """
    mock_segment = Mock(spec=Segment)
    mock_subsegment = Mock(spec=Subsegment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = mock_subsegment
    instrumentation.record_data('m1', {'foo': 'bar'}, False)
    mock_subsegment.put_metadata.assert_called_with('m1', {'foo': 'bar'})


supported_type_data = [
    ('key1', 120),
    ('key1', 1.2),
    ('key1', False),
    ('key1', 'foo')
]


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
@pytest.mark.parametrize('key, value', supported_type_data)
def test_record_data_searchable_supported_type(mock_current_subsegment,
                                               mock_current_segment,
                                               key, value):
    """
    Test to ensure that x-ray sdk put_annotation call is invoked when
    value is a supported data type.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment:
    mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    :type key: str
    :param key: annotation key
    :type value: str, bool or number
    :param value: annotation value
    """
    mock_segment = Mock(spec=Segment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = None
    instrumentation.record_data(key, value, True)
    mock_segment.put_annotation.assert_called_with(key, value)


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
def test_record_data_searchable_unsupported_type(mock_current_subsegment,
                                                 mock_current_segment):
    """
    Test to ensure that exception is thrown for unsupported data type.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment: mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """
    mock_segment = Mock(spec=Segment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = None
    with pytest.raises(ValueError) as error:
        instrumentation.record_data('k1', Mock(), True)
    assert str(error.value) == instrumentation.SEARCHABLE_TYPE_MSG


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
def test_record_data_nonsearchable_unsupported_type(mock_current_subsegment,
                                                    mock_current_segment):
    """
    Test to ensure that exception is thrown for unsupported data type.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment: mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """
    mock_segment = Mock(spec=Segment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = None
    with pytest.raises(ValueError) as error:
        instrumentation.record_data('k1', Mock(), False)
    assert str(error.value) == instrumentation.NON_SEARCHABLE_TYPE_MSG


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
def test_record_decorator_segment(mock_current_subsegment,
                                  mock_current_segment):
    """
    Test to ensure that x-ray sdk put_metadata and put_annotation calls
    are invoked on the current segment.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment: mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """

    # recorder function
    def recorder(response, options):
        kpi_data = {'type': response[1], 'value': response[2]}
        searchable_data = {'id': options['message'], 'errors': response[0]}
        non_searchable_data = {'kpi': kpi_data}
        return instrumentation.Record(searchable=searchable_data, non_searchable=non_searchable_data)

    # decorate function to be instrumented
    @instrumentation.record(recorder)
    def dispatch(message):
        return 0, 'foo', 'bar'

    mock_segment = Mock(spec=Segment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = None
    annotation_calls = [call('id', 'm1'), call('errors', 0)]
    dispatch(message='m1')
    mock_segment.put_annotation.assert_has_calls(annotation_calls)
    mock_segment.put_metadata.assert_called_with('kpi', {'type': 'foo', 'value': 'bar'})


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
@patch.object(xray_recorder, 'begin_subsegment', autospec=True)
@patch.object(xray_recorder, 'end_subsegment', autospec=True)
def test_record_decorator_subsegment(mock_end_subsegment,
                                     mock_begin_subsegment,
                                     mock_current_subsegment,
                                     mock_current_segment):
    """
    Test to ensure that x-ray sdk put_metadata and put_annotation calls
    are invoked on the current subsegment.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment: mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """

    # recorder function
    def recorder(response, options):
        kpi_data = {'type': response[1], 'value': response[2]}
        searchable_data = {'id': options['message'], 'errors': response[0]}
        non_searchable_data = {'kpi': kpi_data}
        return instrumentation.Record(searchable=searchable_data, non_searchable=non_searchable_data)

    # decorate function to be instrumented
    @instrumentation.record(recorder, 'ss1')
    def dispatch(message):
        return 0, 'foo', 'bar'

    mock_segment = Mock(spec=Segment)
    mock_subsegment = Mock(spec=Subsegment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = mock_subsegment
    mock_begin_subsegment.return_value = mock_subsegment
    mock_end_subsegment.return_value = None
    annotation_calls = [call('id', 'm1'), call('errors', 0)]
    dispatch(message='m1')
    mock_begin_subsegment.assert_called_with('ss1')
    mock_subsegment.put_annotation.assert_has_calls(annotation_calls)
    mock_subsegment.put_metadata.assert_called_with('kpi', {'type': 'foo', 'value': 'bar'})
    mock_end_subsegment.assert_called


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
@patch.object(xray_recorder, 'begin_subsegment', autospec=True)
@patch.object(xray_recorder, 'end_subsegment', autospec=True)
def test_handle_decorator_error(mock_end_subsegment,
                                mock_begin_subsegment,
                                mock_current_subsegment,
                                mock_current_segment):
    """
    Test to ensure that decorator exceptions are handled and
    current subsegment is closed.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment: mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """

    # recorder function
    def recorder(response, options):
        raise ZeroDivisionError('omg!')

    # decorate function to be instrumented
    @instrumentation.record(recorder, 'ss1')
    def dispatch(message):
        return 0, 'foo', 'bar'

    mock_segment = Mock(spec=Segment)
    mock_subsegment = Mock(spec=Subsegment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = mock_subsegment
    mock_begin_subsegment.return_value = mock_subsegment
    mock_end_subsegment.return_value = None
    dispatch(message='m1')
    mock_begin_subsegment.assert_called_with('ss1')
    mock_subsegment.put_annotation.assert_called_with('instrumentation_error', True)
    mock_subsegment.put_metadata.assert_called_with('instrumentation_error_detail',
                                                    {'message': "ZeroDivisionError('omg!')"})
    mock_end_subsegment.assert_called


@patch.object(xray_recorder, 'current_segment', autospec=True)
@patch.object(xray_recorder, 'current_subsegment', autospec=True)
@patch.object(xray_recorder, 'begin_subsegment', autospec=True)
@patch.object(xray_recorder, 'end_subsegment', autospec=True)
def test_record_decorator_no_recorder_subsegment(mock_end_subsegment,
                                                 mock_begin_subsegment,
                                                 mock_current_subsegment,
                                                 mock_current_segment):
    """
    Test to ensure that x-ray sdk begin_subsegment and end_subsegment calls
    are invoked when no recorder function is specified.

    :type mock_current_segment: unittest.mock.MagicMock
    :param mock_current_segment: mock object for xray_recorder current_segment
    :type mock_current_subsegment: unittest.mock.MagicMock
    :param mock_current_subsegment:
    mock object for xray_recorder current_subsegment
    """

    # decorate function to be instrumented
    @instrumentation.record(subsegment='ss1')
    def dispatch(message):
        return 0, 'foo', 'bar'

    mock_segment = Mock(spec=Segment)
    mock_subsegment = Mock(spec=Subsegment)
    mock_current_segment.return_value = mock_segment
    mock_current_subsegment.return_value = mock_subsegment
    mock_begin_subsegment.return_value = mock_subsegment
    mock_end_subsegment.return_value = None
    dispatch(message='m1')
    mock_begin_subsegment.assert_called_with('ss1')
    mock_end_subsegment.assert_called
