{%- from "ironic/map.jinja" import api,conductor with context %}
{%- if api.get("enabled", False) %}
  {%- set ironic, service_name = api, 'api' %}
{%- elif conductor.get('enabled', False) %}
  {%- set ironic, service_name = conductor, 'conductor' %}
{%- endif %}

ironic_ssl_rabbitmq:
  test.show_notification:
    - text: "Running ironic._ssl.rabbitmq"

{%- if ironic.message_queue.get('x509',{}).get('enabled',False) %}

  {%- set ca_file=ironic.message_queue.x509.ca_file %}
  {%- set key_file=ironic.message_queue.x509.key_file %}
  {%- set cert_file=ironic.message_queue.x509.cert_file %}

rabbitmq_ironic_ssl_x509_ca:
  {%- if ironic.message_queue.x509.cacert is defined %}
  file.managed:
    - name: {{ ca_file }}
    - contents_pillar: ironic:{{ service_name }}:message_queue:x509:cacert
    - mode: 444
    - user: ironic
    - group: ironic
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ ca_file }}
  {%- endif %}

rabbitmq_ironic_client_ssl_cert:
  {%- if ironic.message_queue.x509.cert is defined %}
  file.managed:
    - name: {{ cert_file }}
    - contents_pillar: ironic:{{ service_name }}:message_queue:x509:cert
    - mode: 440
    - user: ironic
    - group: ironic
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ cert_file }}
  {%- endif %}

rabbitmq_ironic_client_ssl_private_key:
  {%- if ironic.message_queue.x509.key is defined %}
  file.managed:
    - name: {{ key_file }}
    - contents_pillar: ironic:{{ service_name }}:message_queue:x509:key
    - mode: 400
    - user: ironic
    - group: ironic
    - makedirs: true
  {%- else %}
  file.exists:
    - name: {{ key_file }}
  {%- endif %}

rabbitmq_ironic_ssl_x509_set_user_and_group:
  file.managed:
    - names:
      - {{ ca_file }}
      - {{ cert_file }}
      - {{ key_file }}
    - user: ironic
    - group: ironic

{% elif ironic.message_queue.get('ssl',{}).get('enabled',False) %}
rabbitmq_ca_ironic_client:
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
