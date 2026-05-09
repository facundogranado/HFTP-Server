# HFTP Server

Implementación de un servidor de transferencia de archivos basado en un protocolo propio llamado **HFTP (Home-made File Transfer Protocol)**.

El proyecto está desarrollado en **Python 3** utilizando sockets TCP y soporta múltiples clientes concurrentes, transferencia parcial de archivos, modo binario raw, manejo robusto de errores y compatibilidad con la red Tor mediante servicios ocultos `.onion`.

---

# 🚀 Características

- 📡 Servidor TCP concurrente
- 📂 Listado de archivos compartidos
- 📏 Obtención de metadata de archivos
- ✂️ Descarga parcial de archivos
- 🔤 Transferencia en Base64
- 🧱 Transferencia binaria Raw
- ⚠️ Manejo robusto de errores
- 🧵 Soporte para múltiples clientes
- 🧅 Compatibilidad con Tor
- ✅ Testing automatizado

---

# 🧠 ¿Qué es HFTP?

HFTP es un protocolo de transferencia de archivos inspirado en protocolos clásicos como FTP y HTTP.

Características principales:

- Comunicación sobre TCP
- Protocolo textual ASCII
- Delimitadores `\r\n`
- Respuestas mediante códigos numéricos
- Soporte para payloads:
  - Base64
  - Binario Raw

Puerto por defecto:

```txt
19500
```

---

# 📂 Estructura del proyecto

```txt
.
├── server.py
├── connection.py
├── constants.py
├── client.py
├── tests/
├── scripts/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

# ⚙️ Instalación

## 1️⃣ Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd hftp-server
```

---

## 2️⃣ Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

En Windows:

```bash
venv\Scripts\activate
```

---

## 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# 🚀 Ejecución del servidor

Ejecución básica:

```bash
python3 server.py -d shared_files
```

Configuración personalizada:

```bash
python3 server.py -d shared_files -p 19500 -a 0.0.0.0
```

### Opciones disponibles

| Opción | Descripción |
|---|---|
| `-d` | Directorio de archivos compartidos |
| `-p` | Puerto TCP |
| `-a` | Dirección IP de escucha |

---

# 📡 Comandos del protocolo

---

## `help`

Devuelve los comandos disponibles.

### Request

```txt
help\r\n
```

### Response

```txt
0 OK\r\n
get_file_listing\r\n
get_metadata\r\n
get_slice\r\n
quit\r\n
```

---

## `get_file_listing`

Obtiene la lista de archivos disponibles.

### Request

```txt
get_file_listing\r\n
```

### Response

```txt
0 OK\r\n
archivo.txt\r\n
imagen.png\r\n
\r\n
```

---

## `get_metadata`

Obtiene el tamaño del archivo en bytes.

### Request

```txt
get_metadata archivo.txt\r\n
```

### Response

```txt
0 OK\r\n
1024\r\n
```

---

## `get_slice`

Obtiene una porción del archivo codificada en Base64.

### Request

```txt
get_slice archivo.txt 0 10\r\n
```

### Response

```txt
0 OK\r\n
SG9sYSBtdW5kbw==\r\n
```

---

## `get_slice raw`

Obtiene bytes binarios en modo raw.

### Request

```txt
get_slice archivo.txt 0 10 raw\r\n
```

### Response

```txt
0 OK\r\n
Content-Length: 10\r\n
\r\n
<10 bytes binarios>
```

---

## `quit`

Cierra la conexión.

### Request

```txt
quit\r\n
```

### Response

```txt
0 OK\r\n
```

---

# 🔁 Modos de transferencia

## 📄 Modo Base64

- Payload codificado en Base64
- Delimitado mediante `\r\n`
- Simplifica el framing sobre TCP

---

## 🧱 Modo Raw

- Transferencia binaria exacta
- Utiliza `Content-Length`
- Permite enviar cualquier tipo de byte

---

# ❌ Códigos de error

| Código | Significado |
|---|---|
| `0` | Operación exitosa |
| `100` | Terminador de línea inválido |
| `101` | Request malformado |
| `199` | Error interno del servidor |
| `200` | Comando desconocido |
| `201` | Argumentos inválidos |
| `202` | Archivo inexistente |
| `203` | Offset o tamaño inválido |

---

# 🧵 Concurrencia

El servidor soporta múltiples clientes simultáneamente utilizando:

```python
threading.Thread
```

Cada conexión se maneja de forma independiente.

---

# 🛡️ Consideraciones de seguridad

Protecciones implementadas:

- Prevención de path traversal
- Validación de entradas
- Manejo de requests inválidos
- Acceso seguro a archivos
- Aislamiento entre conexiones

---

# 🧪 Testing

Ejecutar todos los tests:

```bash
pytest -v
```

Ejecutar tests del protocolo:

```bash
python3 server-test.py
```

Ejecutar validación completa:

```bash
python3 grade.py
```

---

# 🧅 Ejecución sobre Tor

HFTP puede ejecutarse de forma transparente sobre la red Tor utilizando servicios ocultos.

Ejemplo de ejecución del cliente:

```bash
torsocks python3 client.py
```

Esto permite:

- Acceso anónimo
- Direcciones `.onion`
- Comunicación TCP extremo a extremo sin modificar el protocolo

---

# 📖 Tecnologías utilizadas

- Python 3
- Sockets TCP
- Threads
- Base64
- Pytest
- Ruff
- Tor

---

# 📌 Ejemplo de ejecución

Log del servidor:

```txt
Serving shared_files on 0.0.0.0:19500
Connection from ('127.0.0.1', 53321)
Request: help
Request: get_file_listing
Request: get_metadata archivo.txt
Request: get_slice archivo.txt 0 128
Closing connection...
```

---

# 📄 Licencia

Proyecto desarrollado con fines educativos y experimentales.
