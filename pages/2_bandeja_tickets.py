import streamlit as st
from datetime import datetime
from db import get_conn, cargar_tablas, obtener_lista_tecnicos

user = st.session_state.usuario_logueado
lista_tecnicos_disponibles = obtener_lista_tecnicos()
df_tickets, df_historial_all, _ = cargar_tablas()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tickets", len(df_tickets))
m2.metric("Abiertos", len(df_tickets[df_tickets["estado"] == "Abierto"]))
m3.metric("En Proceso", len(df_tickets[df_tickets["estado"] == "En Proceso"]))
m4.metric("Resueltos", len(df_tickets[df_tickets["estado"] == "Resuelto"]))

st.markdown("---")
st.subheader("📋 Bandeja de Incidentes y Buscador")

c_busq, c_est, c_sec = st.columns([2, 1, 1.2])
with c_busq:
    busqueda_ticket = st.text_input(
        "Buscar por N° de Ticket o Código Patrimonial",
        placeholder="Ej: TK-2026-001 o IMP-REN-108"
    ).strip().upper()
with c_est:
    filtro_estado = st.selectbox("Estado", ["Todos", "Abierto", "En Proceso", "Resuelto"])
with c_sec:
    secretarias_lista = ["Todas"] + sorted(df_tickets["secretaria"].unique().tolist())
    filtro_sec = st.selectbox("Secretaría", secretarias_lista)

df_filtrado = df_tickets.copy().reset_index(drop=True)
if busqueda_ticket:
    df_filtrado = df_filtrado[
        df_filtrado["numero_ticket"].str.contains(busqueda_ticket, case=False, na=False) |
        df_filtrado["codigo_elemento"].str.contains(busqueda_ticket, case=False, na=False)
    ].reset_index(drop=True)
if filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado"] == filtro_estado].reset_index(drop=True)
if filtro_sec != "Todas":
    df_filtrado = df_filtrado[df_filtrado["secretaria"] == filtro_sec].reset_index(drop=True)

st.caption("💡 Hacé clic sobre cualquier fila o número de ticket para abrir su detalle e historial abajo:")

columnas_tabla = [
    "numero_ticket", "codigo_elemento", "secretaria", "oficina",
    "categoria", "prioridad", "estado", "tecnico_asignado", "fecha_creacion"
]

evento_tabla = st.dataframe(
    df_filtrado[columnas_tabla],
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    key="tabla_bandeja_tickets"
)

st.markdown("---")
st.subheader("Detalle e Intervención Técnica")

if len(df_filtrado) == 0:
    st.warning("No se encontraron tickets con los filtros aplicados.")
else:
    filas_seleccionadas = evento_tabla.selection.rows
    if filas_seleccionadas:
        ticket_sel = df_filtrado.iloc[filas_seleccionadas[0]]["numero_ticket"]
    else:
        ticket_sel = df_filtrado.iloc[0]["numero_ticket"]

    datos_tk = df_filtrado[df_filtrado["numero_ticket"] == ticket_sel].iloc[0]

    col_info, col_accion = st.columns([1.2, 1])

    with col_info:
        with st.container(border=True):
            st.markdown(f"### 🎫 {datos_tk['numero_ticket']} — Elemento: `{datos_tk['codigo_elemento']}`")
            st.markdown(f"**Dependencia:** {datos_tk['secretaria']} — *{datos_tk['oficina']}*")
            st.markdown(f"**Solicitante:** {datos_tk['solicitante']} | **Creado:** {datos_tk['fecha_creacion']} | **Prioridad:** `{datos_tk['prioridad']}`")
            st.info(f"**Descripción del problema:**\n\n{datos_tk['descripcion']}")

            df_hist_tk = df_historial_all[df_historial_all["numero_ticket"] == ticket_sel][
                ["fecha_hora", "usuario", "tipo_evento", "detalle"]
            ]
            st.markdown("**Línea de Tiempo del Ticket:**")
            st.dataframe(df_hist_tk, use_container_width=True, hide_index=True)

    with col_accion:
        with st.container(border=True):
            with st.form("form_actualizar_ticket"):
                st.markdown("**Actualizar Estado / Registrar Seguimiento**")
                nuevo_estado = st.selectbox(
                    "Nuevo Estado",
                    ["Abierto", "En Proceso", "Resuelto"],
                    index=["Abierto", "En Proceso", "Resuelto"].index(datos_tk["estado"])
                )
                opciones_tec = lista_tecnicos_disponibles.copy()
                if datos_tk["tecnico_asignado"] not in opciones_tec:
                    opciones_tec.append(datos_tk["tecnico_asignado"])

                nuevo_tecnico = st.selectbox(
                    "Técnico Asignado",
                    opciones_tec,
                    index=opciones_tec.index(datos_tk["tecnico_asignado"])
                )
                nota_seguimiento = st.text_area(
                    "Detalle técnico de la intervención",
                    placeholder="Describí el diagnóstico, repuesto utilizado o solución aplicada..."
                )
                btn_guardar = st.form_submit_button("Guardar Cambios en Bitácora", type="primary", use_container_width=True)

                if btn_guardar:
                    if not nota_seguimiento.strip():
                        st.error("Ingresá una nota de seguimiento para dejar registro en el historial.")
                    else:
                        ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE tickets SET estado = ?, tecnico_asignado = ? WHERE numero_ticket = ?",
                            (nuevo_estado, nuevo_tecnico, ticket_sel)
                        )
                        evento_label = "Resolución" if nuevo_estado == "Resuelto" else f"Cambio a {nuevo_estado}"
                        cur.execute(
                            """INSERT INTO historial (numero_ticket, codigo_elemento, fecha_hora, usuario, tipo_evento, detalle)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (
                                ticket_sel,
                                datos_tk["codigo_elemento"],
                                ahora,
                                user["nombre_completo"],
                                evento_label,
                                nota_seguimiento.strip()
                            )
                        )
                        conn.commit()
                        conn.close()
                        st.success("Ticket actualizado y registrado en historial.")
                        st.rerun()
