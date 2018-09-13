{%- from "ironic/map.jinja" import api with context %}
{%- if api.enabled %}
include:
  - ironic._common
  - ironic.db.offline_sync

ironic_api_packages:
  pkg.installed:
  - names: {{ api.pkgs }}
  - install_recommends: False
  - require_in:
    - sls: ironic._common
    - sls: ironic.db.offline_sync

{{ api.service }}:
  service.running:
    - enable: true
    - full_restart: true
    - require:
      - sls: ironic._common
      - sls: ironic.db.offline_sync
    - watch:
      - file: /etc/ironic/ironic.conf
      - file: /etc/ironic/policy.json
    {%- if api.message_queue.get('ssl',{}).get('enabled', False) %}
      - file: rabbitmq_ca_ironic_file
    {%- endif %}

/etc/ironic/policy.json:
  file.managed:
  - source: salt://ironic/files/{{ api.version }}/policy.json
  - template: jinja
  - require:
    - pkg: ironic_api_packages

{%- endif %}
