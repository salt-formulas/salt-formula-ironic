from ironicv1.common import send
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('get')
def chassis_list_details(**kwargs):
    url = '/chassis/detail?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def chassis_get_details(chassis_id, **kwargs):
    url = '/chassis/{}?{}'.format(chassis_id, urlencode(kwargs))
    return url, {}


@send('patch')
def chassis_update(chassis_id, properties, **kwargs):
    url = '/chassis/{}'.format(chassis_id)
    return url, {'json': properties}


@send('delete')
def chassis_delete(chassis_id, **kwargs):
    url = '/chassis/{}'.format(chassis_id)
    return url, {}


@send('post')
def chassis_create(chassis, **kwargs):
    url = '/chassis'
    return url, {'json': chassis}


@send('get')
def chassis_list(**kwargs):
    url = '/chassis?{}'.format(urlencode(kwargs))
    return url, {}
