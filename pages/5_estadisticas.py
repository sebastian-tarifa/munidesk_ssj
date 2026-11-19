import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
from db import cargar_tablas

def construir_html_reporte(df_rep: pd.DataFrame, filtros_texto: str, kpis: dict, sintesis: str) -> str:
    filas_html = ""
    for _, r in df_rep.iterrows():
        filas_html += f"""
        <tr>
            <td><strong>{r['numero_ticket']}</strong></td>
            <td>{r['fecha_creacion']}</td>
            <td>{r['codigo_elemento']}</td>
            <td>{r['secretaria']}</td>
            <td>{r['categoria']}</td>
            <td>{r['prioridad']}</td>
            <td>{r['estado']}</td>
            <td>{r['tecnico_asignado']}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Gestión IT - Municipalidad SSJ</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #111827;
                max-width: 960px;
                margin: 15px auto;
                padding: 24px;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #0b3c6d;
                padding-bottom: 12px;
                margin-bottom: 18px;
            }}
            .header h2 {{ margin: 0; color: #0b3c6d; font-size: 19px; }}
            .header p {{ margin: 3px 0 0 0; font-size: 12px; color: #4b5563; }}
            .filtros {{
                background: #f3f4f6;
                padding: 8px 12px;
                border-left: 4px solid #f59e0b;
                font-size: 12px;
                margin-bottom: 16px;
            }}
            .kpis {{
                display: flex;
                gap: 12px;
                margin-bottom: 18px;
            }}
            .kpi-card {{
                flex: 1;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                text-align: center;
                background: #f9fafb;
            }}
            .kpi-card span {{ display: block; font-size: 11px; color: #6b7280; }}
            .kpi-card strong {{ font-size: 18px; color: #0b3c6d; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 11.5px;
            }}
            th {{
                background: #0b3c6d;
                color: white;
                padding: 8px 6px;
                text-align: left;
            }}
            td {{
                border: 1px solid #d1d5db;
                padding: 6px;
            }}
            tr:nth-child(even) {{ background: #f9fafb; }}
            .sintesis-box {{
                margin-top: 18px;
                padding: 12px 14px;
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-left: 4px solid #0b3c6d;
                border-radius: 6px;
                font-size: 12.5px;
                line-height: 1.5;
            }}
            .no-print {{ text-align: right; margin-bottom: 12px; }}
            .btn-print {{
                background: #0b3c6d;
                color: white;
                border: none;
                padding: 9px 18px;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
            }}
            @media print {{
                .no-print {{ display: none; }}
                body {{ margin: 0; padding: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn-print" onclick="window.print()">🖨️ Imprimir Reporte / Guardar PDF</button>
        </div>

        <div class="header">
            <div>
                <h2>MUNICIPALIDAD DE SAN SALVADOR DE JUJUY</h2>
                <p>Dirección de Cómputos · Informe Ejecutivo de Soporte Técnico IT y Patrimonio</p>
            </div>
            <div style="text-align: right; font-size: 12px;">
                <strong>Fecha de Emisión:</strong><br>{kpis['fecha_emision']}
            </div>
        </div>

        <div class="filtros"><strong>Parámetros del Reporte:</strong> {filtros_texto}</div>

        <div class="kpis">
            <div class="kpi-card"><span>Total Incidentes</span><strong>{kpis['total']}</strong></div>
            <div class="kpi-card"><span>Resueltos</span><strong>{kpis['resueltos']}</strong></div>
            <div class="kpi-card"><span>En Proceso / Abiertos</span><strong>{kpis['pendientes']}</strong></div>
            <div class="kpi-card"><span>Tasa Resolución</span><strong>{kpis['tasa']}</strong></div>
            <div class="kpi-card"><span>Tiempo Medio (MTTR)</span><strong>{kpis['mttr']}</strong></div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>N° Ticket</th>
                    <th>Fecha</th>
                    <th>Elemento</th>
                    <th>Secretaría</th>
                    <th>Categoría</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th>Técnico</th>
                </tr>
            </thead>
            <tbody>
                {filas_html}
            </tbody>
        </table>

        <div class="sintesis-box">
            <strong style="color: #0b3c6d;">Conclusiones y Proyección Técnica:</strong><br>{sintesis}
        </div>
    </body>
    </html>
    """

