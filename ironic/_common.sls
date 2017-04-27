{%- from "ironic/map.jinja" import api,conductor with context %}
{%- if api.get("enabled", False) %}
  {%- set ironic = api %}
{%- elif conductor.get('enabled', False) %}
  {%- set ironic = conductor %}
{%- endif %}

ironic_common_pkgs:
  pkg.installed:
    - name: 'ironic-common'
    - install_recommends: False

/etc/ironic/ironic.conf:
  file.managed:
  - source: salt://ironic/files/{{ ironic.version }}/ironic.conf
  - template: jinja
  - require:
    - pkg: ironic_common_pkgs
