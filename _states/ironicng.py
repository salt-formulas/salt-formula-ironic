# -*- coding: utf-8 -*-
'''
Management of Ironic resources
===============================
:depends:   - ironicclient Python module
:configuration: See :py:mod:`salt.modules.ironic` for setup instructions.
.. code-block:: yaml
    ironicng node present:
      ironicng.node_present:
        - name: node-1
        - provider_physical_network: PHysnet1
        - provider_network_type: vlan
'''
import logging
from functools import wraps
LOG = logging.getLogger(__name__)


def __virtual__():
    '''
    Only load if ironic module is present in __salt__
    '''
    return 'ironicng' if 'ironicng.list_nodes' in __salt__ else False


def _test_call(method):
    (resource, functionality) = method.func_name.split('_')
    if functionality == 'present':
        functionality = 'updated'
    else:
        functionality = 'removed'

    @wraps(method)
    def check_for_testing(name, *args, **kwargs):
        if __opts__.get('test', None):
            return _no_change(name, resource, test=functionality)
        return method(name, *args, **kwargs)
    return check_for_testing


def _ironic_module_call(method, *args, **kwargs):
    return __salt__['ironicng.{0}'.format(method)](*args, **kwargs)

def _auth(profile=None, endpoint_type=None,
          ironic_api_version=None):
    '''
    Set up ironic credentials
    '''
    if profile:
        credentials = __salt__['config.option'](profile)
        user = credentials['keystone.user']
        password = credentials['keystone.password']
        tenant = credentials['keystone.tenant']
        auth_url = credentials['keystone.auth_url']
    kwargs = {
        'connection_user': user,
        'connection_password': password,
        'connection_tenant': tenant,
        'connection_auth_url': auth_url,
        'connection_endpoint_type': endpoint_type,
        'connection_ironic_api_version': ironic_api_version,
        'profile': profile
    }

    return kwargs

@_test_call
def node_present(name,
                 driver,
                 driver_info=None,
                 properties=None,
                 extra=None,
                 console_enabled=None,
                 resource_class=None,
                 boot_interface=None,
                 console_interface=None,
                 deploy_interface=None,
                 inspect_interface=None,
                 management_interface=None,
                 network_interface=None,
                 power_interface=None,
                 raid_interface=None,
                 vendor_interface=None,
                 maintenance=None,
                 maintenance_reason=None,
                 ports=None,
                 profile=None,
                 endpoint_type=None,
                 ironic_api_version=None):
    '''
    Ensure that the ironic node is present with the specified properties.
    '''
    connection_args = _auth(profile, endpoint_type,
                            ironic_api_version=ironic_api_version)

    existing_nodes = _ironic_module_call(
        'list_nodes', detail=True, **connection_args)['nodes']
    existing_nodes = [node for node in existing_nodes if node['name'] == name]

    node_arguments = _get_non_null_args(
        name=name,
        driver=driver,
        driver_info=driver_info,
        properties=properties,
        extra=extra,
        console_enabled=console_enabled,
        resource_class=resource_class,
        boot_interface=boot_interface,
        console_interface=console_interface,
        deploy_interface=deploy_interface,
        inspect_interface=inspect_interface,
        management_interface=management_interface,
        network_interface=network_interface,
        power_interface=power_interface,
        raid_interface=raid_interface,
        vendor_interface=vendor_interface,
        maintenance=maintenance,
        maintenance_reason=maintenance_reason)

    # In ironic node names are unique
    if len(existing_nodes) == 0:
        node_arguments.update(connection_args)
        res = _ironic_module_call(
            'create_node', **node_arguments)

        if res.get('name') == name:
            return _created(name, 'node', res)

    elif len(existing_nodes) == 1:
        # TODO(vsaienko) add update with deep comparison
        return _no_change(name, 'node')
        existing_node = existing_nodes[0]
    return _create_failed(name, 'node')


@_test_call
def node_absent(name, uuid=None, profile=None, endpoint_type=None):
    connection_args = _auth(profile, endpoint_type)
    identifier = uuid or name
    _ironic_module_call(
        'delete_node', identifier, **connection_args)
    return _absent(identifier, 'node')

@_test_call
def port_present(name,
                 address,
                 node_name=None,
                 node_uuid=None,
                 local_link_connection=None,
                 extra=None,
                 profile=None,
                 endpoint_type=None, ironic_api_version=None):
    connection_args = _auth(profile, endpoint_type,
                            ironic_api_version=ironic_api_version)
    identifier = node_uuid or node_name
    existing_ports =  _ironic_module_call('list_ports', detail=True,
                                          address=address,
                                          **connection_args)['ports']
    # we filtered ports by address, so if port found only one item will
    # exist since address is unique.
    existing_port = existing_ports[0] if len(existing_ports) else {}

    existing_node = _ironic_module_call('show_node', node_id=identifier,
        **connection_args)

    port_arguments = _get_non_null_args(
            address=address,
            node_uuid=existing_node['uuid'],
            local_link_connection=local_link_connection,
            extra=extra)

    if not existing_port:
        port_arguments.update(connection_args)
        res = _ironic_module_call('create_port', **port_arguments)
        return _created(address, 'port', res)
    else:
        # generate differential
        # TODO(vsaienko) add update with deep comparison
        return _no_change(address, 'port')

def _created(name, resource, resource_definition):
    changes_dict = {'name': name,
                    'changes': resource_definition,
                    'result': True,
                    'comment': '{0} {1} created'.format(resource, name)}
    return changes_dict

def _updated(name, resource, resource_definition):
    changes_dict = {'name': name,
                    'changes': resource_definition,
                    'result': True,
                    'comment': '{0} {1} updated'.format(resource, name)}
    return changes_dict

def _no_change(name, resource, test=False):
    changes_dict = {'name': name,
                    'changes': {},
                    'result': True}
    if test:
        changes_dict['comment'] = \
            '{0} {1} will be {2}'.format(resource, name, test)
    else:
        changes_dict['comment'] = \
            '{0} {1} is in correct state'.format(resource, name)
    return changes_dict


def _deleted(name, resource, resource_definition):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} removed'.format(resource, name),
                    'result': True}
    return changes_dict


def _absent(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} not present'.format(resource, name),
                    'result': True}
    return changes_dict


def _delete_failed(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} failed to delete'.format(resource,
                                                                 name),
                    'result': False}
    return changes_dict

def _create_failed(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} failed to create'.format(resource,
                                                                 name),
                    'result': False}
    return changes_dict

def _update_failed(name, resource):
    changes_dict = {'name': name,
                    'changes': {},
                    'comment': '{0} {1} failed to update'.format(resource,
                                                                 name),
                    'result': False}
    return changes_dict


def _get_non_null_args(**kwargs):
    '''
    Return those kwargs which are not null
    '''
    return dict((key, value,) for key, value in kwargs.iteritems()
                if value is not None)