df_tickets, df_historial_all, df_elementos_all = cargar_tablas()

st.subheader("📊 Estadísticas, Proyecciones y Generación de Reportes")

if len(df_tickets) == 0:
    st.info("No hay suficientes datos registrados para generar estadísticas o reportes.")
    st.stop()

df_tickets["dt_creacion"] = pd.to_datetime(df_tickets["fecha_creacion"], errors="coerce")
total_tk = len(df_tickets)
resueltos_tk = len(df_tickets[df_tickets["estado"] == "Resuelto"])
tasa_resolucion = (resueltos_tk / total_tk) * 100

df_hist_dt = df_historial_all.copy()
df_hist_dt["dt"] = pd.to_datetime(df_hist_dt["fecha_hora"], errors="coerce")

creaciones = df_hist_dt[df_hist_dt["tipo_evento"] == "Creación"].groupby("numero_ticket")["dt"].min()
resoluciones = df_hist_dt[df_hist_dt["tipo_evento"].str.contains("Resolu|Resuelto", case=False, na=False)].groupby("numero_ticket")["dt"].max()

df_sla = pd.DataFrame({"inicio": creaciones, "fin": resoluciones}).dropna()
if len(df_sla) > 0:
    df_sla["minutos_resolucion"] = (df_sla["fin"] - df_sla["inicio"]).dt.total_seconds() / 60.0
    df_sla = df_sla[df_sla["minutos_resolucion"] >= 0]
    mttr_min = df_sla["minutos_resolucion"].mean()
    mttr_texto = f"{mttr_min:.1f} min" if mttr_min < 120 else f"{mttr_min / 60:.1f} hs"
else:
    mttr_texto = "Sin datos"

top_equipo_serie = df_tickets["codigo_elemento"].value_counts()
equipo_critico = f"{top_equipo_serie.index[0]} ({top_equipo_serie.iloc[0]} fallas)"

top_sec_serie = df_tickets["secretaria"].value_counts()
sec_mayor_demanda = f"{top_sec_serie.index[0]} ({top_sec_serie.iloc[0]})"

k1, k2, k3, k4 = st.columns(4)
k1.metric("Tasa de Resolución", f"{tasa_resolucion:.1f}%", f"{resueltos_tk} de {total_tk} cerrados")
k2.metric("Tiempo Medio Resolución", mttr_texto)
k3.metric("Activo Más Reincidente", equipo_critico)
k4.metric("Área Mayor Demanda", sec_mayor_demanda)

st.divider()

# ==============================================================================
# BLOQUE 1: VISUALIZACIONES GRÁFICAS VARIADAS (ALTAIR)
# ==============================================================================
st.markdown("### 📈 Análisis Visual de la Gestión")

g1, g2 = st.columns([1.15, 1])

with g1:
    with st.container(border=True):
        st.markdown("#### Incidentes por Secretaría y Estado (Barras Apiladas)")
        df_sec_est = df_tickets.groupby(["secretaria", "estado"]).size().reset_index(name="Cantidad")
        chart_sec = (
            alt.Chart(df_sec_est)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                y=alt.Y("secretaria:N", sort="-x", title=None),
                x=alt.X("Cantidad:Q", title="Cantidad de Tickets"),
                color=alt.Color(
                    "estado:N",
                    title="Estado",
                    scale=alt.Scale(
                        domain=["Resuelto", "En Proceso", "Abierto"],
                        range=["#10b981", "#f59e0b", "#ef4444"]
                    )
                ),
                tooltip=["secretaria", "estado", "Cantidad"]
            )
            .properties(height=300)
        )
        st.altair_chart(chart_sec, use_container_width=True)

with g2:
    with st.container(border=True):
        st.markdown("#### Proporción por Categoría de Falla (Gráfico de Anillo)")
        df_cat = df_tickets["categoria"].value_counts().reset_index()
        df_cat.columns = ["Categoría", "Cantidad"]
        chart_dona = (
            alt.Chart(df_cat)
            .mark_arc(innerRadius=65, outerRadius=115, padAngle=0.03)
            .encode(
                theta=alt.Theta(field="Cantidad", type="quantitative"),
                color=alt.Color(field="Categoría", type="nominal", legend=alt.Legend(orient="bottom")),
                tooltip=["Categoría", "Cantidad"]
            )
            .properties(height=300)
        )
        st.altair_chart(chart_dona, use_container_width=True)

