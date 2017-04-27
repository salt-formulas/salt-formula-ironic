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
    - properties: {{ node.properties }}
    - profile: {{ identity_name }}
    - driver_info: {{ node.driver_info }}

  {%- for port in node.ports %}

{{ node.name }}_port{{ loop.index }}_present:
  ironicng.port_present:
    - address: {{ port.address }}
    - node_name: {{ node.name }}
    - profile: {{ identity_name }}

  {%- endfor %} # end for ports

  {%- endfor %} # end for nodes
{%- endfor %} # end client.nodes.iteritems

{%- endif %} # end if client.enabled
