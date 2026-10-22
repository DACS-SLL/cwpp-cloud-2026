# Fase F: detección de Falco en Ubuntu VirtualBox

Fecha de las alertas: 22 de octubre de 2026, 00:38 y 00:39 UTC (21 de octubre en Perú).

## Arquitectura probada

En el mismo equipo físico, una VM Ubuntu Desktop 22.04 ejecuta Docker Engine, PostgreSQL 17, el portal `d4c5g/uts-cwpp-portal:2026-10-21` y Falco 0.45.0. Portal y base aparecieron `healthy`; `python3 scripts/smoke_portal.py` pasó para `estudiante_demo`, `docente_demo` y `admin_demo`. Desde Windows se abrió el portal de la VM por el puerto NAT `localhost:18080`.

Falco arrancó en la VM con la fuente de eventos `syscall` y la sonda modern BPF. Sus logs indican `Loaded event sources: syscall` y `Opening 'syscall' source with modern BPF probe`. Esa inicialización, por sí sola, no era prueba de detección; las alertas siguientes sí relacionan el evento con el contenedor del portal.

## Prueba controlada y resultado

Se ejecutó una shell de prueba en el contenedor del portal. La segunda ejecución usó:

```bash
sudo docker exec -it uts-portal sh -c 'echo prueba-falco'
```

Falco emitió dos mensajes de nivel `Notice` con la descripción `A shell was spawned in a container with an attached terminal`. El primero se registró a las **00:38:30 UTC** con `command=sh`; el segundo, a las **00:39:39 UTC** con `command=sh -c echo prueba-falco`. Ambos mostraron `container_name=uts-portal`, `container_image_repository=d4c5g/uts-cwpp-portal` y `container_image_tag=2026-10-21`. Los datos se transcribieron de la salida visible en la captura local `docs/evidencias/capturas/20-falco-alerta-portal.png`.

Para consultar nuevamente las entradas:

```bash
sudo docker logs --tail=100 uts-falco 2>&1 | grep -F 'container_name=uts-portal'
```

El filtro anterior `grep -F 'Terminal shell in container'` no devolvió líneas porque buscaba el **nombre de la regla** y Falco escribió la **descripción del evento** en el log. Esto no implica ausencia de alertas: aparecen al consultar el log completo o al filtrar por contenedor.

## Evidencia para el informe

| Captura local | Contenido verificable |
| --- | --- |
| `16-ubuntu-compose-smoke.png` | Portal/base saludables y prueba funcional de los tres roles. |
| `17-portal-ubuntu-windows.png` | Portal de la VM accesible desde Windows por `localhost:18080`. |
| `18-falco-modern-bpf-iniciado.png` | Falco carga `syscall` mediante modern BPF. |
| `19-falco-consulta-inicial.png` | Comando de prueba y consulta inicial del log. |
| `20-falco-alerta-portal.png` | Dos alertas reales, hora, comando, contenedor e imagen del portal. |

Las capturas se conservaron localmente y están excluidas de Git. Para RF-04, la captura **20** es la evidencia principal de detección; combínala con **16** y **18** para mostrar que el workload y el monitor funcionaban en la misma VM. La regla alerta por una shell interactiva y no demuestra, por sí sola, bloqueo, prevención, cobertura de todas las técnicas ni correlación en Wazuh.

## Alcance pendiente

La detección corresponde al **portal desplegado en Ubuntu**, no al portal original de Docker Desktop en Windows. Wazuh se probó por separado en Windows; no se ha demostrado ingesta de estas alertas de Falco en Wazuh ni funcionamiento simultáneo de ambos stacks. Tampoco se ha medido el rendimiento conjunto. Mantener esta distinción al presentar el resultado.

## Fuentes

- [Falco: despliegue como contenedor y controladores](https://falco.org/docs/setup/container/).
- [Falco: reglas predeterminadas](https://falco.org/docs/reference/rules/default-rules/).