g3, g4 = st.columns(2)

with g3:
    with st.container(border=True):
        st.markdown("#### Evolución Temporal de Demanda (Gráfico de Área)")
        df_temp = df_tickets.dropna(subset=["dt_creacion"]).copy()
        df_temp["Mes"] = df_temp["dt_creacion"].dt.to_period("M").astype(str)
        df_mes = df_temp.groupby("Mes").size().reset_index(name="Tickets")

        chart_area = (
            alt.Chart(df_mes)
            .mark_area(
                line={"color": "#38bdf8", "strokeWidth": 3},
                color=alt.Gradient(
                    gradient="linear",
                    stops=[
                        alt.GradientStop(color="rgba(56, 189, 248, 0.45)", offset=0),
                        alt.GradientStop(color="rgba(56, 189, 248, 0.02)", offset=1),
                    ],
                    x1=1, x2=1, y1=1, y2=0
                ),
                point=alt.OverlayMarkDef(color="#38bdf8", size=70)
            )
            .encode(
                x=alt.X("Mes:N", title="Período Mensual"),
                y=alt.Y("Tickets:Q", title="Tickets Ingresados"),
                tooltip=["Mes", "Tickets"]
            )
            .properties(height=270)
        )
        st.altair_chart(chart_area, use_container_width=True)

with g4:
    with st.container(border=True):
        st.markdown("#### Distribución por Prioridad y Origen del Ticket")
        col_orig = "origen_ticket" if "origen_ticket" in df_tickets.columns else "estado"
        df_prio = df_tickets.groupby(["prioridad", col_orig]).size().reset_index(name="Tickets")
        chart_prio = (
            alt.Chart(df_prio)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X("prioridad:N", sort=["Baja", "Media", "Alta", "Crítica"], title="Prioridad"),
                y=alt.Y("Tickets:Q", title="Cantidad"),
                xOffset=f"{col_orig}:N",
                color=alt.Color(f"{col_orig}:N", title="Canal / Origen"),
                tooltip=["prioridad", col_orig, "Tickets"]
            )
            .properties(height=270)
        )
        st.altair_chart(chart_prio, use_container_width=True)

st.divider()

# ==============================================================================
# BLOQUE 2: PROYECCIONES PREDICTIVAS E INFORME DE RIESGO PATRIMONIAL
# ==============================================================================
st.markdown("### 🔮 Proyecciones de Demanda y Mantenimiento Predictivo")
st.caption("Modelado estadístico basado en el histórico de incidentes y frecuencia de fallas por activo.")

agg_tickets = df_tickets.groupby("codigo_elemento").agg(
    total_tickets=("numero_ticket", "count"),
    tickets_abiertos=("estado", lambda x: (x != "Resuelto").sum()),
    ultima_falla=("fecha_creacion", "max")
).reset_index()

agg_hist = df_historial_all.groupby("codigo_elemento").agg(
    total_intervenciones=("id", "count")
).reset_index()

df_ranking_activos = (
    df_elementos_all
    .merge(agg_tickets, on="codigo_elemento", how="left")
    .merge(agg_hist, on="codigo_elemento", how="left")
    .fillna({"total_tickets": 0, "tickets_abiertos": 0, "total_intervenciones": 0, "ultima_falla": "Sin registros"})
)
df_ranking_activos["total_tickets"] = df_ranking_activos["total_tickets"].astype(int)
df_ranking_activos["tickets_abiertos"] = df_ranking_activos["tickets_abiertos"].astype(int)
df_ranking_activos["total_intervenciones"] = df_ranking_activos["total_intervenciones"].astype(int)
df_ranking_activos = df_ranking_activos.sort_values(by=["total_tickets", "total_intervenciones"], ascending=False)

col_proy1, col_proy2 = st.columns([1.2, 1])

