{%- from "ironic/map.jinja" import client with context %}
{%- if client.enabled %}

ironic_client_pkg:
  pkg.installed:
    - names: {{ client.pkgs }}
    - install_recommends: False

{%- for identity_name, nodes in client.nodes.iteritems() %}
  {%- for node in nodes %}

node_{{ node.name }}_present:
  ironicng.node_present:
    - name: {{ node.name }}
    - driver: {{ node.driver }}
    - properties: {{ node.properties|default({}) }}
    - profile: {{ identity_name }}
    - driver_info: {{ node.driver_info|default({}) }}

  {%- if node.ports is defined %}
  {%- for port in node.ports %}

{{ node.name }}_port{{ loop.index }}_present:
  ironicng.port_present:
    - address: {{ port.address }}
    - node_name: {{ node.name }}
    {%- if port.local_link_connection is defined %}
    - local_link_connection: {{ port.local_link_connection }}
    {%- endif %}
    {%- if port.ironic_api_version is defined %}
    - ironic_api_version: {{ port.ironic_api_version }}
    {%- endif %}
    - profile: {{ identity_name }}

  {%- endfor %} # end for ports
  {%- endif %} # end if node.ports defined

  {%- endfor %} # end for nodes
{%- endfor %} # end client.nodes.iteritems

{%- endif %} # end if client.enabled
