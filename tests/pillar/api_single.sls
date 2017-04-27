ironic:
  api:
    enabled: true
    version: mitaka
    bind:
      address: '0.0.0.0'
      port: 6385
    message_queue:
      engine: rabbitmq
      host: '127.0.0.1'
      port: 5672
      user: openstack
      password: workshop
      virtual_host: '/openstack'
    database:
      engine: mysql
      host: '127.0.0.1'
      port: 3306
      name: ironic
      user: ironic
      password: workshop
    identity:
      engine: 'noauth'
