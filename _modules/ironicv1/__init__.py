try:
    import os_client_config
    from keystoneauth1 import exceptions as ka_exceptions
    REQUIREMENTS_MET = True
except ImportError:
    REQUIREMENTS_MET = False

from ironicv1 import nodes
from ironicv1 import ports
from ironicv1 import drivers
from ironicv1 import chassis
from ironicv1 import volumes

node_boot_device_get = nodes.node_boot_device_get
node_boot_device_get_supported = nodes.node_boot_device_get_supported
node_boot_device_set = nodes.node_boot_device_set
node_console_get = nodes.node_console_get
node_console_start_stop = nodes.node_console_start_stop
node_create = nodes.node_create
node_delete = nodes.node_delete
node_get_details = nodes.node_get_details
node_inject_nmi = nodes.node_inject_nmi
node_list = nodes.node_list
node_maintenance_flag_clear = nodes.node_maintenance_flag_clear
node_maintenance_flag_set = nodes.node_maintenance_flag_set
node_power_state_change = nodes.node_power_state_change
node_provision_state_change = nodes.node_provision_state_change
node_raid_config_set = nodes.node_raid_config_set
node_state_summary = nodes.node_state_summary
node_traits_delete = nodes.node_traits_delete
node_traits_delete_single = nodes.node_traits_delete_single
node_traits_list = nodes.node_traits_list
node_traits_set = nodes.node_traits_set
node_traits_set_single = nodes.node_traits_set_single
node_update = nodes.node_update
node_validate = nodes.node_validate
node_vif_attach = nodes.node_vif_attach
node_vif_detach = nodes.node_vif_detach
node_vif_list = nodes.node_vif_list

driver_get_details = drivers.driver_get_details
driver_get_logical_disk_properties = drivers.driver_get_logical_disk_properties
driver_get_properties = drivers.driver_get_properties
driver_list = drivers.driver_list

port_create = ports.port_create
port_delete = ports.port_delete
port_get_details = ports.port_get_details
port_list = ports.port_list
port_list_details = ports.port_list_details
port_update = ports.port_update

chassis_create = chassis.chassis_create
chassis_delete = chassis.chassis_delete
chassis_get_details = chassis.chassis_get_details
chassis_list = chassis.chassis_list
chassis_list_details = chassis.chassis_list_details
chassis_update = chassis.chassis_update

volume_connector_create = volumes.volume_connector_create
volume_connector_delete = volumes.volume_connector_delete
volume_connector_get_details = volumes.volume_connector_get_details
volume_connector_list = volumes.volume_connector_list
volume_connector_update = volumes.volume_connector_update
volume_resource_list = volumes.volume_resource_list
volume_target_create = volumes.volume_target_create
volume_target_delete = volumes.volume_target_delete
volume_target_get_details = volumes.volume_target_get_details
volume_target_list = volumes.volume_target_list
volume_target_update = volumes.volume_target_update


__all__ = (
    # node.py
    'node_list', 'node_boot_device_get', 'node_boot_device_get_supported',
    'node_boot_device_set', 'node_console_get', 'node_console_start_stop',
    'node_create', 'node_delete', 'node_get_details', 'node_inject_nmi',
    'node_maintenance_flag_clear', 'node_maintenance_flag_set',
    'node_power_state_change', 'node_provision_state_change',
    'node_raid_config_set', 'node_state_summary', 'node_traits_delete',
    'node_traits_delete_single', 'node_traits_list', 'node_traits_set',
    'node_traits_set_single', 'node_update', 'node_validate',
    'node_vif_attach', 'node_vif_detach', 'node_vif_list',

    # driver.py
    'driver_get_details', 'driver_get_logical_disk_properties',
    'driver_get_properties', 'driver_list',

    # ports.py
    'port_create', 'port_delete', 'port_get_details', 'port_list',
    'port_update', 'port_list_details',

    # chassis.py
    'chassis_create', 'chassis_delete', 'chassis_get_details', 'chassis_list',
    'chassis_list_details', 'chassis_update',

    # volumes.py
    'volume_connector_create', 'volume_connector_delete',
    'volume_connector_get_details', 'volume_connector_list',
    'volume_connector_update', 'volume_resource_list', 'volume_target_create',
    'volume_target_delete', 'volume_target_get_details', 'volume_target_list',
    'volume_target_update',
)


def __virtual__():
    """Only load ironicv1 if requirements are available."""
    if REQUIREMENTS_MET:
        return 'ironicv1'
    else:
        return False, ("The ironicv1 execution module cannot be loaded: "
                       "os_client_config or keystoneauth are unavailable.")
