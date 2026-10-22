# Arquitectura implementada y verificada

![Diagrama de arquitectura del portal UTS](arquitectura-actual.svg)

**Estado:** portal y base saludables; consultas de 20 estudiantes, 7 cursos y 60 matrículas validadas. Wazuh y Falco aún no forman parte de esta arquitectura. El dashboard y las alertas de seguridad se incorporarán solo después de instalarlos y verificarlos.

Este diagrama corresponde a la fase inicial en Docker Desktop. Las pruebas posteriores de Wazuh en Windows y de Falco junto al portal en Ubuntu VirtualBox están documentadas en [fase D](fase-d-wazuh.md) y [fase F](fase-f-falco-ubuntu.md). No representa un despliegue conjunto de Wazuh y Falco.
