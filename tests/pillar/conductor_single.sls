ironic:
  conductor:
    version: ocata
    enabled: true
    tftp_root: '/var/lib/tftpboot'
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
    http_root: '/var/www/httproot'
  tftpd_hpa:
    server:
      bind:
        address: '0.0.0.0'
        port: 69
      username: 'ironic'
      path: ${ironic:conductor:tftp_root}
      options:
        - secure
        - map-file: '${ironic:conductor:tftp_root}/map-file'
