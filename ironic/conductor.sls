{%- from "ironic/map.jinja" import conductor with context %}
{%- if conductor.enabled %}
include:
  - ironic._common

ironic_conductor_packages:
  pkg.installed:
  - names: {{ conductor.pkgs }}
  - install_recommends: False
  - require_in:
    - sls: ironic._common

{{ conductor.service }}:
  service.running:
    - enable: true
    - full_restart: true
    - watch:
      - file: /etc/ironic/ironic.conf
    - require:
      - pkg: ironic_conductor_packages
      - sls: ironic._common

ironic_dirs:
  file.directory:
    - names:
      - {{ conductor.tftp_root }}
      - {{ conductor.http_root }}
      makedirs: True
      user: 'ironic'
      group: 'ironic'
    - require_in:
      - pkg: ironic_conductor_packages

ironic_copy_pxelinux.0:
  file.managed:
    - name: {{ conductor.tftp_root }}/pxelinux.0
    - source: {{ conductor.pxelinux_path }}/pxelinux.0
    - user: 'ironic'
    - group: 'ironic'
    - require:
      - file: ironic_dirs
      - pkg: ironic_conductor_packages

{%- if conductor.uefi.enabled %}
ironic_conductor_uefi_packages:
  pkg.installed:
  - names: {{ conductor.uefi_pkgs }}
  - install_recommends: False
  - require_in:
    - sls: ironic._common

{% for file, args in conductor.uefi_files.items() %}
ironic_copy_uefi_{{ file }}:
  file.managed:
    - name: {{ conductor.tftp_root }}/{{ args['dst'] }}
    - source: {{ args['src'] }}
    - user: 'ironic'
    - group: 'ironic'
    - require:
      - file: ironic_dirs
      - file: ironic_uefi_grub_dir
      - pkg: ironic_conductor_packages
      - pkg: ironic_conductor_uefi_packages
{%- endfor %}

ironic_uefi_grub_dir:
  file.directory:
    - name: {{ conductor.tftp_root }}/{{ conductor.uefi.grub_dir_name }}
      makedirs: True
      user: 'ironic'
      group: 'ironic'
    - require_in:
      - pkg: ironic_conductor_packages
      - pkg: ironic_conductor_uefi_packages

ironic_uefi_grub_cfg:
  file.managed:
    - name: {{ conductor.tftp_root }}/{{ conductor.uefi.grub_dir_name }}/grub.cfg
    - contents: 'GRUB_DIR={{ conductor.tftp_root }}/{{ conductor.uefi.grub_dir_name }}'
    - user: 'ironic'
    - group: 'ironic'
    - mode: 644
    - require:
      - file: ironic_dirs
      - file: ironic_uefi_grub_dir
      - pkg: ironic_conductor_packages
      - pkg: ironic_conductor_uefi_packages
{%- endif %}

{% for file in conductor.syslinux_files %}
ironic_copy_{{ file }}:
  file.managed:
    - name: {{ conductor.tftp_root }}/{{ file }}
    - source: {{ conductor.syslinux_path }}/{{ file }}
    - user: 'ironic'
    - group: 'ironic'
    - require:
      - file: ironic_dirs
      - pkg: ironic_conductor_packages
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
      - pkg: ironic_conductor_packages
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
      - pkg: ironic_conductor_packages

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
