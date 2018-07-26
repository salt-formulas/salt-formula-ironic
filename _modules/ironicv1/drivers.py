from ironicv1.common import send
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('get')
def driver_list(**kwargs):
    url = '/drivers?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def driver_get_details(name, **kwargs):
    url = '/drivers/{}'.format(name)
    return url, {}


@send('get')
def driver_get_properties(name, **kwargs):
    url = '/drivers/{}/properties'.format(name)
    return url, {}


@send('get')
def driver_get_logical_disk_properties(name, **kwargs):
    url = '/drivers/{}/raid/logical_disk_properties'.format(name)
    return url, {}
