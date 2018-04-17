{%- from "ironic/map.jinja" import api with context %}
{%- if api.enabled %}
include:
  - ironic._common

ironic_api_packages:
  pkg.installed:
  - names: {{ api.pkgs }}
  - install_recommends: False

{%- if api.api_type not in ["deploy"] %}
ironic_install_database:
  cmd.run:
  - names:
    - ironic-dbsync --config-file /etc/ironic/ironic.conf upgrade
  - require:
    - file: /etc/ironic/ironic.conf
{%- endif %}

{{ api.service }}:
  service.running:
    - enable: true
    - full_restart: true
    - watch:
      - file: /etc/ironic/ironic.conf
      - file: /etc/ironic/policy.json
    {%- if api.message_queue.get('ssl',{}).get('enabled', False) %}
      - file: rabbitmq_ca_ironic_file
    {%- endif %}
    {%- if api.database.get('ssl',{}).get('enabled', False) %}
      - file: mysql_ca_ironic_file
    {%- endif %}

/etc/ironic/policy.json:
  file.managed:
  - source: salt://ironic/files/{{ api.version }}/policy.json
  - template: jinja
  - require:
    - pkg: ironic_api_packages

{%- endif %}
