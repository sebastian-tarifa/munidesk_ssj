import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from db import get_conn, generar_nuevo_numero_ticket, obtener_lista_tecnicos
from styles import generar_html_impresion_ticket

user = st.session_state.usuario_logueado
es_tecnico = user["rol"] in ("Tecnico IT", "Administrador")
lista_tecnicos_disponibles = obtener_lista_tecnicos()

st.subheader("➕ Abrir un Nuevo Ticket (Estilo SCP Soporte SSJ)")

# Vista previa imprimible automática tras generar el ticket
if st.session_state.ultimo_ticket_creado:
    tk_ok = st.session_state.ultimo_ticket_creado
    st.success(f"✅ **Ticket `{tk_ok['numero_ticket']}` abierto correctamente.** Podés imprimir la orden de trabajo ahora:")

    html_comprobante = generar_html_impresion_ticket(tk_ok)

    col_btn1, col_btn2, _ = st.columns([1.2, 1.2, 2])
    with col_btn1:
        st.download_button(
            label="📄 Descargar Comprobante (HTML / PDF)",
            data=html_comprobante.encode("utf-8"),
            file_name=f"Ticket_{tk_ok['numero_ticket']}.html",
            mime="text/html",
            use_container_width=True
        )
    with col_btn2:
        if st.button("✖️ Cerrar Vista de Impresión", use_container_width=True):
            st.session_state.ultimo_ticket_creado = None
            st.rerun()

    components.html(html_comprobante, height=540, scrolling=True)
    st.divider()

conn = get_conn()
df_elementos = pd.read_sql_query("SELECT * FROM elementos ORDER BY codigo_elemento ASC", conn)
conn.close()

