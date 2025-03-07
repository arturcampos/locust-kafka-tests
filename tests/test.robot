* Settings *
Library    OperatingSystem
Library  ConfluentKafkaLibrary
Library  Collections
* Variables *
${nome}    Mundo

* Test Cases *
Dizer Olá
    [Documentation]    This is a simple test that produces a message and consume from kafka
    [Tags]    simples
        ${group_id}=  Create Consumer  auto_offset_reset=beginning  server=127.0.0.1  port=9092
        ${topics}=  List Topics  ${group_id}
        LOG  ${topics}
        Dictionary Should Contain Key  ${topics}  in-topic
        ${message}=  Subscribe Topic   ${group_id}  out-topic
        ${result}=  Poll  group_id=${group_id}	max_records=5
        LOG  ${result}
        Unsubscribe	${group_id}		
        [Teardown]  Close Consumer  ${group_id}