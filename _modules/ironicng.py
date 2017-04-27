# -*- coding: utf-8 -*-

import logging
from functools import wraps
LOG = logging.getLogger(__name__)

# Import third party libs
HAS_IRONIC = False
try:
    from ironicclient import client
    HAS_IRONIC = True
except ImportError:
    pass

__opts__ = {}


def __virtual__():
    '''
    Only load this module if ironic is installed on this minion.
    '''
    if HAS_IRONIC:
        return 'ironicng'
    return False


def _autheticate(func_name):
    '''
    Authenticate requests with the salt keystone module and format return data
    '''
    @wraps(func_name)
    def decorator_method(*args, **kwargs):
        '''
        Authenticate request and format return data
        '''
        connection_args = {'profile': kwargs.pop('profile', None)}
        nkwargs = {}
        for kwarg in kwargs:
            if 'connection_' in kwarg:
                connection_args.update({kwarg: kwargs[kwarg]})
            elif '__' not in kwarg:
                nkwargs.update({kwarg: kwargs[kwarg]})
        kstone = __salt__['keystone.auth'](**connection_args)
        token = kstone.auth_token

        if kwargs.get('connection_endpoint_type') == None:
            endpoint_type = 'internalURL'
        else:
            endpoint_type = kwargs.get('connection_endpoint_type')

        endpoint = kstone.service_catalog.url_for(
            service_type='baremetal',
            endpoint_type=endpoint_type)
        ironic_interface = client.get_client(
            1,
            ironic_url=endpoint, os_auth_token=token)
        return func_name(ironic_interface, *args, **nkwargs)
    return decorator_method


@_autheticate
def list_nodes(ironic_interface, **kwargs):
    '''
    list all ironic nodes
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.list_nodes
    '''
    return {'nodes': [x.to_dict() for x
                      in ironic_interface.node.list(**kwargs)]}


@_autheticate
def create_node(ironic_interface, **kwargs):
    '''
    create ironic node
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.create_node
    '''
    return ironic_interface.node.create(**kwargs).to_dict()


@_autheticate
def delete_node(ironic_interface, node_id):
    '''
    delete ironic node

    :param node_id: UUID or Name of the node.
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.delete_node
    '''
    ironic_interface.node.delete(node_id)


@_autheticate
def show_node(ironic_interface, node_id):
    '''
    show info about ironic node
    :param node_id: UUID or Name of the node.
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.show_node
    '''
    return ironic_interface.node.get(node_id).to_dict()


@_autheticate
def create_port(ironic_interface, address, node_name=None,
                node_uuid=None, **kwargs):
    '''
    create ironic port
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.crate_port
    '''
    node_uuid = node_uuid or ironic_interface.node.get(
        node_name).to_dict()['uuid']
    return ironic_interface.port.create(
        address=address, node_uuid=node_uuid, **kwargs).to_dict()


@_autheticate
def list_ports(ironic_interface, **kwargs):
    '''
    list all ironic ports
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.list_ports
    '''

    return {'ports': [x.to_dict() for x
                      in ironic_interface.port.list(**kwargs)]}


