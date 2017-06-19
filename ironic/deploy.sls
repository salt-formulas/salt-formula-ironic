{%- from "ironic/map.jinja" import client,deploy with context %}

{%- if deploy.enabled %}

{%- for identity_name, nodes in deploy.nodes.iteritems() %}
  {%- for node in nodes %}
    {%- if node.deployment_profile %}

{%- set ir_n = salt['ironicng.show_node'](node_id=node.name, profile=identity_name) %}
{%- if ir_n['provision_state'] == 'available' and ir_n['maintenance'] == False %}

node_{{ node.name }}_deployment_started:
  module.run:
    - name: ironicng.deploy_node
    - node_id: {{ node.name }}
    - profile: {{ identity_name }}
    - deployment_profile: {{ node.deployment_profile }}
    - partition_profile: {{ node.partition_profile|default(None) }}

{%- else %}
node_{{ node.name }}_deployment_started:
  test.show_notification:
  - text: |
      Didn't start deployment on node as node provision_state is
      {{ ir_n['provision_state'] }} and maintenance is {{ ir_n['maintenance'] }}

{%- endif %}

    {%- endif %} {#- end if node.deployment_profile #}
  {%- endfor %} {#- end for nodes #}
{%- endfor %} {#- end client.nodes.iteritems #}

{%- endif %} {#- end if deploy.enabled #}
