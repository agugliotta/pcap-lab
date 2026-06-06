# Contexto del Proyecto: PCAP Lab Generator

Este proyecto es un generador de tráfico HTTP determinista para laboratorios de ciberseguridad.

## Estado Actual
- **Estructura:** Generador modular en Python con ataques (SQLi, XSS, IDOR, CSRF), capturador con `tcpdump` y servidor dummy integrado.
- **Funcionalidad:** Genera PCAPs y un `answer_key.json` basado en un `STUDENT_ID` (seed).
- **Scripts:** `scripts/generate.sh` (captura) y `scripts/replay.sh` (tcpreplay).
- **Pruebas:** Cobertura para generación de semillas, estructura de ataques y lógica de tráfico (9 tests pasando).

## Comandos Rápidos
- `make install`: Instalar dependencias (`requests`, `pytest`).
- `make generate STUDENT=nombre`: Generar tráfico para un estudiante (requiere sudo).
- `make test`: Correr la suite de pruebas.
- `make replay FILE=ruta/al/pcap INTERFACE=eth0`: Replay de tráfico contra un WAF.

## Próximos Pasos Posibles
- Añadir más tipos de ataques (LFI, RCE, etc.).
- Mejorar la aleatoriedad controlada del tráfico normal.
- Implementar validación automática de reglas de ModSecurity.
