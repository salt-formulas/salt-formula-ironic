{%- if pillar.ironic is defined %}
include:
{%- if pillar.ironic.api is defined %}
- ironic.api
{% endif %}
{%- if pillar.ironic.conductor is defined %}
- ironic.conductor
{%- endif %}
{%- if pillar.ironic.client is defined %}
- ironic.client
{%- endif %}
{%- endif %}
