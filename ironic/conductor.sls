{%- from "ironic/map.jinja" import conductor with context %}
{%- if conductor.enabled %}
include:
  - ironic._common

ironic_conductor_packages:
  pkg.installed:
  - names: {{ conductor.pkgs }}
  - install_recommends: False

{{ conductor.service }}:
  service.running:
    - enable: true
    - full_restart: true
    - watch:
      - file: /etc/ironic/ironic.conf
    {%- if conductor.message_queue.get('ssl',{}).get('enabled', False) %}
      - file: rabbitmq_ca
    {%- endif %}

ironic_dirs:
  file.directory:
    - names:
      - {{ conductor.tftp_root }}
      - {{ conductor.http_root }}
      makedirs: True
      user: 'ironic'
      group: 'ironic'
    - require:
      - pkg: ironic_conductor_packages

ironic_copy_pxelinux.0:
  file.managed:
    - name: {{ conductor.tftp_root }}/pxelinux.0
    - source: {{ conductor.pxelinux_path }}/pxelinux.0
    - user: 'ironic'
    - group: 'ironic'
    - require:
      - file: ironic_dirs

{% for file in conductor.syslinux_files %}
ironic_copy_{{ file }}:
  file.managed:
    - name: {{ conductor.tftp_root }}/{{ file }}
    - source: {{ conductor.syslinux_path }}/{{ file }}
    - user: 'ironic'
    - group: 'ironic'
    - require:
      - file: ironic_dirs
{%- endfor %}

{% for file in conductor.ipxe_rom_files %}
ironic_copy_{{ file }}:
  file.managed:
    - name: {{ conductor.tftp_root }}/{{ file }}
    - source: {{ conductor.ipxe_rom_path }}/{{ file }}
    - user: 'ironic'
    - group: 'ironic'
    - require:
      - file: ironic_dirs
{%- endfor %}

ironic_tftp_map_file:
  file.managed:
    - name: {{ conductor.tftp_root }}/map-file
    - contents: |
        r ^[^/] /\0
        r ^({{ conductor.tftp_root }}) /\2
    - user: 'ironic'
    - group: 'ironic'
    - require:
      - file: ironic_dirs

{%- if conductor.http_images is defined %}
{%- for image in conductor.http_images %}

image_{{ image.name }}:
  file.managed:
    - name: {{ conductor.http_root }}/{{ image.name }}
    - source: {{ image.source }}
    - source_hash: md5={{ image.md5summ }}
    - user: 'ironic'
    - group: 'ironic'

{%- endfor %}
{%- endif %}

{%- endif %}
