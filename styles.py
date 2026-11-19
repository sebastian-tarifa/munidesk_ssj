import streamlit as st

def aplicar_estilos_web():
    st.markdown("""
        <style>
        /* Ocultar menú estándar y pie nativo */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

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

        /* Cabecera institucional limpia (sin fondo detrás de los textos) */
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