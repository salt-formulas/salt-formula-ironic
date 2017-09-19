# -*- coding: utf-8 -*-

import logging
import json
from functools import wraps
LOG = logging.getLogger(__name__)

# Import third party libs
HAS_IRONIC = False
try:
    from ironicclient import client
    from ironicclient.common import utils
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


def _get_keystone_endpoint_and_token(**connection_args):
    if connection_args.get('connection_endpoint_type') == None:
        endpoint_type = 'internalURL'
    else:
        endpoint_type = connection_args.get('connection_endpoint_type')

    kstone = __salt__['keystone.auth'](**connection_args)
    endpoint = kstone.service_catalog.url_for(
        service_type='baremetal', endpoint_type=endpoint_type)
    token = kstone.auth_token
    return endpoint, token


def _get_ironic_session(endpoint, token, api_version=None):
    return client.get_client(1, ironic_url=endpoint,
                             os_auth_token=token,
                             os_ironic_api_version=api_version)


def _get_function_attrs(**kwargs):
    connection_args = {'profile': kwargs.pop('profile', None)}
    nkwargs = {}
    for kwarg in kwargs:
        if 'connection_' in kwarg:
            connection_args.update({kwarg: kwargs[kwarg]})
        elif '__' not in kwarg:
            nkwargs.update({kwarg: kwargs[kwarg]})
    return connection_args, nkwargs


def _autheticate(api_version=None):
    def _auth(func_name):
        '''
        Authenticate requests with the salt keystone module and format return data
        '''
        @wraps(func_name)
        def decorator_method(*args, **kwargs):
            '''Authenticate request and format return data'''
            connection_args, nkwargs = _get_function_attrs(**kwargs)
            endpoint, token = _get_keystone_endpoint_and_token(**connection_args)

            ironic_api_version = api_version or connection_args.get(
                'connection_ironic_api_version', None)

            ironic_interface = _get_ironic_session(
                endpoint=endpoint,
                token = token,
                api_version=ironic_api_version)

            return func_name(ironic_interface, *args, **nkwargs)
        return decorator_method
    return _auth


@_autheticate()
def list_nodes(ironic_interface, *args, **kwargs):
    '''
    list all ironic nodes
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.list_nodes
    '''
    return {'nodes': [x.to_dict() for x
                      in ironic_interface.node.list(*args, **kwargs)]}


@_autheticate()
def create_node(ironic_interface, *args, **kwargs):
    '''
    create ironic node
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.create_node
    '''
    return ironic_interface.node.create(*args, **kwargs).to_dict()


@_autheticate()
def delete_node(ironic_interface, node_id):
    '''
    delete ironic node

    :param node_id: UUID or Name of the node.
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.delete_node
    '''
    ironic_interface.node.delete(node_id)


@_autheticate()
def show_node(ironic_interface, node_id):
    '''
    show info about ironic node
    :param node_id: UUID or Name of the node.
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.show_node
    '''
    return ironic_interface.node.get(node_id).to_dict()


@_autheticate()
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


@_autheticate()
def list_ports(ironic_interface, *args, **kwargs):
    '''
    list all ironic ports
    CLI Example:
    .. code-block:: bash
        salt '*' ironic.list_ports
    '''

    return {'ports': [x.to_dict() for x
                      in ironic_interface.port.list(*args, **kwargs)]}

@_autheticate()
def node_set_provision_state(ironic_interface, *args, **kwargs):
    '''Set the provision state for the node.

    CLI Example:
    .. code-block:: bash
        salt '*' ironic.node_set_provision_state node_uuid=node-1 state=active profile=admin_identity
    '''

    ironic_interface.node.set_provision_state(*args, **kwargs)

@_autheticate(api_version='1.28')
def vif_attach(ironic_interface, *args, **kwargs):
    '''Attach vif to a given node.

    CLI Example:
    .. code-block:: bash
        salt '*' ironic.vif_attach node_ident=node-1 vif_id=vif1 profile=admin_identity
    '''

    ironic_interface.node.vif_attach(*args, **kwargs)

