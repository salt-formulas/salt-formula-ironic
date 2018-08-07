from ironicv1.common import send
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('get')
def port_list(**kwargs):
    url = '/ports?{}'.format(urlencode(kwargs))
    return url, {}


@send('post')
def port_create(node_uuid, address, **kwargs):
    url = '/ports'
    json = {
        'node_uuid': node_uuid,
        'address': address,
    }
    json.update(kwargs)
    return url, {'json': json}


@send('get')
def port_list_details(**kwargs):
    url = '/ports/detail?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def port_get_details(port_id, **kwargs):
    url = '/ports/{}?{}'.format(port_id, urlencode(kwargs))
    return url, {}


@send('patch')
def port_update(port_id, properties, **kwargs):
    url = '/ports/{}'.format(port_id)
    return url, {'json': properties}


@send('delete')
def port_delete(port_id, **kwargs):
    url = '/ports/{}'.format(port_id)
    return url, {}