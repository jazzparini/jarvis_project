# Guía de Despliegue en VPS (vps-hermes)

Esta guía te muestra los pasos sencillos para clonar y ejecutar **JARVIS** dentro de tu máquina `vps-hermes` en Google Cloud.

---

### Paso 1: Conectarte a tu VPS

Puedes hacerlo mediante el botón **SSH** en la consola de Google Cloud o con tu cliente SSH:

```bash
# O usando gcloud si lo tienes configurado:
# gcloud compute ssh vps-hermes --zone=us-central1-a --project=openclaw-free-vps
```

---

### Paso 2: Clonar o copiar el proyecto en el VPS

```bash
git clone <URL_DE_TU_REPOSITORIO> jarvis-repo
cd jarvis-repo
```

*(O si subes los archivos directamente, sitúate en la carpeta del proyecto).*

---

### Paso 3: Configurar variables (`.env`)

Crea tu archivo `.env` antes del despliegue:

```bash
cp .env.example .env
nano .env
```

Configura los siguientes valores clave:

```env
APP_ENV=production
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_ALLOWED_USER_IDS=tu_telegram_user_id

# Configuración Hermes en localhost
DEFAULT_LLM_PROVIDER=hermes
HERMES_API_BASE_URL=http://localhost:11434/v1
HERMES_MODEL=hermes-3-llama-3.1-8b

# Si también quieres soporte de Gemini como fallback:
GEMINI_API_KEY=tu_gemini_api_key_aqui
```

---

### Paso 4: Ejecutar script de despliegue automático

Ejecuta el script para instalar el entorno, permisos y servicio `systemd`:

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

---

### Paso 5: Gestión y Logs

- **Ver logs en tiempo real:**
  ```bash
  sudo journalctl -u jarvis -f
  ```
- **Reiniciar servicio:**
  ```bash
  sudo systemctl restart jarvis
  ```
- **Ver estado:**
  ```bash
  sudo systemctl status jarvis
  ```
