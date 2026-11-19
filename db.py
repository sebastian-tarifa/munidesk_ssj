import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "munidesk_ssj.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            email TEXT DEFAULT '',
            rol TEXT NOT NULL,
            area TEXT NOT NULL
        )
    """)

    # Migración segura si la tabla usuarios ya existía sin columna email
    cur.execute("PRAGMA table_info(usuarios)")
    cols_u = [row[1] for row in cur.fetchall()]
    if "email" not in cols_u:
        cur.execute("ALTER TABLE usuarios ADD COLUMN email TEXT DEFAULT ''")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS elementos (
            codigo_elemento TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            marca_modelo TEXT NOT NULL,
            secretaria TEXT NOT NULL,
            estado_activo TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_ticket TEXT UNIQUE NOT NULL,
            codigo_elemento TEXT NOT NULL,
            secretaria TEXT NOT NULL,
            oficina TEXT NOT NULL,
            solicitante TEXT NOT NULL,
            origen_ticket TEXT DEFAULT 'Presencial',
            categoria TEXT NOT NULL,
            asunto TEXT DEFAULT 'Incidente Técnico',
            prioridad TEXT NOT NULL,
            estado TEXT NOT NULL,
            tecnico_asignado TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL
        )
    """)

    cur.execute("PRAGMA table_info(tickets)")
    cols_t = [row[1] for row in cur.fetchall()]
    if "origen_ticket" not in cols_t:
        cur.execute("ALTER TABLE tickets ADD COLUMN origen_ticket TEXT DEFAULT 'Presencial'")
    if "asunto" not in cols_t:
        cur.execute("ALTER TABLE tickets ADD COLUMN asunto TEXT DEFAULT 'Incidente Técnico'")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_ticket TEXT NOT NULL,
            codigo_elemento TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            usuario TEXT NOT NULL,
            tipo_evento TEXT NOT NULL,
            detalle TEXT NOT NULL
        )
    """)

    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        usuarios_demo = [
            ("rtarifa", hash_pass("muni2026"), "Ricardo Tarifa", "rtarifa@sansalvadordejujuy.gob.ar", "Tecnico IT", "Secretaría de Hacienda"),
            ("admin", hash_pass("admin123"), "Soporte Central SSJ", "soporte@sansalvadordejujuy.gob.ar", "Administrador", "Dirección de Cómputos"),
            ("agente.rentas", hash_pass("1234"), "Laura Méndez", "lmendez@sansalvadordejujuy.gob.ar", "Operador", "Dirección General de Rentas"),
        ]
        cur.executemany("INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol, area) VALUES (?, ?, ?, ?, ?, ?)", usuarios_demo)

        elementos_demo = [
            ("PAT-HAC-042", "PC Escritorio", "Dell OptiPlex 7090 i7", "Secretaría de Hacienda", "Operativo con observación"),
            ("IMP-REN-108", "Impresora Térmica", "Epson TM-T20III POS", "Dirección General de Rentas", "En reparación"),
            ("POS-CAJ-009", "Terminal Caja", "HP ProDesk 400 G7 + Lector", "Tesorería Municipal", "Operativo"),
            ("NET-INT-015", "Switch Red", "Cisco Catalyst 2960 24P", "Intendencia", "Operativo"),
            ("PC-OBR-210", "Workstation CAD", "Lenovo ThinkStation P340", "Secretaría de Obras Públicas", "Operativo"),
        ]
        cur.executemany("INSERT INTO elementos VALUES (?, ?, ?, ?, ?)", elementos_demo)

        tickets_demo = [
            ("TK-2026-001", "IMP-REN-108", "Dirección General de Rentas", "Box Atención 4", "Laura Méndez", "Teléfono", "Impresoras / Ticketeadoras", "Falla impresión boletas tasa", "Alta", "En Proceso", "Ricardo Tarifa", "No imprime comprobantes de tasa municipal desde actualización de sistema.", "2026-11-10 08:30"),
            ("TK-2026-002", "PAT-HAC-042", "Secretaría de Hacienda", "Liquidaciones", "Carlos Mamani", "Sistema Interno", "Software / Sistemas", "Error certificado digital", "Media", "Abierto", "Sin asignar", "Error de certificado digital al intentar validar firma en sistema contable.", "2026-11-11 10:15"),
            ("TK-2026-003", "POS-CAJ-009", "Tesorería Municipal", "Caja Central 2", "Marta Quispe", "Presencial", "Hardware", "Lector código de barras", "Alta", "Resuelto", "Ricardo Tarifa", "El lector de código de barras no reconoce boletas de patente.", "2026-11-09 09:00"),
            ("TK-2026-004", "NET-INT-015", "Intendencia", "Mesa de Entradas", "Jorge Villalba", "Teléfono", "Redes / Conectividad", "Microcortes fibra óptica", "Crítica", "En Proceso", "Soporte Central SSJ", "Microcortes intermitentes en enlace de fibra hacia planta baja.", "2026-11-12 07:45"),
        ]
        cur.executemany("""
            INSERT INTO tickets (numero_ticket, codigo_elemento, secretaria, oficina, solicitante, origen_ticket, categoria, asunto, prioridad, estado, tecnico_asignado, descripcion, fecha_creacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tickets_demo)

        historial_demo = [
            ("TK-2026-001", "IMP-REN-108", "2026-11-10 08:30", "Laura Méndez", "Creación", "Ticket generado por falla en impresora térmica Epson TM-T20III."),
            ("TK-2026-001", "IMP-REN-108", "2026-11-10 09:10", "Ricardo Tarifa", "Asignación / Diagnóstico", "Se asigna ticket. Se verifica puerto COM y cola de impresión spooler."),
            ("TK-2026-002", "PAT-HAC-042", "2026-11-11 10:15", "Carlos Mamani", "Creación", "Reporte de error en validación de certificado SSL/OpenSSL."),
            ("TK-2026-003", "POS-CAJ-009", "2026-11-09 09:00", "Marta Quispe", "Creación", "Falla en lectura de código de barras en Caja Central 2."),
            ("TK-2026-003", "POS-CAJ-009", "2026-11-09 11:20", "Ricardo Tarifa", "Resolución", "Se reconfigura modo HID del escáner y se realiza prueba de cobro exitosa."),
            ("TK-2026-004", "NET-INT-015", "2026-11-12 07:45", "Jorge Villalba", "Creación", "Pérdida de paquetes en puestos de Mesa de Entradas."),
        ]
        cur.executemany("""
            INSERT INTO historial (numero_ticket, codigo_elemento, fecha_hora, usuario, tipo_evento, detalle)
            VALUES (?, ?, ?, ?, ?, ?)
        """, historial_demo)

    conn.commit()
    conn.close()

def generar_nuevo_numero_ticket() -> str:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM tickets")
    max_id = cur.fetchone()[0] or 0
    conn.close()
    anio = datetime.now().year
    return f"TK-{anio}-{max_id + 1:03d}"

def obtener_lista_tecnicos() -> list:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT nombre_completo FROM usuarios WHERE rol IN ('Tecnico IT', 'Administrador') ORDER BY nombre_completo ASC")
    nombres = [row["nombre_completo"] for row in cur.fetchall()]
    conn.close()
    return ["Sin asignar"] + nombres

def cargar_tablas():
    conn = get_conn()
    df_tickets = pd.read_sql_query("SELECT * FROM tickets ORDER BY id DESC", conn)
    df_historial = pd.read_sql_query("SELECT * FROM historial ORDER BY id ASC", conn)
    df_elementos = pd.read_sql_query("SELECT * FROM elementos ORDER BY codigo_elemento ASC", conn)
    conn.close()
    return df_tickets, df_historial, df_elementos