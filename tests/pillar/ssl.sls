# Description:
# test of SSL enabling for the following communication paths:
# - messaging (rabbitmq)

include:
  - .api_single
  - .conductor_single

ironic:
  api:
    message_queue:
      port: 5671
      ssl:
        enabled: True
  conductor:
    message_queue:
      port: 5671
      ssl:
        enabled: True
