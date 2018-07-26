from ironicv1.common import send
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


@send('get')
def volume_resource_list(**kwargs):
    url = '/volume'
    return url, {}


@send('get')
def volume_connector_list(**kwargs):
    url = '/volume/connectors?{}'.format(urlencode(kwargs))
    return url, {}


@send('post')
def volume_connector_create(node_uuid, volume_type, connector_id, **kwargs):
    url = '/volume/connectors'
    json = {
        'node_uuid': node_uuid,
        'type': volume_type,
        'connector_id': connector_id,
    }
    json.update(kwargs)
    return url, {'json': json}


@send('get')
def volume_connector_get_details(volume_connector_id, **kwargs):
    url = '/volume/connectors/{}?{}'.format(
        volume_connector_id, urlencode(kwargs))
    return url, {}


@send('patch')
def volume_connector_update(volume_connector_id, properties, **kwargs):
    url = '/volume/connectors/{}'.format(volume_connector_id)
    return url, {'json': properties}


@send('delete')
def volume_connector_delete(volume_connector_id, **kwargs):
    url = '/volume/connectors/{}'.format(volume_connector_id)
    return url, {}


@send('get')
def volume_target_list(**kwargs):
    url = '/volume/targets?{}'.format(urlencode(kwargs))
    return url, {}


@send('post')
def volume_target_create(node_uuid, volume_type, properties,
                         boot_index, volume_id, **kwargs):
    url = '/volume/targets'
    json = {
        'node_uuid': node_uuid,
        'volume_type': volume_type,
        'properties': properties,
        'boot_index': boot_index,
        'volume_id': volume_id,
    }
    json.update(kwargs)
    return url, {'json': json}


@send('get')
def volume_target_get_details(target_id, **kwargs):
    url = '/volume/targets/{}?{}'.format(target_id, urlencode(kwargs))
    return url, {}


@send('patch')
def volume_target_update(target_id, properties, **kwargs):
    url = '/volume/targets/{}'.format(target_id)
    return url, {'json': properties}


@send('delete')
def volume_target_delete(target_id, **kwargs):
    url = '/volume/targets/{}'.format(target_id)
    return url, {}
