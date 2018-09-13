{%- from "ironic/map.jinja" import api,conductor with context %}
{%- if api.get("enabled", False) %}
  {%- set ironic, service_name = api, 'api' %}
{%- elif conductor.get('enabled', False) %}
  {%- set ironic, service_name = conductor, 'conductor' %}
{%- endif %}

include:
  - ironic._ssl.mysql

ironic_common_pkgs:
  pkg.installed:
    - name: 'ironic-common'
    - install_recommends: False
    - require_in:
      - sls: ironic._ssl.mysql

/etc/ironic/ironic.conf:
  file.managed:
  - source: salt://ironic/files/{{ ironic.version }}/ironic.conf
  - template: jinja
  - require:
    - pkg: ironic_common_pkgs
    - sls: ironic._ssl.mysql

{%- if ironic.message_queue.get('ssl',{}).get('enabled', False) %}
rabbitmq_ca_ironic_file:
{%- if ironic.message_queue.ssl.cacert is defined %}
  file.managed:
    - name: {{ ironic.message_queue.ssl.cacert_file }}
    - contents_pillar: ironic:{{ service_name }}:message_queue:ssl:cacert
    - mode: 0444
    - makedirs: true
{%- else %}
  file.exists:
   - name: {{ ironic.message_queue.ssl.get('cacert_file', ironic.cacert_file) }}
{%- endif %}
{%- endif %}
