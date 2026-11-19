import streamlit as st
import pandas as pd
import unicodedata
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import get_conn, hash_pass

user = st.session_state.usuario_logueado
if user["rol"] != "Administrador":
    st.error("Acceso denegado. Esta sección es exclusiva para Administradores.")
    st.stop()

def normalizar_texto(texto: str) -> str:
    texto_norm = unicodedata.normalize("NFD", texto.lower().strip())
    return "".join(c for c in texto_norm if unicodedata.category(c) != "Mn" and c.isalnum())

def generar_username_automatico(nombre: str, apellido: str, usuarios_existentes: list) -> str:
    ini_nombre = normalizar_texto(nombre)[:1]
    ape_limpio = normalizar_texto(apellido)
    base_user = f"{ini_nombre}{ape_limpio}"
    if not base_user:
        return ""
    candidato = base_user
    contador = 2
    while candidato in usuarios_existentes:
        candidato = f"{base_user}{contador}"
        contador += 1
    return candidato

def enviar_correo_credenciales(destinatario: str, nombre_completo: str, username: str, password_plana: str, rol: str, area: str, smtp_cfg: dict) -> tuple[bool, str]:
    """Envía el correo con usuario y contraseña mediante SMTP."""
    asunto = "Alta de Usuario - Portal de Soporte Técnico IT (Municipalidad SSJ)"
    cuerpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.5;">
        <div style="max-width: 580px; margin: auto; border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0b3c6d; color: #ffffff; padding: 16px 20px;">
                <h2 style="margin: 0; font-size: 18px;">🏛️ Municipalidad de San Salvador de Jujuy</h2>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: #dbeafe;">Dirección de Cómputos · Mesa de Ayuda IT</p>
            </div>
            <div style="padding: 20px;">
                <p>Hola <strong>{nombre_completo}</strong>,</p>
                <p>Se ha generado tu cuenta de acceso al sistema interno de gestión de tickets <strong>MuniDesk SSJ</strong>.</p>
                <table style="width: 100%; border-collapse: collapse; margin: 16px 0; background: #f9fafb;">
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #e5e7eb; font-weight: bold;">Usuario (Login):</td>
                        <td style="padding: 8px 12px; border: 1px solid #e5e7eb; font-family: monospace; font-size: 15px;">{username}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #e5e7eb; font-weight: bold;">Contraseña Inicial:</td>
                        <td style="padding: 8px 12px; border: 1px solid #e5e7eb; font-family: monospace; font-size: 15px;">{password_plana}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; border: 1px solid #e5e7eb; font-weight: bold;">Perfil Asignado:</td>
                        <td style="padding: 8px 12px; border: 1px solid #e5e7eb;">{rol} ({area})</td>
                    </tr>
                </table>
                <p style="font-size: 12px; color: #6b7280;">Por seguridad, recordá resguardar estas credenciales.</p>
            </div>
        </div>
    </body>
    </html>
    """

    if not smtp_cfg.get("remitente") or not smtp_cfg.get("clave_app"):
        return False, cuerpo_html

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"] = smtp_cfg["remitente"]
        msg["To"] = destinatario
        msg.attach(MIMEText(cuerpo_html, "html", "utf-8"))

        with smtplib.SMTP(smtp_cfg["servidor"], int(smtp_cfg["puerto"]), timeout=10) as server:
            server.starttls()
            server.login(smtp_cfg["remitente"], smtp_cfg["clave_app"])
            server.sendmail(smtp_cfg["remitente"], destinatario, msg.as_string())
        return True, "Correo enviado exitosamente."
    except Exception as e:
        return False, f"Error SMTP: {e}"

st.subheader("👥 Administración de Técnicos y Usuarios del Sistema (ABM)")

# Configuración opcional de servidor SMTP para envío real de correos
with st.expander("⚙️ Configurar Servidor de Correo Saliente (SMTP) para envío real"):
    s1, s2, s3, s4 = st.columns([1.4, 0.7, 1.5, 1.4])
    with s1:
        smtp_host = st.text_input("Servidor SMTP", value="smtp.gmail.com", key="smtp_host")
    with s2:
        smtp_port = st.number_input("Puerto", value=587, step=1, key="smtp_port")
    with s3:
        smtp_user = st.text_input("Correo Remitente", placeholder="soporte.ssj@gmail.com", key="smtp_user")
    with s4:
        smtp_pass = st.text_input("Contraseña de Aplicación", type="password", placeholder="xxxx xxxx xxxx xxxx", key="smtp_pass")
    st.caption("Si dejás vacío el correo remitente, el sistema funcionará en modo simulación mostrando en pantalla el correo generado con las credenciales.")

conn = get_conn()
df_usuarios = pd.read_sql_query(
    "SELECT username, nombre_completo, email, rol, area FROM usuarios ORDER BY rol ASC, nombre_completo ASC",
    conn
)
conn.close()

lista_existentes = df_usuarios["username"].tolist()

# Estados para autocompletado en vivo y editable
for campo in ["alta_nombre", "alta_apellido", "alta_username", "alta_email"]:
    if campo not in st.session_state:
        st.session_state[campo] = ""

if "ultimo_correo_simulado" not in st.session_state:
    st.session_state.ultimo_correo_simulado = None

def actualizar_usuario_en_vivo():
    st.session_state.alta_username = generar_username_automatico(
        st.session_state.alta_nombre,
        st.session_state.alta_apellido,
        lista_existentes
    )

# Mostrar notificación o vista previa del correo tras dar de alta
if st.session_state.ultimo_correo_simulado:
    info_mail = st.session_state.ultimo_correo_simulado
    if info_mail["enviado_real"]:
        st.success(f"📧 **Correo enviado correctamente a `{info_mail['destinatario']}`** con las credenciales de `{info_mail['username']}`.")
    else:
        st.info(f"📨 **Usuario `{info_mail['username']}` creado.** (Modo simulación SMTP — Vista previa del correo preparado para **`{info_mail['destinatario']}`**):")
        st.markdown(info_mail["html"], unsafe_allow_html=True)
    if st.button("Cerrar aviso de correo"):
        st.session_state.ultimo_correo_simulado = None
        st.rerun()

st.markdown("#### Personal Registrado Actualmente")
st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
st.divider()

col_alta, col_mod, col_baja = st.columns(3)

# ==============================================================================
# 1. ALTA DE NUEVO TÉCNICO / USUARIO
# ==============================================================================
with col_alta:
    with st.container(border=True):
        st.markdown("##### ➕ Alta de Nuevo Técnico / Usuario")

        c_nom, c_ape = st.columns(2)
        with c_nom:
            st.text_input("Nombre *", placeholder="Ej: Juan", key="alta_nombre", on_change=actualizar_usuario_en_vivo)
        with c_ape:
            st.text_input("Apellido *", placeholder="Ej: Pérez", key="alta_apellido", on_change=actualizar_usuario_en_vivo)

        usuario_final = st.text_input(
            "Usuario (Login generado - Editable) *",
            placeholder="Se completa automáticamente...",
            key="alta_username"
        ).strip().lower()

        email_final = st.text_input(
            "Correo Electrónico Institucional *",
            placeholder="Ej: jperez@sansalvadordejujuy.gob.ar",
            key="alta_email"
        ).strip().lower()

        nuevo_rol = st.selectbox("Rol en el Sistema *", ["Tecnico IT", "Administrador", "Operador"], key="alta_rol")
        nueva_area = st.selectbox(
            "Área / Secretaría *",
            [
                "Dirección de Cómputos",
                "Secretaría de Hacienda",
                "Dirección General de Rentas",
                "Tesorería Municipal",
                "Intendencia",
                "Secretaría de Obras Públicas",
                "Dirección de Tránsito",
                "Recursos Humanos"
            ],
            key="alta_area"
        )
        nueva_pass = st.text_input("Contraseña Inicial *", type="password", key="alta_pass")

        if st.button("Dar de Alta y Enviar Credenciales", type="primary", use_container_width=True):
            nom_val = st.session_state.alta_nombre.strip()
            ape_val = st.session_state.alta_apellido.strip()

            if not nom_val or not ape_val or not usuario_final or not email_final or not nueva_pass:
                st.error("Completá Nombre, Apellido, Usuario, Correo Electrónico y Contraseña.")
            elif "@" not in email_final or "." not in email_final:
                st.error("Ingresá un correo electrónico válido.")
            elif usuario_final in lista_existentes:
                st.error(f"El usuario `{usuario_final}` ya existe. Editalo en el campo Usuario.")
            else:
                nombre_completo_final = f"{nom_val.title()} {ape_val.title()}"
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol, area) VALUES (?, ?, ?, ?, ?, ?)",
                    (usuario_final, hash_pass(nueva_pass), nombre_completo_final, email_final, nuevo_rol, nueva_area)
                )
                conn.commit()
                conn.close()

                smtp_cfg = {
                    "servidor": smtp_host.strip(),
                    "puerto": smtp_port,
                    "remitente": smtp_user.strip(),
                    "clave_app": smtp_pass.strip()
                }
                enviado, resultado = enviar_correo_credenciales(
                    email_final, nombre_completo_final, usuario_final, nueva_pass, nuevo_rol, nueva_area, smtp_cfg
                )

                if not enviado and smtp_user.strip():
                    st.warning(f"Usuario guardado en base de datos, pero falló el envío SMTP: {resultado}")
                else:
                    st.session_state.ultimo_correo_simulado = {
                        "enviado_real": enviado,
                        "destinatario": email_final,
                        "username": usuario_final,
                        "html": resultado
                    }

                st.session_state.alta_nombre = ""
                st.session_state.alta_apellido = ""
                st.session_state.alta_username = ""
                st.session_state.alta_email = ""
                st.rerun()

# ==============================================================================
# 2. MODIFICACIÓN DE DATOS O CLAVE
# ==============================================================================
with col_mod:
    with st.container(border=True):
        st.markdown("##### ✏️ Modificar Datos o Clave")
        user_a_editar = st.selectbox(
            "Seleccioná usuario a editar:",
            df_usuarios["username"].tolist(),
            key="sel_edit_user"
        )
        datos_u = df_usuarios[df_usuarios["username"] == user_a_editar].iloc[0]

        with st.form("form_mod_usuario"):
            edit_nombre = st.text_input("Nombre y Apellido", value=datos_u["nombre_completo"])
            edit_email = st.text_input("Correo Electrónico", value=datos_u["email"] or "")
            roles_lista = ["Tecnico IT", "Administrador", "Operador"]
            edit_rol = st.selectbox(
                "Rol",
                roles_lista,
                index=roles_lista.index(datos_u["rol"]) if datos_u["rol"] in roles_lista else 0
            )
            edit_area = st.text_input("Área / Secretaría", value=datos_u["area"])
            edit_pass = st.text_input("Nueva Contraseña (dejar vacío para no cambiar)", type="password")
            btn_mod = st.form_submit_button("Guardar Cambios", use_container_width=True)

            if btn_mod:
                if not edit_nombre.strip() or not edit_area.strip():
                    st.error("El nombre y el área no pueden quedar vacíos.")
                else:
                    conn = get_conn()
                    cur = conn.cursor()
                    if edit_pass.strip():
                        cur.execute(
                            "UPDATE usuarios SET nombre_completo = ?, email = ?, rol = ?, area = ?, password_hash = ? WHERE username = ?",
                            (edit_nombre.strip(), edit_email.strip().lower(), edit_rol, edit_area.strip(), hash_pass(edit_pass.strip()), user_a_editar)
                        )
                    else:
                        cur.execute(
                            "UPDATE usuarios SET nombre_completo = ?, email = ?, rol = ?, area = ? WHERE username = ?",
                            (edit_nombre.strip(), edit_email.strip().lower(), edit_rol, edit_area.strip(), user_a_editar)
                        )
                    conn.commit()
                    conn.close()
                    st.success(f"Datos de `{user_a_editar}` actualizados.")
                    st.rerun()

# ==============================================================================
# 3. BAJA DE TÉCNICO / USUARIO
# ==============================================================================
with col_baja:
    with st.container(border=True):
        st.markdown("##### 🗑️ Baja de Técnico / Usuario")
        usuarios_borrables = [u for u in df_usuarios["username"].tolist() if u != user["username"]]

        if not usuarios_borrables:
            st.info("No hay otros usuarios disponibles para dar de baja.")
        else:
            with st.form("form_baja_usuario"):
                user_a_borrar = st.selectbox("Seleccioná usuario a eliminar:", usuarios_borrables)
                confirmar_baja = st.checkbox("Confirmo la baja definitiva de esta cuenta")
                btn_baja = st.form_submit_button("Eliminar Usuario", use_container_width=True)

                if btn_baja:
                    if not confirmar_baja:
                        st.warning("Marcá la casilla de confirmación antes de eliminar.")
                    else:
                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute("DELETE FROM usuarios WHERE username = ?", (user_a_borrar,))
                        conn.commit()
                        conn.close()
                        st.success(f"Usuario `{user_a_borrar}` eliminado del sistema.")
                        st.rerun()