from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import dotenv_values
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError


class MongoConnection:
    """Repositorio MongoDB para las colecciones operativas de LogiSmart."""

    COLECCIONES = (
        "camiones",
        "accesos",
        "incidentes",
        "riesgos_eticos",
        "evaluaciones_llm",
    )

    def __init__(self, archivo_env=None):
        carpeta = Path(__file__).resolve().parent
        env_path = Path(archivo_env) if archivo_env else carpeta / ".env"
        if not env_path.is_file() and archivo_env is None:
            env_path = carpeta.parent / ".env"
        configuracion = dotenv_values(env_path)

        self.user = configuracion.get("Mongo_User")
        self.password = configuracion.get("Mongo_Password")
        self.cluster = configuracion.get("Mongo_Cluster")
        self.nombre_bd = configuracion.get("Mongo_Db") or "LogiSmart"
        self.nombre_coleccion = configuracion.get("Mongo_Collection") or "data"
        self.uri = None
        if self.user and self.password and self.cluster:
            self.uri = (
                f"mongodb+srv://{quote_plus(self.user)}:{quote_plus(self.password)}"
                f"@{self.cluster}/?retryWrites=true&w=majority&appName=LogiSmart"
            )
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000) if self.uri else None
        self.db = self.client[self.nombre_bd] if self.client else None
        self.collection = self.get_collection() if self.db is not None else None
        self.cliente = self.client
        self.bd = self.db
        self.error = ""

    def get_collection(self, collection=None):
        if self.db is None:
            raise ConnectionError("Configura MongoDB en el archivo .env.")
        return self.db[collection or self.nombre_coleccion]

    @property
    def conectado(self):
        return self.client is not None and self.db is not None

    def verificar_conexion(self):
        if not self.conectado:
            self.error = "Configura MongoDB en el archivo .env."
            return False
        try:
            self.client.admin.command("ping")
            self.error = ""
            return True
        except (PyMongoError, OSError) as exc:
            self.error = self._mensaje_error(exc)
            return False

    def _coleccion(self, nombre):
        if nombre not in self.COLECCIONES:
            raise ValueError("Colección no permitida.")
        if not self.conectado:
            raise ConnectionError(self.error or "MongoDB no está configurado.")
        return self.get_collection(nombre)

    @staticmethod
    def _mensaje_error(error):
        detalle = str(error).lower()
        if "ssl handshake failed" in detalle or "tlsv1_alert_internal_error" in detalle:
            return "Los nodos responden por TCP, pero falla el handshake TLS. Revisa Network Access/IP allowlist y posibles proxies; no desactives la validación TLS."
        if isinstance(error, ServerSelectionTimeoutError):
            return "Timeout al contactar MongoDB. Revisa red saliente, URI y Network Access / IP allowlist de Atlas."
        return f"MongoDB: {error.__class__.__name__}: {error}"

    @staticmethod
    def _normalizar(documento):
        if documento is None:
            return None
        documento = dict(documento)
        if "_id" in documento:
            documento["_id"] = str(documento["_id"])
        return documento

    def insertar(self, coleccion, documento):
        documento = dict(documento)
        if coleccion == "camiones":
            documento.pop("_id", None)
            documento.pop("camion_id", None)
        documento.setdefault("creado_en", datetime.now(timezone.utc))
        return str(self._coleccion(coleccion).insert_one(documento).inserted_id)

    def listar(self, coleccion, filtro=None, limite=200):
        cursor = self._coleccion(coleccion).find(filtro or {}).sort("creado_en", -1).limit(limite)
        return [self._normalizar(item) for item in cursor]

    def buscar_uno(self, coleccion, filtro):
        return self._normalizar(self._coleccion(coleccion).find_one(filtro))

    def actualizar(self, coleccion, identificador, cambios):
        from bson import ObjectId

        filtro = {"_id": ObjectId(identificador)} if ObjectId.is_valid(identificador) else {"placa": identificador}
        cambios = dict(cambios)
        cambios.pop("_id", None)
        if coleccion == "camiones":
            cambios.pop("camion_id", None)
            actualizacion = {"$set": cambios, "$unset": {"camion_id": ""}}
        else:
            actualizacion = {"$set": cambios}
        resultado = self._coleccion(coleccion).update_one(filtro, actualizacion)
        return resultado.modified_count > 0 or resultado.matched_count > 0

    def reemplazar(self, coleccion, identificador, documento):
        from bson import ObjectId

        filtro = {"_id": ObjectId(identificador)} if ObjectId.is_valid(identificador) else {"placa": identificador}
        documento = dict(documento)
        documento.pop("_id", None)
        if coleccion == "camiones":
            documento.pop("camion_id", None)
        resultado = self._coleccion(coleccion).replace_one(filtro, documento)
        return resultado.modified_count > 0 or resultado.matched_count > 0

    def eliminar(self, coleccion, identificador):
        from bson import ObjectId

        filtro = {"_id": ObjectId(identificador)} if ObjectId.is_valid(identificador) else {"placa": identificador}
        return self._coleccion(coleccion).delete_one(filtro).deleted_count > 0

    def contar(self, coleccion, filtro=None):
        return self._coleccion(coleccion).count_documents(filtro or {})

    def incidentes_por_categoria_semana(self):
        return list(self._coleccion("incidentes").aggregate([
            {"$group": {
                "_id": {
                    "categoria": {"$ifNull": ["$clasificacion.categoria", "Sin categoría"]},
                    "anio": {"$isoWeekYear": "$creado_en"},
                    "semana": {"$isoWeek": "$creado_en"},
                },
                "total": {"$sum": 1},
            }},
            {"$sort": {"_id.anio": -1, "_id.semana": -1}},
            {"$limit": 100},
        ]))

    def resumen(self, desde=None, hasta=None, umbral_critico=15):
        intervalo = {}
        if desde or hasta:
            intervalo["creado_en"] = {}
            if desde:
                intervalo["creado_en"]["$gte"] = desde
            if hasta:
                intervalo["creado_en"]["$lt"] = hasta
        return {
            "camiones_atendidos": self.contar("accesos", intervalo),
            "incidentes_abiertos": self.contar("incidentes", {"estado": {"$ne": "cerrado"}, **intervalo}),
            "riesgos_criticos": self.contar("riesgos_eticos", {"puntaje_residual": {"$gte": umbral_critico}, **intervalo}),
        }

    def recuperar_camiones_verificados(self, limite=100):
        """Trae camiones cuya última regla guardada autoriza el acceso estándar."""
        from bson import ObjectId

        accesos = self.listar("accesos", {"A": True, "decision_final": True}, limite)
        documentos = []
        for acceso in accesos:
            camion_id = acceso.get("camion_id")
            camion = None
            if isinstance(camion_id, ObjectId):
                camion = self.buscar_uno("camiones", {"_id": camion_id})
            if camion is None and acceso.get("placa"):
                camion = self.buscar_uno("camiones", {"placa": acceso["placa"]})

            acceso["origen"] = "accesos"
            acceso["consulta_especial"] = "camiones_verificados"
            documentos.append(acceso)
            if camion:
                camion["origen"] = "camiones"
                camion["consulta_especial"] = "camiones_verificados"
                documentos.append(camion)
        return documentos

    def recuperar_incidentes(self, pregunta, limite=8):
        import re
        import unicodedata

        texto = "".join(
            letra for letra in unicodedata.normalize("NFD", pregunta.lower())
            if unicodedata.category(letra) != "Mn"
        )
        placa = re.search(r"\bCAM[- ]?\d{2,}\b", pregunta.upper())
        filtro = {}

        if placa:
            filtro["placa"] = placa.group(0).replace(" ", "-")
        if any(palabra in texto for palabra in ("abierto", "abiertos", "pendiente", "pendientes", "nuevo", "nuevos")):
            filtro["estado"] = {"$in": ["nuevo", "en_atencion"]}
        elif any(palabra in texto for palabra in ("cerrado", "cerrados", "resuelto", "resueltos")):
            filtro["estado"] = "cerrado"

        terminos = [
            palabra for palabra in re.findall(r"[\w-]{4,}", texto)
            if palabra not in {"incidente", "incidentes", "accidente", "accidentes", "muestra", "mostrar", "dime", "cuales", "cual", "tengo", "sobre", "abiertos", "abierto", "cerrados", "cerrado", "pendientes", "pendiente", "eso"}
        ]
        if terminos and not placa:
            patron = "|".join(re.escape(palabra) for palabra in terminos[:4])
            filtro["$or"] = [
                {"correo_original": {"$regex": patron, "$options": "i"}},
                {"clasificacion.categoria": {"$regex": patron, "$options": "i"}},
                {"clasificacion.resumen": {"$regex": patron, "$options": "i"}},
            ]

        documentos = self.listar("incidentes", filtro, limite)
        for documento in documentos:
            documento["origen"] = "incidentes"
            documento["consulta_especial"] = "incidentes"
        return documentos

    def recuperar_contexto(self, pregunta, limite=8):
        """Busca primero por entidad o intención; luego busca términos en Mongo."""
        import re
        import unicodedata

        pregunta_normalizada = "".join(
            caracter for caracter in unicodedata.normalize("NFD", pregunta.lower())
            if unicodedata.category(caracter) != "Mn"
        )
        pide_camiones_aprobados = (
            re.search(r"\b(camiones?|unidades?)\b", pregunta_normalizada)
            and any(palabra in pregunta_normalizada for palabra in ("verificacion", "cumplen", "aprobados", "autorizados"))
        )
        if pide_camiones_aprobados:
            return self.recuperar_camiones_verificados(limite=100)

        pide_incidentes = re.search(r"\b(incidente|incidentes|accidente|accidentes)\b", pregunta_normalizada)
        if pide_incidentes:
            return self.recuperar_incidentes(pregunta, limite=limite)

        placa = re.search(r"\bCAM[- ]?\d{2,}\b", pregunta.upper())
        if placa:
            valor = placa.group(0).replace(" ", "-")
            resultado = []
            for nombre in ("camiones", "accesos", "incidentes", "evaluaciones_llm"):
                campos = {
                    "camiones": ("placa",),
                    "accesos": ("placa",),
                    "incidentes": ("placa",),
                    "evaluaciones_llm": ("prompt",),
                }[nombre]
                condiciones = [{campo: valor} if campo != "prompt" else {campo: {"$regex": re.escape(valor), "$options": "i"}} for campo in campos]
                for documento in self.listar(nombre, {"$or": condiciones}, limite):
                    documento["origen"] = nombre
                    resultado.append(documento)
            return resultado[:limite]

        ignorar = {"que", "cual", "cuales", "hay", "dime", "muestra", "dame", "datos", "sobre", "para", "con", "los", "las", "una", "uno"}
        terminos = [
            palabra for palabra in re.findall(r"[\w-]{4,}", pregunta_normalizada)
            if palabra not in ignorar
        ]
        if not terminos:
            return []

        patron = "|".join(re.escape(palabra) for palabra in terminos[:5])
        opciones = {"$regex": patron, "$options": "i"}
        busquedas = {
            "riesgos_eticos": {"$or": [{"descripcion": opciones}, {"categoria": opciones}, {"modulo": opciones}]},
            "evaluaciones_llm": {"$or": [{"prompt": opciones}, {"modelo": opciones}, {"metodo": opciones}]},
            "camiones": {"$or": [{"placa": opciones}, {"empresa": opciones}]},
            "accesos": {"$or": [{"placa": opciones}, {"decision_operativa": opciones}, {"operador": opciones}]},
        }
        if any(t.startswith(("riesg", "etica", "etico", "mitig")) for t in terminos):
            orden = ("riesgos_eticos",)
        elif any(t.startswith(("modelo", "evaluacion", "prompt", "ollama")) for t in terminos):
            orden = ("evaluaciones_llm",)
        else:
            orden = ("incidentes",)

        encontrados = []
        for nombre in orden:
            if nombre == "incidentes":
                encontrados.extend(self.recuperar_incidentes(pregunta, limite))
                continue
            for documento in self.listar(nombre, busquedas[nombre], limite):
                documento["origen"] = nombre
                encontrados.append(documento)
        return encontrados[:limite]

    def close_connection(self):
        if self.client:
            self.client.close()

    def cerrar(self):
        self.close_connection()


BaseDatos = MongoConnection