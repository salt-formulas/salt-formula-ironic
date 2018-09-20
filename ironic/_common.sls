{%- from "ironic/map.jinja" import api,conductor with context %}
{%- if api.get("enabled", False) %}
  {%- set ironic, service_name = api, 'api' %}
{%- elif conductor.get('enabled', False) %}
  {%- set ironic, service_name = conductor, 'conductor' %}
{%- endif %}

include:
  - ironic._ssl.mysql
  - ironic._ssl.rabbitmq

ironic_common_pkgs:
  pkg.installed:
    - name: 'ironic-common'
    - install_recommends: False
    - require_in:
      - sls: ironic._ssl.mysql
      - sls: ironic._ssl.rabbitmq

/etc/ironic/ironic.conf:
  file.managed:
  - source: salt://ironic/files/{{ ironic.version }}/ironic.conf
  - template: jinja
  - require:
    - pkg: ironic_common_pkgs
    - sls: ironic._ssl.mysql
    - sls: ironic._ssl.rabbitmq
