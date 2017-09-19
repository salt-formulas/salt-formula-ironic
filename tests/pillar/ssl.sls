# Description:
# test of SSL enabling for the following communication paths:
# - messaging (rabbitmq)
# - database

include:
  - .api_single
  - .conductor_single

ironic:
  api:
    database:
      ssl:
        enabled: True
    message_queue:
      port: 5671
      ssl:
        enabled: True
  conductor:
    database:
      ssl:
        enabled: True
    message_queue:
      port: 5671
      ssl:
        enabled: True