with col_proy1:
    with st.container(border=True):
        st.markdown("#### 📈 Proyección de Tickets (Próximos 3 Meses)")
        df_serie = df_tickets.dropna(subset=["dt_creacion"]).copy()
        df_serie["Mes_Period"] = df_serie["dt_creacion"].dt.to_period("M")
        conteo_mensual = df_serie.groupby("Mes_Period").size().sort_index()

        if len(conteo_mensual) >= 2:
            x = np.arange(len(conteo_mensual))
            y = conteo_mensual.values
            pendiente, intercepto = np.polyfit(x, y, 1)

            ultimo_periodo = conteo_mensual.index[-1]
            datos_proyeccion = []

            for per, val in conteo_mensual.items():
                datos_proyeccion.append({
                    "Período": str(per),
                    "Tickets": float(val),
                    "Tipo": "Histórico Real"
                })

            for step in range(1, 4):
                futuro_per = ultimo_periodo + step
                prediccion = max(0.0, round(pendiente * (len(conteo_mensual) - 1 + step) + intercepto, 1))
                datos_proyeccion.append({
                    "Período": str(futuro_per),
                    "Tickets": prediccion,
                    "Tipo": "Proyección Estimada"
                })

            df_proy_chart = pd.DataFrame(datos_proyeccion)

            chart_proy = (
                alt.Chart(df_proy_chart)
                .mark_line(point=alt.OverlayMarkDef(size=80), strokeWidth=3)
                .encode(
                    x=alt.X("Período:N", title="Mes"),
                    y=alt.Y("Tickets:Q", title="Cantidad de Tickets"),
                    color=alt.Color(
                        "Tipo:N",
                        scale=alt.Scale(
                            domain=["Histórico Real", "Proyección Estimada"],
                            range=["#38bdf8", "#f59e0b"]
                        )
                    ),
                    strokeDash=alt.StrokeDash(
                        "Tipo:N",
                        scale=alt.Scale(
                            domain=["Histórico Real", "Proyección Estimada"],
                            range=[[1, 0], [6, 4]]
                        )
                    ),
                    tooltip=["Período", "Tipo", "Tickets"]
                )
                .properties(height=270)
            )
            st.altair_chart(chart_proy, use_container_width=True)

            tendencia_txt = "al alza 📈" if pendiente > 0.1 else ("a la baja 📉" if pendiente < -0.1 else "estable ➖")
            st.info(f"**Tendencia detectada:** La demanda mensual muestra un comportamiento **{tendencia_txt}** (pendiente: `{pendiente:+.2f}` tickets/mes).")
        else:
            st.warning("Se necesitan registros en al menos 2 meses distintos para proyectar tendencia.")

with col_proy2:
    with st.container(border=True):
        st.markdown("#### ⚠️ Score de Riesgo y Recomendación de Recambio")
        df_riesgo = df_ranking_activos.copy()
        df_riesgo["Score_Riesgo"] = ((df_riesgo["total_tickets"] * 25) + (df_riesgo["tickets_abiertos"] * 30)).clip(upper=100)

        def clasificar_accion(score):
            if score >= 75:
                return "🔴 Crítico — Recambio inmediato"
            elif score >= 45:
                return "🟡 Medio — Mantenimiento preventivo"
            return "🟢 Bajo — Operación normal"

        df_riesgo["Diagnóstico"] = df_riesgo["Score_Riesgo"].apply(clasificar_accion)
        st.dataframe(
            df_riesgo[["codigo_elemento", "tipo", "total_tickets", "Score_Riesgo", "Diagnóstico"]],
            use_container_width=True,
            hide_index=True
        )

activos_criticos = df_riesgo[df_riesgo["Score_Riesgo"] >= 75]["codigo_elemento"].tolist()
txt_criticos = ", ".join(activos_criticos) if activos_criticos else "ninguno por el momento"
pendientes_totales = len(df_tickets[df_tickets["estado"] != "Resuelto"])

sintesis_texto = (
    f"Al día {datetime.now().strftime('%d/%m/%Y')}, la Dirección de Cómputos registra un total de {total_tk} incidentes, "
    f"con una efectividad de cierre del {tasa_resolucion:.1f}% y un tiempo medio de resolución de {mttr_texto}. "
    f"La mayor demanda operativa proviene de {top_sec_serie.index[0]} ({top_sec_serie.iloc[0]} tickets). "
    f"Actualmente existen {pendientes_totales} tickets pendientes en cola y se sugiere priorizar auditoría o recambio "
    f"sobre los activos patrimoniales de alta reincidencia: {txt_criticos}."
)

