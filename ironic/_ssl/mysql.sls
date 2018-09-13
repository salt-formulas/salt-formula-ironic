{%- from "ironic/map.jinja" import api,conductor with context %}
{%- if api.get("enabled", False) %}
  {%- set ironic, service_name = api, 'api' %}
{%- elif conductor.get('enabled', False) %}
  {%- set ironic, service_name = conductor, 'conductor' %}
{%- endif %}

ironic_ssl_mysql:
  test.show_notification:
    - text: "Running ironic._ssl.mysql"

{%- if ironic.database.get('x509',{}).get('enabled',False) %}

  {%- set ca_file=ironic.database.x509.ca_file %}
  {%- set key_file=ironic.database.x509.key_file %}
  {%- set cert_file=ironic.database.x509.cert_file %}

mysql_ironic_ssl_x509_ca:
  {%- if ironic.database.x509.cacert is defined %}
  file.managed:
    - name: {{ ca_file }}
    - contents_pillar: ironic:{{ service_name }}:database:x509:cacert
    - mode: 444
    - user: ironic
    - group: ironic
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ ca_file }}
  {%- endif %}

mysql_ironic_client_ssl_cert:
  {%- if ironic.database.x509.cert is defined %}
  file.managed:
    - name: {{ cert_file }}
    - contents_pillar: ironic:{{ service_name }}:database:x509:cert
    - mode: 440
    - user: ironic
    - group: ironic
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ cert_file }}
  {%- endif %}

mysql_ironic_client_ssl_private_key:
  {%- if ironic.database.x509.key is defined %}
  file.managed:
    - name: {{ key_file }}
    - contents_pillar: ironic:{{ service_name }}:database:x509:key
    - mode: 400
    - user: ironic
    - group: ironic
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ key_file }}
  {%- endif %}

mysql_ironic_ssl_x509_set_user_and_group:
  file.managed:
    - names:
      - {{ ca_file }}
      - {{ cert_file }}
      - {{ key_file }}
    - user: ironic
    - group: ironic

{%- elif ironic.database.get('ssl',{}).get('enabled', False) %}
mysql_ca_ironic_file:
{%- if ironic.database.ssl.cacert is defined %}
  file.managed:
    - name: {{ ironic.databse.ssl.cacert_file }}
    - contents_pillar: ironic:{{ service_name }}:database:ssl:cacert
    - mode: 0444
    - makedirs: true
{%- else %}
  file.exists:
   - name: {{ ironic.database.ssl.get('cacert_file', ironic.cacert_file) }}
{%- endif %}

{%- endif %}