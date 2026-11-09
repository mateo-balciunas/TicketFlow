# Guía de Aprendizaje FastAPI: de cero a profesional

## Proyecto práctico: **TicketFlow**
### API asíncrona de reservas de entradas para eventos con control de aforo

> Metodología: aprendizaje basado en proyectos (Project-Based Learning) con tutoría socrática.
> Duración: 4 semanas / 4 hitos.

---

## Índice

1. [El proyecto](#1-el-proyecto)
2. [Stack tecnológico](#2-stack-tecnológico)
3. [Modelo de dominio](#3-modelo-de-dominio)
4. [Arquitectura y estructura de carpetas](#4-arquitectura-y-estructura-de-carpetas)
5. [Mapa de endpoints](#5-mapa-de-endpoints)
6. [Semana 1: Fundamentos, tipado, Pydantic v2 y DI](#semana-1-fundamentos-tipado-pydantic-v2-e-inyección-de-dependencias)
7. [Semana 2: Persistencia asíncrona y Alembic](#semana-2-persistencia-asíncrona-con-postgresql-sqlalchemy-20-y-alembic)
8. [Semana 3: Seguridad, JWT y roles](#semana-3-seguridad-autenticación-jwt-y-roles)
9. [Semana 4: Testing, Docker y producción](#semana-4-testing-asíncrono-docker-y-preparación-para-producción)
10. [Reglas de tutoría socrática](#10-reglas-de-tutoría-socrática)
11. [Estándares de ingeniería exigidos](#11-estándares-de-ingeniería-exigidos)
12. [Primer paso](#12-primer-paso-semana-1-tarea-1)
13. [Recursos de referencia](#13-recursos-de-referencia)
14. [Registro de progreso](#14-registro-de-progreso)

---

## 1. El proyecto

**El caso de uso:** organizadores publican eventos con varios tipos de entrada (General, VIP…), cada uno con un aforo limitado. Los asistentes **reservan** entradas, la reserva queda **retenida 10 minutos** mientras "pagan" (pago simulado) y, si no confirman, expira y las plazas vuelven al stock. Al confirmar, se emiten las entradas y se envía una notificación en segundo plano.

**Por qué va más allá de un CRUD:** el problema central es la **concurrencia**. Si quedan 3 entradas VIP y 50 personas pulsan "reservar" a la vez, el sistema no puede vender 4. Es el mismo problema que resuelven Ticketmaster o las aerolíneas, y obliga a pensar en:

- Transacciones y bloqueos de base de datos.
- Máquinas de estados con transiciones válidas e inválidas.
- Tiempos de expiración y liberación de recursos.
- Autorización basada en roles **y** en propiedad de los recursos.
- Tareas en segundo plano (notificaciones).

---

## 2. Stack tecnológico

| Área | Herramienta |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework | FastAPI |
| Validación y schemas | Pydantic v2 + pydantic-settings |
| Servidor ASGI | Uvicorn (Gunicorn como gestor de procesos en producción) |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy 2.0 (async) + asyncpg |
| Migraciones | Alembic (plantilla async) |
| Hashing de contraseñas | pwdlib con Argon2 |
| Tokens | PyJWT |
| Testing | pytest + pytest-asyncio (o anyio) + httpx `AsyncClient` + pytest-cov |
| Calidad de código | ruff (lint + formato) + mypy `--strict` |
| Gestión de dependencias | uv (o Poetry) |
| Contenedores | Docker (multi-stage) + Docker Compose |
| CI (bonus) | GitHub Actions |

---

## 3. Modelo de dominio

| Entidad | Responsabilidad |
|---|---|
| `User` | Credenciales y rol: `attendee`, `organizer`, `admin` |
| `Event` | Título, descripción, fecha, lugar, organizador, estado (`draft` / `published` / `cancelled`) |
| `TicketTier` | Tipo de entrada de un evento: nombre, precio, aforo total, plazas disponibles |
| `Reservation` | Usuario, tier, cantidad, estado y `expires_at` |
| `Ticket` | Entrada emitida con código único, ligada a una reserva confirmada |

### Máquina de estados de `Reservation`

```
            confirm (antes de expires_at)
pending ─────────────────────────────────► confirmed
   │
   ├── expires_at superado ──────────────► expired     (plazas devueltas al stock)
   │
   └── cancel (por el usuario) ──────────► cancelled   (plazas devueltas al stock)
```

Cualquier otra transición (por ejemplo, confirmar una reserva `expired`) es **inválida** y debe responder `409 Conflict`.

### Relaciones

- Un `User` (organizer) tiene muchos `Event`.
- Un `Event` tiene muchos `TicketTier`.
- Un `TicketTier` tiene muchas `Reservation`.
- Un `User` (attendee) tiene muchas `Reservation`.
- Una `Reservation` confirmada tiene uno o varios `Ticket`.

---

## 4. Arquitectura y estructura de carpetas

Arquitectura por capas desde la semana 1. Cada capa solo conoce a la de abajo:

```
Router (HTTP)  →  Service (reglas de negocio)  →  Repository (acceso a datos)  →  BD
```

- **Routers:** reciben la petición, validan con Pydantic, llaman al servicio y devuelven el `response_model`. Sin lógica de negocio.
- **Services:** reglas del dominio. No saben nada de HTTP (no lanzan `HTTPException`, lanzan excepciones de dominio).
- **Repositories:** consultas y persistencia. Intercambiables gracias a la inyección de dependencias.

```
ticketflow/
├── app/
│   ├── __init__.py
│   ├── main.py            # creación de la app, lifespan, registro de routers y handlers
│   ├── core/
│   │   ├── config.py      # Settings (pydantic-settings)
│   │   ├── security.py    # hashing y JWT (semana 3)
│   │   └── exceptions.py  # excepciones de dominio y handlers
│   ├── api/
│   │   └── v1/            # un router por recurso
│   ├── schemas/           # modelos Pydantic (Create / Update / Read)
│   ├── models/            # modelos ORM (semana 2)
│   ├── services/          # lógica de negocio
│   ├── repositories/      # acceso a datos
│   └── dependencies.py    # dependencias reutilizables (Annotated + Depends)
├── alembic/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── .env.example
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 5. Mapa de endpoints

| Método | Ruta | Rol | Semana |
|---|---|---|---|
| GET | `/health` | Público | 1 |
| GET | `/api/v1/events` | Público (solo `published`) | 1 |
| GET | `/api/v1/events/{event_id}` | Público | 1 |
| POST | `/api/v1/events` | organizer | 1 (rol en 3) |
| PATCH | `/api/v1/events/{event_id}` | organizer propietario | 1 (rol en 3) |
| DELETE | `/api/v1/events/{event_id}` | organizer propietario / admin | 1 (rol en 3) |
| POST | `/api/v1/events/{event_id}/tiers` | organizer propietario | 1 (rol en 3) |
| GET | `/api/v1/events/{event_id}/tiers` | Público | 1 |
| POST | `/api/v1/reservations` | attendee | 2 |
| POST | `/api/v1/reservations/{id}/confirm` | attendee propietario | 2 |
| POST | `/api/v1/reservations/{id}/cancel` | attendee propietario | 2 |
| GET | `/api/v1/events/{event_id}/reservations` | organizer propietario | 3 |
| POST | `/api/v1/auth/register` | Público | 3 |
| POST | `/api/v1/auth/login` | Público | 3 |
| POST | `/api/v1/auth/refresh` | Público (con refresh token) | 3 |
| GET | `/api/v1/me` | Autenticado | 3 |
| GET | `/api/v1/me/tickets` | Autenticado | 3 |
| PATCH | `/api/v1/users/{user_id}/role` | admin | 3 |
| WS | `/ws/tiers/{tier_id}` | Público | 4 (bonus) |

---

## Semana 1: Fundamentos, tipado, Pydantic v2 e inyección de dependencias

**Objetivo:** la API funciona con persistencia **en memoria**, pero con contratos, validación y arquitectura ya profesionales.

### Conceptos clave

- **Type hints modernos (3.11+):** `list[int]`, `X | None`, `Annotated`, `Literal`, `StrEnum`, y por qué FastAPI los usa en tiempo de ejecución (no solo para el editor).
- **ASGI y async:** qué es un event loop, cuándo usar `async def` frente a `def` en un endpoint y qué pasa si bloqueas el loop.
- **Pydantic v2:** `BaseModel`, `Field` con restricciones (`gt`, `max_length`…), `field_validator` y `model_validator`, `model_config = ConfigDict(...)`, `model_dump()` / `model_validate()`.
- **Separación de schemas:** `EventCreate`, `EventUpdate`, `EventRead`. Por qué el modelo de entrada no debe ser el de salida.
- **Parámetros:** path, query y body; `status_code`; `response_model`; paginación básica.
- **Inyección de dependencias:** `Depends` combinado con `Annotated` (`RepoDep = Annotated[EventRepository, Depends(get_event_repository)]`), dependencias encadenadas y dependencias con `yield`.
- **Errores:** `HTTPException` frente a excepciones de dominio propias (`EventNotFoundError`) traducidas con `exception_handler`.
- **Configuración:** `pydantic-settings` y variables de entorno desde el día uno.

### Tarea práctica

1. Inicializa el proyecto con `uv` (o Poetry), con `ruff` y `mypy --strict` configurados en `pyproject.toml`.
2. Implementa el CRUD de `Event` y `TicketTier` usando un **repositorio en memoria** inyectado con `Depends`.
3. Reglas de validación de negocio:
   - La fecha del evento debe ser futura.
   - `price >= 0` usando `Decimal` (nunca `float` para dinero).
   - Un evento no puede tener dos tiers con el mismo nombre.
   - `available_seats` nunca puede superar `capacity`.
4. Endpoint `GET /events` con filtros opcionales (`status`, `from_date`) y paginación `limit` / `offset` validada.
5. Excepciones de dominio con un handler global que devuelva un JSON de error con formato uniforme.

### Definition of Done

- [ ] `mypy --strict` y `ruff check` pasan sin errores ni `# type: ignore` injustificados.
- [ ] Ningún endpoint devuelve dicts sueltos: todo sale por un `response_model`.
- [ ] Los routers **no contienen lógica de negocio**: delegan en `services/`.
- [ ] Cambiar el repositorio en memoria por otro solo requiere tocar **una** dependencia.
- [ ] `/docs` muestra ejemplos, códigos de respuesta (201, 404, 422…) y descripciones correctos.
- [ ] Sabes explicar con tus palabras la diferencia entre un error 422 y uno 400 en tu API.

---

## Semana 2: Persistencia asíncrona con PostgreSQL, SQLAlchemy 2.0 y Alembic

**Objetivo:** sustituir la memoria por PostgreSQL y resolver el problema de la sobreventa.

### Conceptos clave

- **SQLAlchemy 2.0 async:** `create_async_engine`, `async_sessionmaker`, `AsyncSession`, el driver `asyncpg`, y el estilo declarativo tipado con `Mapped[...]` y `mapped_column`.
- **Ciclo de vida de la sesión:** una sesión por petición mediante una dependencia con `yield`, y commit/rollback explícitos.
- **Relaciones y carga:** `relationship`, el problema N+1 y `selectinload` / `joinedload`. Por qué el *lazy loading* implícito falla en async.
- **Puente ORM ↔ Pydantic:** `ConfigDict(from_attributes=True)`.
- **Transacciones y concurrencia:** niveles de aislamiento, `SELECT ... FOR UPDATE` (`with_for_update()`), *optimistic locking* frente a *pessimistic locking*, y constraints de BD (`CHECK available_seats >= 0`) como última línea de defensa.
- **Alembic:** plantilla async (`alembic init -t async`), autogenerate y sus limitaciones, migraciones reversibles (`downgrade`).
- **Índices:** por qué `expires_at` y `status` los necesitan.

### Tarea práctica

1. `docker-compose.yml` mínimo **solo con PostgreSQL** (la API aún corre en local).
2. Modelos ORM de las 5 entidades con sus constraints (`UNIQUE`, `CHECK`, FKs con un `ondelete` pensado).
3. Primera migración con Alembic y, después, una segunda migración que añada un campo nuevo, para practicar la evolución del esquema.
4. Reimplementa los repositorios con SQLAlchemy **sin tocar los routers** (aquí se verá si la semana 1 quedó bien diseñada).
5. **Flujo de reserva:**
   - `POST /reservations`: bloquea el tier, comprueba stock, descuenta plazas y crea la reserva `pending` con `expires_at = now + 10 min`, todo en **una transacción**.
   - `POST /reservations/{id}/confirm`: pago simulado, pasa a `confirmed` y emite los `Ticket` con código único.
   - `POST /reservations/{id}/cancel`: pasa a `cancelled` y devuelve las plazas.
   - Liberación de reservas expiradas: una tarea periódica con `lifespan` + `asyncio`, o una liberación perezosa al consultar. Tendrás que decidir cuál y justificarlo.
6. Script que lance 50 reservas concurrentes contra un tier con 5 plazas y demuestre que se venden **exactamente** 5.

### Definition of Done

- [ ] `alembic upgrade head` y `alembic downgrade base` funcionan sobre una BD vacía.
- [ ] Cero consultas N+1 en los listados (verificado con `echo=True` en el engine).
- [ ] El test de concurrencia da siempre 5 reservas, nunca 6.
- [ ] Las transiciones de estado inválidas (confirmar una reserva expirada) devuelven 409 con un mensaje claro.
- [ ] La cadena de conexión viene de `Settings`, nunca hardcodeada.

---

## Semana 3: Seguridad, autenticación JWT y roles

**Objetivo:** que solo quien debe pueda hacer cada cosa, y que sea demostrable.

### Conceptos clave

- **Hashing de contraseñas:** por qué no basta con SHA-256, qué son la sal y el *work factor*, y Argon2 frente a bcrypt. Se usará `pwdlib` con Argon2 (la documentación actual de FastAPI lo recomienda frente a `passlib`, que ya no se mantiene).
- **JWT:** estructura (header.payload.signature), claims (`sub`, `exp`, `iat`, `jti`), firmado no es lo mismo que cifrado, y `PyJWT`.
- **Flujo OAuth2 Password** con `OAuth2PasswordBearer` y `OAuth2PasswordRequestForm`.
- **Access tokens frente a refresh tokens:** caducidades, rotación y revocación.
- **Autorización:** RBAC con dependencias (`require_role("organizer")`) y **ownership** (un organizador solo edita *sus* eventos).
- **401 frente a 403:** cuándo usar cada uno y por qué un 404 puede ser más seguro que un 403.
- **Superficie de ataque:** enumeración de usuarios, *timing attacks*, mass assignment (por qué `UserCreate` no debe aceptar `role`), CORS y rate limiting conceptual.

### Tarea práctica

1. `POST /auth/register`, `POST /auth/login` y `POST /auth/refresh`.
2. Dependencia `get_current_user` y dependencias de rol componibles.
3. Matriz de permisos:

   | Acción | attendee | organizer | admin |
   |---|---|---|---|
   | Ver eventos publicados | ✅ | ✅ | ✅ |
   | Reservar entradas | ✅ | ❌ | ✅ |
   | Ver sus propias reservas | ✅ | ✅ | ✅ |
   | Crear eventos y tiers | ❌ | ✅ | ✅ |
   | Editar/borrar eventos | ❌ | Solo los suyos | ✅ |
   | Ver reservas de un evento | ❌ | Solo los suyos | ✅ |
   | Cambiar roles | ❌ | ❌ | ✅ |

4. Endpoint `GET /me/tickets`.
5. Notificación de confirmación con `BackgroundTasks` (un email simulado que se registra en el log), entendiendo sus límites frente a una cola real (Celery, ARQ, RQ…).

### Definition of Done

- [ ] Ninguna contraseña en claro en la BD, los logs ni las respuestas.
- [ ] La clave JWT y las caducidades salen de `Settings`, y el algoritmo está fijado explícitamente al decodificar.
- [ ] Un usuario no puede escalar privilegios ni enviando `role` en el registro ni manipulando el token.
- [ ] Un organizador recibe un error al intentar editar un evento ajeno (y sabes justificar si es 403 o 404).
- [ ] Un token caducado o mal firmado devuelve 401 con la cabecera `WWW-Authenticate`.

---

## Semana 4: Testing asíncrono, Docker y preparación para producción

**Objetivo:** que el proyecto sea demostrable, reproducible y desplegable.

### Conceptos clave

- **Pytest async:** `pytest-asyncio` o `anyio`, fixtures con distintos *scopes* y `conftest.py`.
- **Cliente de test:** `httpx.AsyncClient` con `ASGITransport(app=app)`.
- **Aislamiento de BD en tests:** BD de test dedicada y transacción con rollback por test, frente a recrear tablas.
- **`app.dependency_overrides`:** cómo la inyección de la semana 1 hace testeable todo.
- **Pirámide de tests:** unitarios (servicios), de integración (repositorios + BD) y end-to-end (HTTP). Cobertura con `pytest-cov`, y por qué el 100 % no es el objetivo.
- **Docker:** build multi-stage, imagen slim, usuario no-root, `.dockerignore` y caché de capas.
- **Compose:** `api` + `db`, `healthcheck` y `depends_on: condition: service_healthy`, volúmenes y migraciones al arrancar.
- **Producción:** Uvicorn/Gunicorn y número de workers, logging estructurado, endpoint `/health`, `lifespan` para recursos, y secretos fuera de la imagen.

### Tarea práctica

1. Suite de tests que cubra como mínimo:
   - Unitarios de las reglas de dominio (transiciones de estado de `Reservation`).
   - Integración del flujo completo: registro → login → reserva → confirmación → entradas emitidas.
   - Seguridad: matriz de permisos (parametrizada con `@pytest.mark.parametrize`).
   - El test de concurrencia de la semana 2, convertido en test automatizado.
2. `Dockerfile` multi-stage y `docker-compose.yml` con `api`, `db` y una `db_test` opcional.
3. `GET /health` que compruebe la conexión a la BD.
4. `README.md` con la arquitectura, cómo levantar el proyecto en un comando y las decisiones de diseño.
5. *(Bonus)* Pipeline de GitHub Actions con lint, tipos, tests y build de la imagen.
6. *(Bonus avanzado)* WebSocket que emita en tiempo real el stock restante de un tier.

### Definition of Done

- [ ] `docker compose up` levanta el sistema completo desde cero, migraciones incluidas.
- [ ] `pytest` pasa de forma determinista (lanzado 5 veces, 5 veces en verde) y cada test es independiente del orden.
- [ ] Cobertura ≥ 85 % en `services/`, con los caminos de error cubiertos, no solo los felices.
- [ ] La imagen corre como usuario no-root y no contiene secretos ni `.env`.
- [ ] Puedes explicar en 5 minutos, como en una entrevista, cómo evita tu sistema la sobreventa.

---

## 10. Reglas de tutoría socrática

1. **Método socrático:** el tutor no genera archivos completos de código. Explica la teoría de forma breve, con analogías del mundo real, y da instrucciones concretas de qué codificar (nombres de archivos, firmas, comportamiento esperado). Como mucho, fragmentos mínimos de sintaxis cuando algo sea nuevo y no se pueda deducir.
2. **Control manual:** el alumno escribe el código a mano en su editor. Al compartir su implementación, el tutor la analiza, señala **2 o 3 puntos de mejora** priorizados por impacto y hace **preguntas sobre las decisiones de diseño** en lugar de dar la solución.
3. **Errores bloqueantes:** si hay un fallo grave de seguridad, concurrencia o tipado, se marca como **bloqueante** y se resuelve antes de avanzar.
4. **Avance por hitos:** no se pasa a la siguiente semana hasta cumplir su Definition of Done.

---

## 11. Estándares de ingeniería exigidos

- **Tipado estricto:** todas las funciones con anotaciones de parámetros y retorno; `mypy --strict` en verde.
- **Pydantic v2 idiomático:** `ConfigDict`, `field_validator` / `model_validator`, `model_dump()` / `model_validate()`; nada de API de v1 (`class Config`, `.dict()`, `@validator`, `orm_mode`).
- **Manejo explícito de errores:** excepciones de dominio en los servicios, traducidas a `HTTPException` o mediante handlers globales; nunca un `except Exception: pass`.
- **Código limpio:** funciones pequeñas, nombres descriptivos, sin lógica de negocio en los routers, sin valores mágicos (todo configurable va a `Settings`).
- **Dinero con `Decimal`**, fechas con zona horaria (`datetime` *aware* en UTC).

---

## 12. Primer paso: Semana 1, tarea 1

**Analogía:** antes de cocinar en un restaurante profesional se hace el *mise en place*: cada utensilio en su sitio y cada ingrediente medido. `pyproject.toml`, `ruff` y `mypy --strict` son tu mise en place. Configurarlos después de tener 2.000 líneas es como ordenar la cocina en mitad del servicio.

**Qué hay que hacer:**

1. Crea el proyecto con `uv init ticketflow` y añade `fastapi`, `uvicorn[standard]` y `pydantic-settings` como dependencias, más `ruff` y `mypy` como dependencias de desarrollo.
2. En `pyproject.toml`, configura `mypy` en modo `strict` y `ruff` con al menos las reglas `E`, `F`, `I`, `UP`, `B` y `ANN`.
3. Crea la estructura de carpetas de la sección 4 (con `__init__.py` vacíos).
4. En `app/core/config.py`, define una clase `Settings` con `app_name: str`, `debug: bool` y `api_v1_prefix: str`, leída de un `.env`.
5. En `app/main.py`, crea la app y un endpoint `GET /health` que devuelva un modelo Pydantic `HealthResponse` (no un dict) con el estado y el nombre de la app sacado de `Settings`.

**Entrega para revisión:** `pyproject.toml`, `config.py` y `main.py`.

**Pregunta para reflexionar antes de escribir `Settings`:**
¿Deberías instanciar `Settings()` una sola vez a nivel de módulo, o exponerla mediante una función con `Depends`? ¿Qué implica cada opción cuando lleguemos a los tests de la semana 4?

---

## 13. Recursos de referencia

- Documentación oficial de FastAPI: https://fastapi.tiangolo.com
- Documentación de Pydantic v2: https://docs.pydantic.dev
- SQLAlchemy 2.0 (ORM y asyncio): https://docs.sqlalchemy.org
- Alembic: https://alembic.sqlalchemy.org
- pytest: https://docs.pytest.org
- HTTPX: https://www.python-httpx.org
- Docker Compose: https://docs.docker.com/compose/

---

## 14. Registro de progreso

| Semana | Inicio | Fin | DoD cumplido | Notas / aprendizajes |
|---|---|---|---|---|
| 1. Fundamentos | | | ☐ | |
| 2. Persistencia | | | ☐ | |
| 3. Seguridad | | | ☐ | |
| 4. Testing y Docker | | | ☐ | |