with st.container(border=True):
    st.markdown("#### 📝 Síntesis Ejecutiva Automática")
    st.write(sintesis_texto)

st.divider()

# ==============================================================================
# BLOQUE 3: GENERADOR DE REPORTES EJECUTIVOS (CSV / PDF IMPRIMIBLE)
# ==============================================================================
st.markdown("### 📑 Generador de Reportes Ejecutivos")
st.caption("Filtrá la información para emitir un informe oficial imprimible o descargar la planilla de datos.")

with st.container(border=True):
    f1, f2, f3, f4 = st.columns(4)

    fecha_min_db = df_tickets["dt_creacion"].min().date() if df_tickets["dt_creacion"].notna().any() else datetime.now().date()
    fecha_max_db = df_tickets["dt_creacion"].max().date() if df_tickets["dt_creacion"].notna().any() else datetime.now().date()

    with f1:
        fecha_desde = st.date_input("Desde fecha", value=fecha_min_db)
    with f2:
        fecha_hasta = st.date_input("Hasta fecha", value=fecha_max_db)
    with f3:
        rep_sec = st.selectbox("Secretaría", ["Todas"] + sorted(df_tickets["secretaria"].unique().tolist()), key="rep_sec")
    with f4:
        rep_est = st.selectbox("Estado", ["Todos", "Abierto", "En Proceso", "Resuelto"], key="rep_est")

    df_reporte = df_tickets.copy()
    if df_reporte["dt_creacion"].notna().any():
        df_reporte = df_reporte[
            (df_reporte["dt_creacion"].dt.date >= fecha_desde) &
            (df_reporte["dt_creacion"].dt.date <= fecha_hasta)
        ]
    if rep_sec != "Todas":
        df_reporte = df_reporte[df_reporte["secretaria"] == rep_sec]
    if rep_est != "Todos":
        df_reporte = df_reporte[df_reporte["estado"] == rep_est]

    st.write(f"**Registros incluidos en el reporte:** `{len(df_reporte)}` tickets")

    if len(df_reporte) > 0:
        cols_rep = [
            "numero_ticket", "fecha_creacion", "codigo_elemento", "secretaria",
            "oficina", "categoria", "prioridad", "estado", "tecnico_asignado"
        ]
        st.dataframe(df_reporte[cols_rep], use_container_width=True, hide_index=True)

        rep_resueltos = len(df_reporte[df_reporte["estado"] == "Resuelto"])
        rep_pendientes = len(df_reporte[df_reporte["estado"] != "Resuelto"])
        rep_tasa = f"{(rep_resueltos / len(df_reporte)) * 100:.1f}%"

        kpis_rep = {
            "fecha_emision": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total": len(df_reporte),
            "resueltos": rep_resueltos,
            "pendientes": rep_pendientes,
            "tasa": rep_tasa,
            "mttr": mttr_texto
        }
        filtros_desc = f"Período: {fecha_desde.strftime('%d/%m/%Y')} al {fecha_hasta.strftime('%d/%m/%Y')} | Secretaría: {rep_sec} | Estado: {rep_est}"
        html_reporte = construir_html_reporte(df_reporte, filtros_desc, kpis_rep, sintesis_texto)

        b1, b2, b3 = st.columns([1.2, 1.2, 1.4])
        with b1:
            csv_rep = df_reporte.drop(columns=["dt_creacion"]).to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📥 Descargar Reporte en CSV (Excel)",
                data=csv_rep,
                file_name=f"Reporte_Tickets_SSJ_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with b2:
            st.download_button(
                label="📄 Descargar Informe Oficial (HTML/PDF)",
                data=html_reporte.encode("utf-8"),
                file_name=f"Informe_Ejecutivo_SSJ_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )
        with b3:
            mostrar_vista_previa = st.toggle("👁️ Ver Vista Previa Imprimible del Informe")

        if mostrar_vista_previa:
            components.html(html_reporte, height=620, scrolling=True)
    else:
        st.warning("No hay tickets que coincidan con los filtros seleccionados para el reporte.")