import streamlit as st

def aplicar_estilos_web():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display: none !important;}

        /* Barra superior de navegación (st.navigation) integrada con la paleta institucional */
        header[data-testid="stHeader"] {
            background-color: #092c50 !important;
            border-bottom: 1px solid #1e40af;
        }
        header[data-testid="stHeader"] * {
            background-color: transparent !important;
            color: #f8fafc !important;
        }
        header[data-testid="stHeader"] a {
            padding: 0.35rem 0.75rem !important;
            border-radius: 6px !important;
            transition: background-color 0.2s ease;
        }
        header[data-testid="stHeader"] a:hover {
            background-color: rgba(255, 255, 255, 0.14) !important;
        }
        header[data-testid="stHeader"] a[aria-current="page"] {
            background-color: #1d4ed8 !important;
            border-bottom: 2px solid #f59e0b !important;
            font-weight: 700 !important;
        }

        /* Contenedor principal */
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 3rem;
            max-width: 1380px;
        }

        /* Cabecera institucional */
        .muni-header {
            background: linear-gradient(135deg, #092c50 0%, #0b3c6d 55%, #16599c 100%);
            padding: 1.25rem 1.8rem;
            border-radius: 12px;
            color: #ffffff;
            margin-bottom: 1.1rem;
            border-bottom: 4px solid #f59e0b;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .muni-header h1, .muni-header p, .muni-header div {
            background: transparent !important;
        }
        .muni-header h1 {
            margin: 0;
            font-size: 1.48rem;
            font-weight: 700;
            color: #ffffff !important;
        }
        .muni-header p {
            margin: 0.25rem 0 0 0;
            font-size: 0.87rem;
            color: #dbeafe !important;
        }
        .muni-badge {
            background: rgba(255, 255, 255, 0.14) !important;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.84rem;
            font-weight: 600;
            color: #ffffff !important;
        }

        /* Tarjetas KPI reales de Streamlit (stMetric) */
        div[data-testid="stMetric"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-left: 5px solid #38bdf8;
            padding: 1rem 1.2rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        div[data-testid="stMetric"] label {
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }

        /* Tarjetas con borde */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #161b22;
            border: 1px solid #30363d !important;
            border-radius: 10px !important;
            padding: 0.4rem;
        }

        /* Barras de sección estilo osTicket SCP */
        .scp-section-bar {
            background: linear-gradient(90deg, #0b3c6d 0%, #1e3a8a 100%);
            border-left: 5px solid #f59e0b;
            color: #ffffff;
            padding: 0.55rem 0.95rem;
            font-weight: 600;
            font-size: 0.92rem;
            border-radius: 6px;
            margin: 0.8rem 0 0.9rem 0;
        }

        /* Botones primarios */
        button[kind="primary"] {
            background: linear-gradient(135deg, #1d4ed8 0%, #0b3c6d 100%) !important;
            border: 1px solid #3b82f6 !important;
            border-radius: 7px !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }

        /* Pie de página */
        .muni-footer {
            margin-top: 3rem;
            padding: 1rem;
            border-top: 1px solid #30363d;
            text-align: center;
            font-size: 0.82rem;
            color: #8b949e;
        }
        </style>
    """, unsafe_allow_html=True)

def render_cabecera_web(user: dict):
    st.markdown(f"""
        <div class="muni-header">
            <div>
                <h1>🏛️ Soporte Técnico IT — Municipalidad de San Salvador de Jujuy</h1>
                <p>Panel de Control de Agentes (SCP) · Mesa de Ayuda y Trazabilidad Patrimonial</p>
            </div>
            <div class="muni-badge">
                👤 {user['nombre_completo']} &nbsp;|&nbsp; {user['rol']} · {user['area']}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_pie_web():
    st.markdown("""
        <div class="muni-footer">
            Municipalidad de San Salvador de Jujuy · Dirección de Cómputos · Sistema Integrado de Tickets y Patrimonio (MuniDesk SSJ)
        </div>
    """, unsafe_allow_html=True)

def generar_html_impresion_ticket(ticket: dict) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Comprobante {ticket['numero_ticket']} - Soporte SSJ</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #111827;
                max-width: 740px;
                margin: 15px auto;
                padding: 22px;
                border: 2px solid #0b3c6d;
                border-radius: 8px;
                background: #ffffff;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #0b3c6d;
                padding-bottom: 10px;
                margin-bottom: 14px;
            }}
            .header h2 {{ margin: 0; color: #0b3c6d; font-size: 17px; }}
            .header p {{ margin: 2px 0 0 0; font-size: 12px; color: #4b5563; }}
            .nro-box {{
                background: #0b3c6d;
                color: #ffffff;
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 14px;
                font-size: 13px;
            }}
            td {{
                border: 1px solid #d1d5db;
                padding: 7px 10px;
            }}
            td.label {{
                background: #f3f4f6;
                font-weight: 600;
                width: 24%;
                color: #1f2937;
            }}
            .desc-box {{
                border: 1px solid #d1d5db;
                background: #f9fafb;
                padding: 12px;
                border-radius: 6px;
                font-size: 13px;
                min-height: 65px;
                margin-bottom: 24px;
            }}
            .firmas {{
                display: flex;
                justify-content: space-between;
                margin-top: 40px;
                text-align: center;
                font-size: 12px;
            }}
            .firma-linea {{
                width: 42%;
                border-top: 1px solid #374151;
                padding-top: 6px;
            }}
            .no-print {{
                text-align: center;
                margin-bottom: 14px;
            }}
            .btn-print {{
                background: #0b3c6d;
                color: white;
                border: none;
                padding: 9px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                cursor: pointer;
            }}
            @media print {{
                .no-print {{ display: none; }}
                body {{ border: none; margin: 0; padding: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="no-print">
            <button class="btn-print" onclick="window.print()">🖨️ Imprimir Ticket / Guardar como PDF</button>
        </div>

        <div class="header">
            <div>
                <h2>MUNICIPALIDAD DE SAN SALVADOR DE JUJUY</h2>
                <p>Dirección de Cómputos · Comprobante de Apertura de Ticket IT</p>
            </div>
            <div class="nro-box">{ticket['numero_ticket']}</div>
        </div>

        <table>
            <tr>
                <td class="label">Fecha y Hora:</td>
                <td>{ticket['fecha_creacion']}</td>
                <td class="label">Origen:</td>
                <td>{ticket.get('origen_ticket', 'Presencial')}</td>
            </tr>
            <tr>
                <td class="label">Cód. Elemento:</td>
                <td><strong>{ticket['codigo_elemento']}</strong></td>
                <td class="label">Prioridad:</td>
                <td><strong>{ticket['prioridad']}</strong></td>
            </tr>
            <tr>
                <td class="label">Tema de Ayuda:</td>
                <td>{ticket['categoria']}</td>
                <td class="label">Estado Inicial:</td>
                <td>{ticket.get('estado', 'Abierto')}</td>
            </tr>
            <tr>
                <td class="label">Secretaría / Área:</td>
                <td colspan="3">{ticket['secretaria']} — {ticket['oficina']}</td>
            </tr>
            <tr>
                <td class="label">Agente Solicitante:</td>
                <td>{ticket['solicitante']}</td>
                <td class="label">Técnico Asignado:</td>
                <td>{ticket['tecnico_asignado']}</td>
            </tr>
            <tr>
                <td class="label">Asunto:</td>
                <td colspan="3"><strong>{ticket.get('asunto', 'Incidente Técnico')}</strong></td>
            </tr>
        </table>

        <div style="font-size: 13px; font-weight: 600; margin-bottom: 5px;">Resumen del Problema / Falla Reportada:</div>
        <div class="desc-box">{ticket['descripcion']}</div>

        <div class="firmas">
            <div class="firma-linea">Firma y Aclaración del Solicitante<br>({ticket['solicitante']})</div>
            <div class="firma-linea">Recepción / Conformidad Técnica IT<br>Dirección de Cómputos</div>
        </div>
    </body>
    </html>
    """

def generar_html_reporte_ejecutivo(df_rep, filtros_texto: str, kpis: dict, sintesis: str = "") -> str:
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

    bloque_sintesis = ""
    if sintesis:
        bloque_sintesis = f"""
        <div style="margin-top: 18px; padding: 12px 14px; background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #0b3c6d; border-radius: 6px; font-size: 12.5px;">
            <strong style="color: #0b3c6d;">Conclusiones y Proyección Técnica:</strong><br>{sintesis}
        </div>
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
                background: #ffffff;
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

        {bloque_sintesis}
    </body>
    </html>
    """
