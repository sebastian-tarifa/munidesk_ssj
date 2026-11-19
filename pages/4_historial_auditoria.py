import streamlit as st
from datetime import datetime
from db import cargar_tablas

_, df_historial_all, _ = cargar_tablas()

st.subheader("📜 Bitácora Global de Auditoría")

df_historial_global = df_historial_all.sort_values(by="id", ascending=False)[
    ["id", "fecha_hora", "numero_ticket", "codigo_elemento", "usuario", "tipo_evento", "detalle"]
]

filtro_hist = st.text_input("Filtrar historial por usuario, evento, ticket o detalle:")
if filtro_hist:
    mask = df_historial_global.apply(lambda r: r.astype(str).str.contains(filtro_hist, case=False).any(), axis=1)
    df_historial_global = df_historial_global[mask]

st.dataframe(df_historial_global, use_container_width=True, hide_index=True)

csv_data = df_historial_global.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 Descargar Auditoría en CSV (Excel)",
    data=csv_data,
    file_name=f"auditoria_tickets_ssj_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)
