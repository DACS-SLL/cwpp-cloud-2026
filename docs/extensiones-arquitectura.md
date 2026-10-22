# Extensión de la arquitectura CWPP

Estado: **diseño propuesto**, no despliegue adicional. El piloto verificado está en la [VM Ubuntu](arquitectura-actual.md) y usa cuatro contenedores. Las siguientes rutas explican cómo ampliarlo sin atribuirles resultados experimentales.

| Entorno | Adaptación de la arquitectura | Telemetría y controles | Límite por resolver |
| --- | --- | --- | --- |
| Más máquinas virtuales Linux | Desplegar el portal o las cargas en VMs separadas; mantener identidad de cada host y una ruta de red privada hacia el gestor central. | Sensor Falco en cada kernel Linux que ejecuta las cargas; agente o recolección segura de logs hacia Wazuh; reglas y retención centralizadas. | Capacidad del gestor, certificados, sincronización horaria y operación de agentes en varios hosts. |
| Kubernetes | Sustituir Compose por Deployments, Services, Secrets y volúmenes persistentes; separar aplicación, base y monitoreo mediante namespaces y políticas de red. | Falco puede ejecutarse en modo DaemonSet por nodo Linux para observar contenedores; logs de aplicación y eventos del clúster se enviarían al analizador; RBAC y políticas de admisión limitarían privilegios. | El despliegue necesita nodos y almacenamiento que este laboratorio no tiene. Las reglas deben evaluarse para reducir ruido y preservar contexto de pod/namespace. |
| Funciones serverless | Instrumentar funciones y pasarelas de API, con identidad de servicio y secretos gestionados por la plataforma. | Enviar logs de ejecución y auditoría del proveedor al analizador; analizar dependencias y permisos antes del despliegue. | En un servicio gestionado como AWS Lambda no se controla el kernel anfitrión; por inferencia, la detección basada en syscalls de Falco no ofrece la misma visibilidad. Se usarían logs de función y eventos de la plataforma. |

## Decisiones que se conservan

- Datos ficticios y mínima exposición de red durante el piloto; en una implantación real se requerirían TLS, gestión de identidades institucionales y políticas de retención.
- Separar rutas de **auditoría de aplicación** y **detección de runtime** para poder atribuir el origen de cada alerta.
- Tratar la base de datos como carga distinta con almacenamiento persistente y permisos específicos. Los eventos `data_access` del portal describen consultas hechas por la aplicación; no constituyen auditoría interna del motor PostgreSQL.
- Dimensionar el gestor de alertas y almacenamiento antes de añadir fuentes. La VM actual ejecuta solo Wazuh manager; un indexer y dashboard permanentes requieren más recursos.

## Orden de ampliación

1. Definir las cargas y responsables por entorno, con fuentes de logs y requisitos de confidencialidad.
2. Medir volumen de eventos, uso de CPU/RAM y retención antes de fijar capacidad.
3. Desplegar sensores y colección con identidad y transporte seguros; validar una alerta real por tipo de carga.
4. Añadir visualización central, reglas de respuesta y procedimientos operativos después de comprobar la calidad de las señales.

Esta descripción satisface el alcance arquitectónico de VMs, Kubernetes y serverless; no afirma que esas plataformas hayan sido instaladas o probadas.

## Referencias de diseño

- [Falco: despliegue en Kubernetes y DaemonSet](https://falco.org/docs/setup/kubernetes/).
- [Wazuh: despliegue y agentes en Kubernetes](https://documentation.wazuh.com/current/deployment-options/deploying-with-kubernetes/kubernetes-deployment.html).
- [Falco: eventos del kernel](https://falco.org/docs/concepts/event-sources/kernel/) y [plugin para CloudTrail](https://falco.org/docs/concepts/event-sources/plugins/cloudtrail/).
- [AWS Lambda: registros de funciones en CloudWatch](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-logs.html). AWS Lambda es solo un ejemplo de plataforma serverless para la extensión propuesta.
