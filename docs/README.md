# Guía del repositorio CWPP UTS

Este repositorio contiene un piloto con datos ficticios. La **VM Ubuntu** reúne portal, PostgreSQL, Falco y Wazuh manager. Las pruebas de **Windows** son una línea histórica separada. El documento para integrar al informe grupal es [informe-integrante-2.md](informe-integrante-2.md); su copia editable está en `entregables/informe-integrante-2.docx`.

| Necesidad | Archivo de entrada |
| --- | --- |
| Reproducir el piloto en una VM nueva | [guia-reproduccion.md](guia-reproduccion.md) |
| Entender los dos entornos y diagramas | [arquitectura-actual.md](arquitectura-actual.md) |
| Seleccionar y analizar capturas | [guia-analisis-evidencias.md](guia-analisis-evidencias.md) |
| Ver el front renovado antes de actualizar la VM | [Inicio](evidencias/prototipo-inicio-nuevo.png) y [acceso](evidencias/prototipo-ingreso-nuevo.png), previsualizaciones aisladas |
| Integrar la contribución del integrante 2 | [informe-integrante-2.md](informe-integrante-2.md) y [entrega-integrante-2.md](entrega-integrante-2.md) |
| Consultar resultados depurados | `evidencias/*.json`, `evidencias/*.md` |
| Revisar el despliegue | [deploy/ubuntu/README.md](../deploy/ubuntu/README.md) |

## Estructura

```text
app/backend/           Portal Flask, plantillas y estilos; Dockerfile para reconstruirlo
ubuntu.compose.yaml    Compose base de Ubuntu para un clon Git limpio
database/init/         Esquema y datos académicos ficticios
deploy/ubuntu/         Compose base, Falco y Wazuh manager; reglas y configuración
docs/                  Informe, diagramas, fases, guías y resultados depurados
docs/evidencias/       JSON y PNG de diagramas aptos para compartir
docs/evidencias/capturas/  Capturas originales locales, excluidas de Git
scripts/               Preparación, empaquetado y verificadores
security/wazuh/        Prueba histórica de Wazuh en Windows
dist/                  ZIP generado localmente, excluido de Git
```

La fuente principal es el repositorio. El ZIP de `dist/` se regenera con `python scripts/paquetizar_ubuntu.py`. Nunca copies `.env`, `credenciales_portal.txt`, certificados ni los logs completos a una entrega. Para comparar resultados, conserva el commit, hora, VM y comando de prueba.