@_autheticate(api_version='1.28')
def vif_detach(ironic_interface, *args, **kwargs):
    '''Detach vif from a given node.

    CLI Example:
    .. code-block:: bash
        salt '*' ironic.vif_detach node_ident=node-1 vif_id=vif1 profile=admin_identity
    '''

    ironic_interface.node.vif_detach(*args, **kwargs)

@_autheticate(api_version='1.28')
def vif_list(ironic_interface, *args, **kwargs):
    '''List vifs for a given node.

    CLI Example:
    .. code-block:: bash
        salt '*' ironic.vif_list node_ident=node-1 profile=admin_identity
    '''

    return [vif.to_dict() for vif in ironic_interface.node.vif_list(*args, **kwargs)]

def _merge_profiles(a, b, path=None):
    """Merge b into a"""
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _merge_profiles(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def _get_node_deployment_profile(node_id, profile):
    dp = {}
    nodes = __salt__['pillar.get'](
        'ironic:client:nodes:%s' % profile)

    for node in nodes:
        if node['name'] == node_id:
            return node.get('deployment_profile')


def deploy_node(node_id, image_source=None, root_gb=None,
                image_checksum=None, configdrive=None, vif_id=None,
                deployment_profile=None, partition_profile=None,
                profile=None, **kwargs):
    '''Deploy user image to ironic node

    Deploy node with provided data. If deployment_profile is set,
    try to get deploy data from pillar:

      ironic:
        client:
          deployment_profiles:
            profile1:
              image_source:
              image_checksum:
              ...

    :param node_id: UUID or Name of the node
    :param image_source: URL/glance image uuid to deploy
    :param root_gb: Size of root partition
    :param image_checksum: md5 summ of image, only when image_source
                           is URL
    :param configdrive: URL to or base64 gzipped iso config drive
    :param vif_id: UUID of VIF to attach to node.
    :param deployment_profile: id of the profile to look nodes in.
    :param partition_profile: id of the partition profile to apply.
    :param profile: auth profile to use.

    CLI Example:
    .. code-block:: bash
        salt '*' ironicng.deploy_node node_id=node01 image_source=aaa-bbb-ccc-ddd-eee-fff
    '''
    deploy_params = [image_source, image_checksum, configdrive, vif_id]
    if deployment_profile and any(deploy_params):
        err_msg = ("deployment_profile can' be specified with any "
                   "of %s" % ', '.join(deploy_params))
        LOG.error(err_msg)
        return  _deploy_failed(name, err_msg)

    if partition_profile:
        partition_profile = __salt__['pillar.get'](
          'ironic:client:partition_profiles:%s' % partition_profile)

    if deployment_profile:
        deployment_profile = __salt__['pillar.get'](
            'ironic:client:deployment_profiles:%s' % deployment_profile)
        node_deployment_profile = _get_node_deployment_profile(
            node_id, profile=profile) or {}
        if partition_profile:
            image_properties = deployment_profile['instance_info'].get('image_properties', {})
            image_properties.update(partition_profile)
            deployment_profile['instance_info']['image_properties'] = image_properties
        _merge_profiles(deployment_profile, node_deployment_profile)
    else:
        deployment_profile = {
            'instance_info': {
                'image_source': image_source,
                'image_checksum': image_checksum,
                'root_gb': root_gb,
            },
            'configdrive': configdrive,
            'network': {
                'vif_id': vif_id,
            }
        }

    connection_args, nkwargs = _get_function_attrs(profile=profile, **kwargs)

    endpoint, token = _get_keystone_endpoint_and_token(**connection_args)
    ironic_interface = _get_ironic_session(
            endpoint=endpoint,
            token = token)

    def _convert_to_uuid(resource, name, **connection_args):
        resources =  __salt__['neutronng.list_%s' % resource](
            name=name, **connection_args)

        err_msg = None
        if len(resources) == 0:
            err_msg = "{0} with name {1} not found".format(
                resource, network_name)
        elif len(resources) > 1:
            err_msg = "Multiple {0} with name {1} found.".format(
                resource, network_name)
        else:
            return resources[resource][0]['id']

        LOG.err(err_msg)
        return _deploy_failed(name, err_msg)


    def _prepare_node_for_deploy(ironic_interface,
                                 node_id,
                                 deployment_profile):

        instance_info = deployment_profile.get('instance_info')
        node_attr = []
        for k,v in instance_info.iteritems():
          node_attr.append('instance_info/%s=%s' % (k, json.dumps(v)))

        net = deployment_profile.get('network')
        vif_id = net.get('vif_id')
        network_id = net.get('id')
        network_name = net.get('name')
        if (vif_id and any([network_name, network_id]) or
                (network_name and network_id)):
            err_msg = ("Only one of network:name or network:id or vif_id should be specified.")
            LOG.error(err_msg)
            return  _deploy_failed(name, err_msg)

        if network_name:
            network_id = _convert_to_uuid('networks', network_name, **connection_args)

        if network_id:
            create_port_args = {
                'name': '%s_port' % node_id,
                'network_id': network_id,
            }
            fixed_ips = []
            for fixed_ip in net.get('fixed_ips', []):
                subnet_name = fixed_ip.get('subnet_name')
                subnet_id = fixed_ip.get('subnet_id')
                if subnet_name and subnet_id:
                    err_msg = ("Only one of subnet_name or subnet_id should be specified.")
                    LOG.error(err_msg)
                    return  _deploy_failed(name, err_msg)
                if subnet_name:
                    subnet_id = _convert_to_uuid('subnets', subnet_name, **connection_args)
                if subnet_id:
                    fixed_ips.append({'ip_address': fixed_ip['ip_address'],
                                      'subnet_id': subnet_id})
            if fixed_ips:
                create_port_args['fixed_ips'] = fixed_ips
            create_port_args.update(connection_args)

            vif_id = __salt__['neutronng.create_port'](**create_port_args)

        if vif_id:
            __salt__['ironicng.vif_attach'](node_ident=node_id, vif_id=vif_id, **connection_args)

        configdrive = deployment_profile.get('configdrive')
        if not configdrive:
            metadata = deployment_profile.get('metadata')
            if metadata:
                configdrive_args = {}
                userdata = metadata.get('userdata')
                instance = metadata.get('instance')
                hostname = instance.pop('hostname', node_id)
                if userdata:
                    configdrive_args['user_data'] = userdata
                if instance:
                    configdrive_args.update(instance)
                configdrive = __salt__['configdrive.generate'](
                   dst='/tmp/%s' % node_id, hostname=hostname, ironic_format=True,
                   **configdrive_args)['base64_gzip']

        if configdrive:
            node_attr.append('instance_info/configdrive=%s' % configdrive)

        if node_attr:
            patch = utils.args_array_to_patch('add', node_attr)
            ironic_interface.node.update(node_id, patch).to_dict()


    _prepare_node_for_deploy(ironic_interface, node_id, deployment_profile)

    provision_args = {
      'node_uuid': node_id,
      'state': 'active'
    }
    provision_args.update(connection_args)

    __salt__['ironicng.node_set_provision_state'](**provision_args)
    return _deploy_started(node_id)


def _deploy_failed(name, reason):
    changes_dict = {'name': name,
                    'comment': 'Deployment of node {0} failed to start due to {1}.'.format(name, reason),
                    'result': False}
    return changes_dict


def _deploy_started(name):
    changes_dict = {'name': name,
                    'comment': 'Deployment of node {0} has been started.'.format(name),
                    'result': True}
    return changes_dict
