import streamlit as st
from db import init_db, get_conn, hash_pass
from styles import aplicar_estilos_web, render_cabecera_web, render_pie_web

st.set_page_config(
    page_title="MuniDesk SSJ - Portal de Mesa de Ayuda IT",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_db()
aplicar_estilos_web()

if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None

if "ultimo_ticket_creado" not in st.session_state:
    st.session_state.ultimo_ticket_creado = None

if st.session_state.usuario_logueado is None:
    st.markdown("""
        <div class="muni-header">
            <div>
                <h1>🏛️ MuniDesk SSJ — Portal de Soporte Técnico IT</h1>
                <p>Municipalidad de San Salvador de Jujuy · Acceso al Sistema de Mesa de Ayuda</p>
            </div>
            <div class="muni-badge">Intranet Municipal</div>
        </div>
    """, unsafe_allow_html=True)

    col_izq, col_centro, col_der = st.columns([1, 1.3, 1])
    with col_centro:
        with st.container(border=True):
            st.subheader("🔐 Iniciar Sesión")
            st.caption("Ingresá con tu usuario institucional para operar en el sistema.")
            with st.form("form_login"):
                user_input = st.text_input("Usuario Municipal", placeholder="Ej: admin, rtarifa o agente.rentas")
                pass_input = st.text_input("Contraseña", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Ingresar al Portal", use_container_width=True, type="primary")

                if submit:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT * FROM usuarios WHERE username = ? AND password_hash = ?",
                        (user_input.strip(), hash_pass(pass_input.strip()))
                    )
                    user = cur.fetchone()
                    conn.close()

                    if user:
                        st.session_state.usuario_logueado = dict(user)
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")

        with st.expander("Ver credenciales de prueba"):
            st.markdown(
                "- **Administrador:** `admin` / `admin123`\n"
                "- **Técnico IT:** `rtarifa` / `muni2026`\n"
                "- **Operador (Solo carga):** `agente.rentas` / `1234`"
            )

    render_pie_web()
    st.stop()

user = st.session_state.usuario_logueado
rol = user["rol"]

render_cabecera_web(user)

_, col_logout = st.columns([6, 1])
with col_logout:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_logueado = None
        st.session_state.ultimo_ticket_creado = None
        st.rerun()

# Definición de páginas según permisos
pag_nuevo = st.Page("pages/1_nuevo_ticket.py", title="Abrir Nuevo Ticket", icon="➕", default=(rol == "Operador"))
pag_bandeja = st.Page("pages/2_bandeja_tickets.py", title="Bandeja de Tickets", icon="📋", default=(rol != "Operador"))
pag_elemento = st.Page("pages/3_consulta_elemento.py", title="Por Elemento", icon="🖥️")
pag_carga_elem = st.Page("pages/7_carga_elementos.py", title="Carga de Elementos", icon="📦")
pag_historial = st.Page("pages/4_historial_auditoria.py", title="Historial", icon="📜")
pag_estadisticas = st.Page("pages/5_estadisticas.py", title="Estadísticas y Reportes", icon="📊")
pag_abm = st.Page("pages/6_abm_usuarios.py", title="Gestión Técnicos (ABM)", icon="👥")

if rol == "Operador":
    paginas_disponibles = [pag_nuevo]
elif rol == "Tecnico IT":
    paginas_disponibles = [pag_bandeja, pag_nuevo, pag_elemento, pag_carga_elem, pag_historial, pag_estadisticas]
else:  # Administrador
    paginas_disponibles = [pag_bandeja, pag_nuevo, pag_elemento, pag_carga_elem, pag_historial, pag_estadisticas, pag_abm]

pg = st.navigation(paginas_disponibles, position="top")
pg.run()

render_pie_web()
