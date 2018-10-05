import logging

log = logging.getLogger(__name__)


def __virtual__():
    return 'ironicv1' if 'ironicv1.node_list' in __salt__ else False


def _ironicv1_call(fname, *args, **kwargs):
    return __salt__['ironicv1.{}'.format(fname)](*args, **kwargs)


def node_present(name, cloud_name, driver, **kwargs):
    resource = 'node'
    microversion = kwargs.pop('microversion', '1.16')
    try:
        method_name = '{}_get_details'.format(resource)
        exact_resource = _ironicv1_call(
            method_name, name, cloud_name=cloud_name,
            microversion=microversion
        )
    except Exception as e:
        if 'Not Found' in str(e):
            try:
                method_name = '{}_create'.format(resource)
                resp = _ironicv1_call(
                    method_name, driver, name=name, cloud_name=cloud_name,
                    microversion=microversion,
                    **kwargs
                )
            except Exception as e:
                log.exception('Ironic {0} create failed with {1}'.
                              format('node', e))
                return _failed('create', name, resource)
            return _succeeded('create', name, resource, resp)
        raise

    to_change = []
    for prop in kwargs:
        path = prop.replace('~', '~0').replace('/', '~1')
        if prop in exact_resource:
            if exact_resource[prop] != kwargs[prop]:
                to_change.append({
                    'op': 'replace',
                    'path': '/{}'.format(path),
                    'value': kwargs[prop],
                })
        else:
            to_change.append({
                'op': 'add',
                'path': '/{}'.format(path),
                'value': kwargs[prop],
            })
    if to_change:
        try:
            method_name = '{}_update'.format(resource)
            resp = _ironicv1_call(
                method_name, name, properties=to_change,
                microversion=microversion, cloud_name=cloud_name,
            )
        except Exception as e:
            log.exception(
                'Ironic {0} update failed with {1}'.format(resource, e))
            return _failed('update', name, resource)
        return _succeeded('update', name, resource, resp)
    return _succeeded('no_changes', name, resource)


def node_absent(name, cloud_name, **kwargs):
    resource = 'node'
    microversion = kwargs.pop('microversion', '1.16')
    try:
        method_name = '{}_get_details'.format(resource)
        _ironicv1_call(
            method_name, name, cloud_name=cloud_name,
            microversion=microversion
        )
    except Exception as e:
        if 'Not Found' in str(e):
            return _succeeded('absent', name, resource)
    try:
        method_name = '{}_delete'.format(resource)
        _ironicv1_call(
            method_name, name, cloud_name=cloud_name, microversion=microversion
        )
    except Exception as e:
        log.error('Ironic delete {0} failed with {1}'.format(resource, e))
        return _failed('delete', name, resource)
    return _succeeded('delete', name, resource)


def port_present(name, cloud_name, node, address, **kwargs):
    resource = 'port'
    microversion = kwargs.pop('microversion', '1.16')
    method_name = '{}_list'.format(resource)
    exact_resource = _ironicv1_call(
        method_name, node=node, address=address,
        cloud_name=cloud_name, microversion=microversion
    )['ports']
    if len(exact_resource) == 0:
        try:
            node_uuid = _ironicv1_call(
                'node_get_details', node, cloud_name=cloud_name,
                microversion=microversion
            )['uuid']
        except Exception as e:
            return _failed('create', node, "port's node")
        try:
            method_name = '{}_create'.format(resource)
            resp = _ironicv1_call(
                method_name, node_uuid, address, cloud_name=cloud_name,
                microversion=microversion, **kwargs)
        except Exception as e:
            log.exception('Ironic {0} create failed with {1}'.
                          format('node', e))
            return _failed('create', name, resource)
        return _succeeded('create', name, resource, resp)
    if len(exact_resource) == 1:
        exact_resource = exact_resource[0]
        to_change = []
        for prop in kwargs:
            path = prop.replace('~', '~0').replace('/', '~1')
            if prop in exact_resource:
                if exact_resource[prop] != kwargs[prop]:
                    to_change.append({
                        'op': 'replace',
                        'path': '/{}'.format(path),
                        'value': kwargs[prop],
                    })
            else:
                to_change.append({
                    'op': 'add',
                    'path': '/{}'.format(path),
                    'value': kwargs[prop],
                })
        if to_change:
            try:
                method_name = '{}_update'.format(resource)
                resp = _ironicv1_call(
                    method_name, name, properties=to_change,
                    microversion=microversion, cloud_name=cloud_name,
                )
            except Exception as e:
                log.exception(
                    'Ironic {0} update failed with {1}'.format(resource, e))
                return _failed('update', name, resource)
            return _succeeded('update', name, resource, resp)
        return _succeeded('no_changes', name, resource)
    else:
        return _failed('find', name, resource)


def port_absent(name, cloud_name, node, address, **kwargs):
    resource = 'port'
    microversion = kwargs.pop('microversion', '1.16')
    method_name = '{}_list'.format(resource)
    exact_resource = _ironicv1_call(
        method_name, node=node, address=address,
        cloud_name=cloud_name, microversion=microversion
    )['ports']
    if len(exact_resource) == 0:
            return _succeeded('absent', name, resource)
    elif len(exact_resource) == 1:
        port_id = exact_resource[0]['uuid']
        try:
            method_name = '{}_delete'.format(resource)
            _ironicv1_call(
                method_name, port_id, cloud_name=cloud_name,
                microversion=microversion
            )
        except Exception as e:
            log.error('Ironic delete {0} failed with {1}'.format(resource, e))
            return _failed('delete', name, resource)
        return _succeeded('delete', name, resource)
    else:
        return _failed('find', name, resource)


def _succeeded(op, name, resource, changes=None):
    msg_map = {
        'create': '{0} {1} created',
        'delete': '{0} {1} removed',
        'update': '{0} {1} updated',
        'no_changes': '{0} {1} is in desired state',
        'absent': '{0} {1} not present'
    }
    changes_dict = {
        'name': name,
        'result': True,
        'comment': msg_map[op].format(resource, name),
        'changes': changes or {},
    }
    return changes_dict


def _failed(op, name, resource):
    msg_map = {
        'create': '{0} {1} failed to create',
        'delete': '{0} {1} failed to delete',
        'update': '{0} {1} failed to update',
        'find': '{0} {1} found multiple {0}'
    }
    changes_dict = {
        'name': name,
        'result': False,
        'comment': msg_map[op].format(resource, name),
        'changes': {},
    }
    return changes_dict
