{%- from "ironic/map.jinja" import api with context %}

ironic_online_data_migrations:
  cmd.run:
  - name: ironic-dbsync online_data_migrations
    {%- if grains.get('noservices') or ( api.api_type in ["deploy"] and api.get('role', 'primary') == 'secondary' ) %}
  - onlyif: /bin/false
    {%- endif %}
