{%- from "ironic/map.jinja" import api with context %}

ironic_install_database:
  cmd.run:
  - name: ironic-dbsync --config-file /etc/ironic/ironic.conf upgrade
    {%- if grains.get('noservices') or ( api.api_type in ["deploy"] and api.get('role', 'primary') == 'secondary' ) %}
  - onlyif: /bin/false
    {%- endif %}
