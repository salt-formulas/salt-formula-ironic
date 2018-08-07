{%- from "ironic/map.jinja" import client with context %}
{%- if client.enabled %}

ironic_client_pkg:
  pkg.installed:
    - names: {{ client.pkgs }}
    - install_recommends: False

{%- for identity_name, nodes in client.nodes.iteritems() %}
  {%- for node in nodes %}

node_{{ node.name }}_present:
  ironicv1.node_present:
    - name: {{ node.name }}
    - driver: {{ node.driver }}
    - driver_info: {{ node.driver_info|default({}) }}
    - cloud_name: {{ client.cloud_name }}
    - properties: {{ node.properties|default({}) }}
    {%- if node.network_interface is defined %}
    - network_interface: {{ node.network_interface }}
    {%- endif %}
    {%- if node.ironic_api_version is defined %}
    - ironic_api_version: "{{ node.ironic_api_version }}"
    {%- endif %}

  {%- if node.ports is defined %}
  {%- for port in node.ports %}

{{ node.name }}_port{{ loop.index }}_present:
  ironicv1.port_present:
    - address: {{ port.address }}
    - node: {{ node.name }}
    - cloud_name: {{ client.cloud_name }}
    {%- if port.local_link_connection is defined %}
    - local_link_connection: {{ port.local_link_connection }}
    {%- endif %}
    {%- if port.ironic_api_version is defined %}
    - ironic_api_version: "{{ port.ironic_api_version }}"
    {%- endif %}

  {%- endfor %} # end for ports
  {%- endif %} # end if node.ports defined

  {%- endfor %} # end for nodes
{%- endfor %} # end client.nodes.iteritems

{%- endif %} # end if client.enabled
