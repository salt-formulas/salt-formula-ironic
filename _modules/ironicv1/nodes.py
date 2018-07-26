from ironicv1.common import send
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


# NOTE(opetrenko): Each driver require different driver_info or do not require
# it at all. To make things work, please use driver_get_properties with driver
# you want to use to get list of required arguments for driver_info.
# For more take a look at Baremetal API Reference
@send('post')
def node_create(driver, **kwargs):
    url = '/nodes'
    json = {
        'driver': driver,
    }
    json.update(kwargs)
    return url, {'json': json}


@send('get')
def node_list(**kwargs):
    url = '/nodes?{}'.format(urlencode(kwargs))
    return url, {}


@send('get')
def node_get_details(node_ident, **kwargs):
    url = '/nodes/{}?{}'.format(node_ident, urlencode(kwargs))
    return url, {}


@send('patch')
def node_update(node_ident, properties, **kwargs):
    url = '/nodes/{}'.format(node_ident)
    return url, {'json': properties}


@send('delete')
def node_delete(node_ident, **kwargs):
    url = '/nodes/{}'.format(node_ident)
    return url, {}


# NOTE: Node management API
@send('get')
def node_validate(node_ident, **kwargs):
    url = '/nodes/{}/validate'.format(node_ident)
    return url, {}


@send('put')
def node_maintenance_flag_set(node_ident, **kwargs):
    url = '/nodes/{}/maintenance'.format(node_ident)
    json = {}
    if 'reason' in kwargs:
        json['reason'] = kwargs['reason']
    return url, {'json': json}


@send('delete')
def node_maintenance_flag_clear(node_ident, **kwargs):
    url = '/nodes/{}/maintenance'.format(node_ident)
    return url, {}


@send('put')
def node_boot_device_set(node_ident, boot_device, **kwargs):
    url = '/nodes/{}/management/boot_device'.format(node_ident)
    json = {
        'boot_device': boot_device,
    }
    json.update(kwargs)
    return url, {'json': json}


@send('get')
def node_boot_device_get(node_ident, **kwargs):
    url = '/nodes/{}/management/boot_device'.format(node_ident)
    return url, {}


@send('get')
def node_boot_device_get_supported(node_ident, **kwargs):
    url = '/nodes/{}/management/boot_device/supported'.format(node_ident)
    return url, {}


@send('put')
def node_inject_nmi(node_ident, **kwargs):
    url = '/nodes/{}/management/inject_nmi'.format(node_ident)
    return url, {'json': {}}


@send('get')
def node_state_summary(node_ident, **kwargs):
    url = '/nodes/{}/states'.format(node_ident)
    return url, {}


@send('put')
def node_power_state_change(node_ident, target, **kwargs):
    url = '/nodes/{}/states/power'.format(node_ident)
    json = {
        'target': target,
    }
    json.update(kwargs)
    return url, {'json': json}


@send('put')
def node_provision_state_change(node_ident, target, **kwargs):
    url = '/nodes/{}/states/provision'.format(node_ident)
    json = {
        'target': target,
    }
    json.update(kwargs)
    return url, {'json': json}


@send('put')
def node_raid_config_set(node_ident, target_raid_config, **kwargs):
    url = 'nodes/{}/states/raid'.format(node_ident)
    return url, {'json': target_raid_config}


@send('get')
def node_console_get(node_ident, **kwargs):
    url = '/nodes/{}/states/console'.format(node_ident)
    return url, {}


@send('put')
def node_console_start_stop(node_ident, enabled, **kwargs):
    url = '/nodes/{}/states/console'.format(node_ident)
    json = {
        'enabled': enabled,
    }
    return url, {'json': json}


# NOTE: Node Traits API
@send('get')
def node_traits_list(node_ident, **kwargs):
    url = '/nodes/{}/traits'.format(node_ident)
    return url, {}


@send('put')
def node_traits_set(node_ident, traits, **kwargs):
    url = '/nodes/{}/traits'.format(node_ident)
    json = {
        'traits': traits,
    }
    return url, {'json': json}


@send('put')
def node_traits_set_single(node_ident, trait, **kwargs):
    url = '/nodes/{}/traits/{}'.format(node_ident, trait)
    return url, {'json': {}}


@send('delete')
def node_traits_delete(node_ident, **kwargs):
    url = '/nodes/{}/traits'.format(node_ident)
    return url, {}


@send('delete')
def node_traits_delete_single(node_ident, trait, **kwargs):
    url = '/nodes/{}/traits/{}'.format(node_ident, trait)
    return url, {}


# NOTE: VIFs API
@send('get')
def node_vif_list(node_ident, **kwargs):
    url = '/nodes/{}/vifs'.format(node_ident)
    return url, {}


@send('post')
def node_vif_attach(node_ident, id, **kwargs):
    url = '/nodes/{}/vifs'.format(node_ident)
    json = {
        'id': id,
    }
    return url, {'json': json}


@send('delete')
def node_vif_detach(node_ident, vif_ident, **kwargs):
    url = '/nodes/{}/vifs/{}'.format(node_ident, vif_ident)
    return url, {}
