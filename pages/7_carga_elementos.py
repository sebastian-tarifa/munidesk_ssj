import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import os
from db import get_conn, cargar_tablas

user = st.session_state.usuario_logueado
if user["rol"] not in ("Tecnico IT", "Administrador"):
    st.error("Acceso denegado. Esta sección es exclusiva para Técnicos IT y Administradores.")
    st.stop()

_, _, df_elementos_all = cargar_tablas()

st.subheader("📦 Carga y Gestión de Elementos Patrimoniales")
st.caption("Registrá nuevos equipos en el inventario municipal, actualizá su estado operativo o importá lotes desde archivos.")

# ==============================================================================
# BLOQUE 1: ALTA INDIVIDUAL DE ELEMENTO NUEVO Y ACTUALIZACIÓN DE ESTADO
# ==============================================================================
col_alta, col_edit = st.columns([1.3, 1])

with col_alta:
    with st.container(border=True):
        st.markdown("#### ➕ Alta de Nuevo Elemento Patrimonial")
        with st.form("form_alta_elemento_patrimonial", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nuevo_codigo = st.text_input(
                    "Código Patrimonial *",
                    placeholder="Ej: PC-HAC-099 o IMP-REN-201"
                ).strip().upper()

                nuevo_tipo = st.selectbox(
                    "Tipo de Elemento *",
                    [
                        "PC Escritorio",
                        "Notebook",
                        "Impresora Térmica",
                        "Impresora Láser / Multifunción",
                        "Terminal Caja / POS",
                        "Monitor",
                        "Switch / Router Red",
                        "Teléfono IP",
                        "Escáner / Lector",
                        "Servidor / UPS",
                        "Otro"
                    ]
                )
            with c2:
                nueva_marca_modelo = st.text_input(
                    "Marca y Modelo *",
                    placeholder="Ej: Dell OptiPlex 7090 i7 / Epson TM-T20III"
                ).strip()

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
                nueva_secretaria = st.selectbox("Secretaría / Dependencia Asignada *", secretarias_opciones)

            nuevo_estado_activo = st.selectbox(
                "Estado Inicial del Activo *",
                ["Operativo", "Operativo con observación", "En reparación", "Baja patrimonial"]
            )

            btn_guardar_elem = st.form_submit_button("💾 Registrar Elemento en Inventario", type="primary", use_container_width=True)

            if btn_guardar_elem:
                if not nuevo_codigo or not nueva_marca_modelo:
                    st.error("Completá el Código Patrimonial y la Marca/Modelo.")
                elif nuevo_codigo in df_elementos_all["codigo_elemento"].values:
                    st.error(f"El código patrimonial `{nuevo_codigo}` ya existe en la base de datos.")
                else:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(
                        """INSERT INTO elementos (codigo_elemento, tipo, marca_modelo, secretaria, estado_activo)
                           VALUES (?, ?, ?, ?, ?)""",
                        (nuevo_codigo, nuevo_tipo, nueva_marca_modelo, nueva_secretaria, nuevo_estado_activo)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Elemento **`{nuevo_codigo}`** ({nuevo_tipo} - {nueva_marca_modelo}) registrado correctamente.")
                    st.rerun()

with col_edit:
    with st.container(border=True):
        st.markdown("#### ✏️ Actualizar Ubicación o Estado de Activo")
        if len(df_elementos_all) == 0:
            st.info("Aún no hay elementos cargados.")
        else:
            cod_sel = st.selectbox(
                "Seleccioná un código patrimonial:",
                df_elementos_all["codigo_elemento"].tolist(),
                key="sel_edit_elemento"
            )
            datos_eq = df_elementos_all[df_elementos_all["codigo_elemento"] == cod_sel].iloc[0]

            with st.form("form_editar_elemento"):
                edit_modelo = st.text_input("Marca y Modelo", value=datos_eq["marca_modelo"])
                edit_sec = st.text_input("Secretaría / Área", value=datos_eq["secretaria"])
                estados_lista = ["Operativo", "Operativo con observación", "En reparación", "Baja patrimonial"]
                idx_est = estados_lista.index(datos_eq["estado_activo"]) if datos_eq["estado_activo"] in estados_lista else 0
                edit_estado = st.selectbox("Estado Operativo", estados_lista, index=idx_est)

                btn_upd_elem = st.form_submit_button("Guardar Cambios del Equipo", use_container_width=True)
                if btn_upd_elem:
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(
                        """UPDATE elementos
                           SET marca_modelo = ?, secretaria = ?, estado_activo = ?
                           WHERE codigo_elemento = ?""",
                        (edit_modelo.strip(), edit_sec.strip(), edit_estado, cod_sel)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Datos de `{cod_sel}` actualizados.")
                    st.rerun()

st.divider()

# ==============================================================================
# BLOQUE 2: IMPORTACIÓN MASIVA DESDE ARCHIVO (CSV / EXCEL / SQLITE)
# ==============================================================================
with st.expander("📥 Importar Lote Masivo de Elementos Patrimoniales (CSV, Excel o SQLite)"):
    st.caption(
        "Subí una planilla o base de datos con las columnas: "
        "`codigo_elemento`, `tipo`, `marca_modelo`, `secretaria`, `estado_activo`."
    )

    c_tpl, c_mod = st.columns([1.1, 1.5])
    with c_tpl:
        plantilla_df = pd.DataFrame([
            {
                "codigo_elemento": "PC-HAC-101",
                "tipo": "PC Escritorio",
                "marca_modelo": "HP ProDesk 400 G9 i5",
                "secretaria": "Secretaría de Hacienda",
                "estado_activo": "Operativo"
            },
            {
                "codigo_elemento": "IMP-REN-205",
                "tipo": "Impresora Láser",
                "marca_modelo": "Brother HL-L2370DN",
                "secretaria": "Dirección General de Rentas",
                "estado_activo": "Operativo"
            }
        ])
        st.download_button(
            label="📄 Descargar Plantilla Modelo (.csv)",
            data=plantilla_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="plantilla_elementos_patrimoniales_ssj.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c_mod:
        modo_imp = st.radio(
            "Si el código ya existe:",
            ["Omitir existentes (solo agregar nuevos)", "Actualizar existentes con los datos del archivo"],
            horizontal=True
        )

    arch_subido = st.file_uploader(
        "Seleccioná archivo (.csv, .xlsx, .xls, .db, .sqlite)",
        type=["csv", "xlsx", "xls", "db", "sqlite"],
        key="uploader_carga_elementos"
    )

    if arch_subido is not None:
        nom = arch_subido.name.lower()
        df_imp = None
        try:
            if nom.endswith(".csv"):
                try:
                    df_imp = pd.read_csv(arch_subido, sep=None, engine="python", encoding="utf-8-sig")
                except UnicodeDecodeError:
                    arch_subido.seek(0)
                    df_imp = pd.read_csv(arch_subido, sep=None, engine="python", encoding="latin-1")
            elif nom.endswith((".xlsx", ".xls")):
                df_imp = pd.read_excel(arch_subido)
            elif nom.endswith((".db", ".sqlite")):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                    tmp.write(arch_subido.getbuffer())
                    tmp_path = tmp.name
                try:
                    c_ext = sqlite3.connect(tmp_path)
                    cur_ext = c_ext.cursor()
                    cur_ext.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tablas_ext = [t[0] for t in cur_ext.fetchall()]
                    if tablas_ext:
                        idx_def = tablas_ext.index("elementos") if "elementos" in tablas_ext else 0
                        t_sel = st.selectbox("Tabla a importar:", tablas_ext, index=idx_def)
                        df_imp = pd.read_sql_query(f"SELECT * FROM [{t_sel}]", c_ext)
                    c_ext.close()
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

            if df_imp is not None:
                df_imp.columns = [str(c).strip().lower() for c in df_imp.columns]
                req = {"codigo_elemento", "tipo", "marca_modelo", "secretaria", "estado_activo"}
                faltan = req - set(df_imp.columns)
                if faltan:
                    st.error(f"Faltan columnas obligatorias: `{', '.join(sorted(faltan))}`")
                else:
                    df_clean = df_imp[list(req)].copy()
                    df_clean["codigo_elemento"] = df_clean["codigo_elemento"].astype(str).str.strip().str.upper()
                    df_clean = df_clean[df_clean["codigo_elemento"].notna() & (df_clean["codigo_elemento"] != "") & (df_clean["codigo_elemento"] != "NAN")]
                    for col in ["tipo", "marca_modelo", "secretaria", "estado_activo"]:
                        df_clean[col] = df_clean[col].fillna("Sin especificar").astype(str).str.strip()
                    df_clean = df_clean.drop_duplicates(subset=["codigo_elemento"], keep="last")

                    st.dataframe(df_clean.head(8), use_container_width=True, hide_index=True)
                    if st.button("✅ Importar Lote Ahora", type="primary", use_container_width=True):
                        conn = get_conn()
                        cur = conn.cursor()
                        regs = [
                            (r["codigo_elemento"], r["tipo"], r["marca_modelo"], r["secretaria"], r["estado_activo"])
                            for _, r in df_clean.iterrows()
                        ]
                        sql_cmd = (
                            "INSERT OR IGNORE INTO elementos VALUES (?, ?, ?, ?, ?)"
                            if modo_imp.startswith("Omitir")
                            else "INSERT OR REPLACE INTO elementos VALUES (?, ?, ?, ?, ?)"
                        )
                        cur.executemany(sql_cmd, regs)
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Se procesaron **{len(regs)}** elementos patrimoniales.")
                        st.rerun()
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

# ==============================================================================
# BLOQUE 3: LISTADO COMPLETO DEL INVENTARIO PATRIMONIAL
# ==============================================================================
st.markdown(f"#### 📋 Inventario Patrimonial Registrado ({len(df_elementos_all)} equipos)")

f_busq, f_sec = st.columns([2, 1.2])
with f_busq:
    filtro_eq = st.text_input("Filtrar inventario por código, tipo o modelo:", placeholder="Ej: Dell, Epson, PAT-HAC...").strip()
with f_sec:
    sec_opts = ["Todas"] + sorted(df_elementos_all["secretaria"].unique().tolist())
    filtro_sec_eq = st.selectbox("Filtrar por Secretaría:", sec_opts)

df_inv_view = df_elementos_all.copy()
if filtro_eq:
    mask = df_inv_view.apply(lambda r: r.astype(str).str.contains(filtro_eq, case=False).any(), axis=1)
    df_inv_view = df_inv_view[mask]
if filtro_sec_eq != "Todas":
    df_inv_view = df_inv_view[df_inv_view["secretaria"] == filtro_sec_eq]

st.dataframe(df_inv_view, use_container_width=True, hide_index=True)