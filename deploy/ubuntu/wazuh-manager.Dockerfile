FROM wazuh/wazuh-manager:4.14.9

# El piloto usa solo análisis local; no inicia Filebeat sin indexer.
RUN rm -rf /etc/services.d/filebeat