with st.container(border=True):
    modo_equipo = st.radio(
        "Identificación del Elemento Patrimonial:",
        ["Seleccionar equipo existente en inventario", "Registrar código de elemento nuevo"],
        horizontal=True
    )

    with st.form("form_scp_nuevo_ticket", clear_on_submit=True):
        # ----------------------------------------------------------------------
        # SECCIÓN 1 (osTicket SCP): USUARIO Y ORIGEN DEL TICKET
        # ----------------------------------------------------------------------
        st.markdown('<div class="scp-section-bar">1. Usuario y Origen del Ticket</div>', unsafe_allow_html=True)
        u1, u2, u3 = st.columns([1.3, 1.3, 1])
        with u1:
            solicitante_nuevo = st.text_input("Agente Solicitante *", value=user["nombre_completo"])
        with u2:
            secretarias_opciones = [
                "Secretaría de Hacienda",
                "Dirección General de Rentas",
                "Tesorería Municipal",
                "Intendencia",
                "Secretaría de Obras Públicas",
                "Dirección de Tránsito",
                "Recursos Humanos",
                "Dirección de Cómputos"
            ]
            idx_sec = secretarias_opciones.index(user["area"]) if user["area"] in secretarias_opciones else 0
            secretaria_nueva = st.selectbox("Secretaría / Departamento *", secretarias_opciones, index=idx_sec)
        with u3:
            if es_tecnico:
                origen_ticket = st.selectbox("Origen del Ticket *", ["Teléfono", "Presencial", "Email", "Sistema Interno"])
            else:
                origen_ticket = "Sistema Interno"
                st.text_input("Origen del Ticket", value="Sistema Interno", disabled=True)

        oficina_nueva = st.text_input("Oficina / Box / Interno Telefónico *", placeholder="Ej: Box 4 - Planta Baja (Int. 412)")

        # ----------------------------------------------------------------------
        # SECCIÓN 2 (osTicket SCP + PATRIMONIO): DETALLES DEL TICKET Y EQUIPO
        # ----------------------------------------------------------------------
        st.markdown('<div class="scp-section-bar">2. Detalles del Ticket y Elemento Patrimonial</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)

        with d1:
            if modo_equipo == "Seleccionar equipo existente en inventario":
                opciones_elem = [
                    f"{row['codigo_elemento']} - {row['tipo']} ({row['marca_modelo']})"
                    for _, row in df_elementos.iterrows()
                ]
                elem_elegido = st.selectbox("Código de Elemento Patrimonial *", opciones_elem)
                codigo_final = elem_elegido.split(" - ")[0]
                tipo_nuevo_eq = ""
                modelo_nuevo_eq = ""
            else:
                codigo_final = st.text_input(
                    "Nuevo Código Patrimonial *",
                    placeholder="Ej: PC-HAC-099 o IMP-TRA-004"
                ).strip().upper()
                sub_e1, sub_e2 = st.columns(2)
                with sub_e1:
                    tipo_nuevo_eq = st.text_input("Tipo de Equipo *", placeholder="Ej: PC Escritorio / Impresora")
                with sub_e2:
                    modelo_nuevo_eq = st.text_input("Marca / Modelo", placeholder="Ej: HP ProDesk / Epson")

            categoria_nueva = st.selectbox(
                "Tema de Ayuda (Help Topic) *",
                [
                    "Hardware",
                    "Software / Sistemas",
                    "Redes / Conectividad",
                    "Impresoras / Ticketeadoras",
                    "Telefonía IP",
                    "Acceso / Usuarios"
                ]
            )

        with d2:
            prioridad_nueva = st.selectbox("Nivel de Prioridad *", ["Baja", "Media", "Alta", "Crítica"], index=1)

            if es_tecnico:
                tecnico_inicial = st.selectbox("Asignar a Técnico", lista_tecnicos_disponibles)
                estado_seleccionado = st.selectbox("Estado del Ticket", ["Abierto", "En Proceso", "Resuelto"])
            else:
                tecnico_inicial = "Sin asignar"
                estado_seleccionado = "Abierto"

        # ----------------------------------------------------------------------
        # SECCIÓN 3 (osTicket SCP): ASUNTO, RESUMEN Y NOTA INTERNA
        # ----------------------------------------------------------------------
        st.markdown('<div class="scp-section-bar">3. Resumen del Problema</div>', unsafe_allow_html=True)
        asunto_nuevo = st.text_input("Asunto *", placeholder="Ej: Impresora térmica no emite comprobantes de caja")
        descripcion_nueva = st.text_area(
            "Descripción detallada del incidente *",
            placeholder="Detalle de la falla, mensajes de error o pruebas ya realizadas...",
            height=110
        )

        nota_interna_inicial = ""
        if es_tecnico:
            nota_interna_inicial = st.text_input(
                "Nota Interna Inicial (Opcional - Solo visible para técnicos)",
                placeholder="Ej: Se coordina visita técnica para las 10:30 hs."
            )

        col_sub1, col_sub2 = st.columns([2, 1])
        with col_sub1:
            crear_btn = st.form_submit_button("🎫 Abrir Ticket e Imprimir Comprobante", type="primary", use_container_width=True)
        with col_sub2:
            st.form_submit_button("🔄 Limpiar Formulario", use_container_width=True)

        if crear_btn:
            if (
                not codigo_final
                or not oficina_nueva.strip()
                or not solicitante_nuevo.strip()
                or not asunto_nuevo.strip()
                or not descripcion_nueva.strip()
            ):
                st.error("Completá todos los campos obligatorios marcados con (*).")
            elif modo_equipo == "Registrar código de elemento nuevo" and not tipo_nuevo_eq.strip():
                st.error("Indicá el Tipo de Equipo para registrar el nuevo código patrimonial.")
            else:
                nuevo_nro = generar_nuevo_numero_ticket()
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

                if es_tecnico and estado_seleccionado == "Abierto" and tecnico_inicial != "Sin asignar":
                    estado_final = "En Proceso"
                else:
                    estado_final = estado_seleccionado

                conn = get_conn()
                cur = conn.cursor()

                if modo_equipo == "Registrar código de elemento nuevo":
                    cur.execute(
                        """INSERT OR IGNORE INTO elementos (codigo_elemento, tipo, marca_modelo, secretaria, estado_activo)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            codigo_final,
                            tipo_nuevo_eq.strip(),
                            modelo_nuevo_eq.strip() or "Sin especificar",
                            secretaria_nueva,
                            "Con incidente abierto"
                        )
                    )

                cur.execute(
                    """INSERT INTO tickets (numero_ticket, codigo_elemento, secretaria, oficina, solicitante, origen_ticket, categoria, asunto, prioridad, estado, tecnico_asignado, descripcion, fecha_creacion)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        nuevo_nro, codigo_final, secretaria_nueva, oficina_nueva.strip(),
                        solicitante_nuevo.strip(), origen_ticket, categoria_nueva, asunto_nuevo.strip(),
                        prioridad_nueva, estado_final, tecnico_inicial, descripcion_nueva.strip(), ahora
                    )
                )

                cur.execute(
                    """INSERT INTO historial (numero_ticket, codigo_elemento, fecha_hora, usuario, tipo_evento, detalle)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        nuevo_nro,
                        codigo_final,
                        ahora,
                        user["nombre_completo"],
                        "Creación",
                        f"[{origen_ticket}] {asunto_nuevo.strip()} — {descripcion_nueva.strip()}"
                    )
                )

                if nota_interna_inicial.strip():
                    cur.execute(
                        """INSERT INTO historial (numero_ticket, codigo_elemento, fecha_hora, usuario, tipo_evento, detalle)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            nuevo_nro,
                            codigo_final,
                            ahora,
                            user["nombre_completo"],
                            "Nota Interna",
                            nota_interna_inicial.strip()
                        )
                    )

                conn.commit()
                conn.close()

                st.session_state.ultimo_ticket_creado = {
                    "numero_ticket": nuevo_nro,
                    "codigo_elemento": codigo_final,
                    "secretaria": secretaria_nueva,
                    "oficina": oficina_nueva.strip(),
                    "solicitante": solicitante_nuevo.strip(),
                    "origen_ticket": origen_ticket,
                    "categoria": categoria_nueva,
                    "asunto": asunto_nuevo.strip(),
                    "prioridad": prioridad_nueva,
                    "estado": estado_final,
                    "tecnico_asignado": tecnico_inicial,
                    "descripcion": descripcion_nueva.strip(),
                    "fecha_creacion": ahora
                }
                st.rerun()