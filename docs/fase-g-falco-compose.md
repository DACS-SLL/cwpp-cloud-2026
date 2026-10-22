# Fase G: Falco reproducible con Compose en Ubuntu

Fecha: 22 de octubre de 2026 (UTC). Esta fase usa el portal y PostgreSQL en la misma VM Ubuntu VirtualBox donde Falco observa los eventos del kernel.

## Cambio aplicado

Se añadió `deploy/ubuntu/falco.compose.yaml` con Falco 0.45.0, los montajes del host requeridos para modern BPF y metadatos de Docker, reinicio automático y rotación de logs de Docker. El sensor necesita privilegios elevados; las restricciones del contenedor `uts-portal` no se atribuyen a Falco. El archivo también entra en el ZIP portátil generado por `scripts/paquetizar_ubuntu.py`.

En la VM, `README.md` tenía cambios locales, por lo que `git pull --ff-only` se detuvo. Se conservó ese archivo y se extrajo únicamente la configuración nueva desde `origin/main`. Antes de cambiar el contenedor Falco manual, se guardó su log en `~/falco-previo.log`. El contenedor manual se eliminó automáticamente al detenerse porque había sido iniciado con `--rm`; después Compose inició `uts-falco`.

`sudo docker compose -f compose.yaml -f falco.compose.yaml ps -a` mostró `uts-database` y `uts-portal` saludables, y `uts-falco` en ejecución. El portal siguió respondiendo desde Windows en `http://127.0.0.1:18080/health` con `status: ok` y `database: connected` tras el cambio.

## Detección repetida

Desde SSH se ejecutó:

```bash
sudo docker exec -it uts-portal sh -c 'echo prueba-falco-compose'
sudo docker logs --since=2m uts-falco 2>&1 | grep -F 'prueba-falco-compose'
```

A las **00:51:23 UTC**, Falco generó una alerta `Notice` con la descripción `A shell was spawned in a container with an attached terminal`, `evt_type=execve`, `command=sh -c echo prueba-falco-compose`, `container_name=uts-portal` e imagen `d4c5g/uts-cwpp-portal:2026-10-21`. Esta segunda prueba confirma detección después de pasar Falco a Compose. Los campos depurados están en [falco-compose-verificacion.json](evidencias/falco-compose-verificacion.json).

## Recursos: una muestra

| Contenedor | CPU instantánea | Memoria instantánea |
| --- | ---: | ---: |
| `uts-database` | 0,00 % | 26,75 MiB |
| `uts-portal` | 0,02 % | 45,19 MiB |
| `uts-falco` | 3,23 % | 41,06 MiB |

`free -h` dentro de la VM mostró aproximadamente 2,4 GiB de memoria **disponible** en ese momento. Los valores proceden de un solo `docker stats --no-stream` y no son promedios ni permiten calcular el costo total de Wazuh y Falco juntos. Tampoco se comparó la latencia del portal en condiciones equivalentes antes y después de Falco.

## Capturas para el informe

1. `21-falco-compose-reproducible.png`: terminal Ubuntu con `sudo docker compose -f compose.yaml -f falco.compose.yaml ps -a`; debe verse `uts-falco` en ejecución y portal/base saludables.
2. `22-falco-compose-alerta.png`: terminal Ubuntu con la línea de alerta que contiene `prueba-falco-compose`, hora, contenedor e imagen.
3. `23-consumo-ubuntu-falco.png`: terminal Ubuntu con `docker stats --no-stream` para los tres contenedores y `free -h`. Rotularla como muestra puntual.

Guarda las capturas en `docs/evidencias/capturas/` en Windows; esa carpeta se excluye de Git. La salida de `~/falco-previo.log` puede contener rutas y comandos del host y no se publica. Las capturas originales de la fase F siguen siendo evidencia de la primera detección manual.

## Alcance

Esta fase valida el despliegue reproducible y la alerta del portal **de Ubuntu**. Wazuh se probó por separado en Docker Desktop de Windows; todavía no existe una ruta verificada que entregue las alertas de Falco a Wazuh. El dashboard de Wazuh tampoco se ha validado con los tres componentes activos por la presión de memoria descrita en [fase D](fase-d-wazuh.md).

## Fuente

- [Falco: despliegue oficial como contenedor](https://falco.org/docs/setup/container/).
