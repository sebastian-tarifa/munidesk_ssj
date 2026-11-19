import streamlit as st
from datetime import datetime
from db import get_conn, cargar_tablas, obtener_lista_tecnicos

user = st.session_state.usuario_logueado
lista_tecnicos_disponibles = obtener_lista_tecnicos()
df_tickets, df_historial_all, df_elementos_all = cargar_tablas()

st.subheader("🖥️ Trazabilidad por Código de Elemento Patrimonial")

if len(df_elementos_all) == 0:
    st.warning("No hay elementos patrimoniales cargados en la base de datos.")
    st.stop()

# Armar opciones descriptivas para el botón desplegable con búsqueda integrada
opciones_elementos = [
    f"{row['codigo_elemento']} — {row['tipo']} ({row['marca_modelo']}) | {row['secretaria']}"
    for _, row in df_elementos_all.iterrows()
]

col_e1, col_e2 = st.columns([2.2, 1])
with col_e1:
    opcion_seleccionada = st.selectbox(
        "Seleccioná o escribí el Código Patrimonial a consultar:",
        options=opciones_elementos,
        index=0,
        placeholder="Escribí para filtrar por código, equipo o secretaría..."
    )
    codigo_buscado = opcion_seleccionada.split(" — ")[0].strip()

with col_e2:
    st.metric("Total Activos en Inventario", f"{len(df_elementos_all)} equipos")

if codigo_buscado:
    ficha = df_elementos_all[df_elementos_all["codigo_elemento"] == codigo_buscado]
    if len(ficha) == 0:
        st.warning(f"No existe ningún equipo registrado con el código `{codigo_buscado}`.")
    else:
        item = ficha.iloc[0]
        st.success(
            f"**Ficha Técnica:** {item['tipo']} | **Modelo:** {item['marca_modelo']} | "
            f"**Área:** {item['secretaria']} | **Estado:** {item['estado_activo']}"
        )

        df_tk_elem = df_tickets[df_tickets["codigo_elemento"] == codigo_buscado].reset_index(drop=True)
        df_hist_elem = df_historial_all[df_historial_all["codigo_elemento"] == codigo_buscado].sort_values(by="id", ascending=False)[
            ["fecha_hora", "numero_ticket", "usuario", "tipo_evento", "detalle"]
        ]

        with st.container(border=True):
            st.markdown(f"#### Tickets asociados a este equipo ({len(df_tk_elem)})")
            if len(df_tk_elem) == 0:
                st.info("Este equipo patrimonial aún no registra tickets de incidentes.")
            else:
                st.caption("💡 Hacé clic sobre cualquier fila o número de ticket para abrir su detalle e intervenirlo abajo:")

                columnas_tk = [
                    "numero_ticket", "fecha_creacion", "categoria",
                    "prioridad", "estado", "tecnico_asignado", "descripcion"
                ]
                evento_tk_elem = st.dataframe(
                    df_tk_elem[columnas_tk],
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="tabla_tickets_elemento"
                )

                filas_sel = evento_tk_elem.selection.rows
                if filas_sel:
                    ticket_sel = df_tk_elem.iloc[filas_sel[0]]["numero_ticket"]
                    datos_tk = df_tk_elem[df_tk_elem["numero_ticket"] == ticket_sel].iloc[0]

                    st.markdown("---")
                    st.subheader(f"Detalle del Ticket Seleccionado: {ticket_sel}")
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
                            with st.form("form_actualizar_tk_elemento"):
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

        with st.container(border=True):
            st.markdown(f"#### Historial técnico completo del equipo ({len(df_hist_elem)} registros)")
            if len(df_hist_elem) == 0:
                st.caption("Sin intervenciones registradas en la bitácora para este elemento.")
            else:
                st.dataframe(df_hist_elem, use_container_width=True, hide_index=True)