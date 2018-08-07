import logging
import os_client_config

log = logging.getLogger(__name__)

IRONIC_VERSION_HEADER = 'X-OpenStack-Ironic-API-Version'
ADAPTER_VERSION = '1.0'


class IronicException(Exception):

    _msg = "Ironic module exception occurred."

    def __init__(self, message=None, **kwargs):
        super(IronicException, self).__init__(message or self._msg)


class NoIronicEndpoint(IronicException):
    _msg = "Ironic endpoint not found in keystone catalog."


class NoAuthPluginConfigured(IronicException):
    _msg = ("You are using keystoneauth auth plugin that does not support "
            "fetching endpoint list from token (noauth or admin_token).")


class NoCredentials(IronicException):
    _msg = "Please provide cloud name present in clouds.yaml."


def _get_raw_client(cloud_name):
    service_type = 'baremetal'
    config = os_client_config.OpenStackConfig()
    cloud = config.get_one_cloud(cloud_name)
    adapter = cloud.get_session_client(service_type)
    adapter.version = ADAPTER_VERSION
    try:
        access_info = adapter.session.auth.get_access(adapter.session)
        access_info.service_catalog.get_endpoints()
    except (AttributeError, ValueError):
        e = NoAuthPluginConfigured()
        log.exception('%s' % e)
        raise e
    return adapter


def send(method):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            cloud_name = kwargs.pop('cloud_name')
            if not cloud_name:
                e = NoCredentials()
                log.error('%s' % e)
                raise e
            adapter = _get_raw_client(cloud_name)
            # Remove salt internal kwargs
            kwarg_keys = list(kwargs.keys())
            for k in kwarg_keys:
                if k.startswith('__'):
                    kwargs.pop(k)
            microversion = kwargs.pop('microversion', None)
            url, request_kwargs = func(*args, **kwargs)
            if microversion:
                if 'headers' not in request_kwargs:
                    request_kwargs['headers'] = {}
                request_kwargs['headers'][IRONIC_VERSION_HEADER] = \
                    microversion
            response = getattr(adapter, method)(url, **request_kwargs)
            if not response.content:
                return {}
            try:
                resp = response.json()
            except ValueError:
                resp = response.content
            return resp
        return wrapped_f
    return wrap
