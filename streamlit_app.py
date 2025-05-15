import Definitions
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="MaxEnt Probabilidad", page_icon="🧠")

st.title("🧠 Visualización Modelo MaxEnt")

with st.expander("ℹ️ Instrucciones"):
    st.markdown("""
    - Sube un archivo `.gpkg` o `.csv` que contenga los datos espaciales o tabulares.
    - Si el archivo contiene una columna llamada `probabilidad`, se mostrará sobre el mapa con escala de color.
    """)

with st.form(key="form_carga_datos"):

    uploaded_file = st.file_uploader(
        "📂 Sube tu archivo GPKG o CSV", accept_multiple_files=False, type=["gpkg", "csv"]
    )

    submit_button = st.form_submit_button(label="Cargar datos")

    if submit_button and uploaded_file is not None:
        st.success("✅ Archivo cargado correctamente")
        st.write(f"Nombre del archivo: `{uploaded_file.name}`")

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.write("Vista previa del archivo CSV:")
            st.dataframe(df.head())

        elif uploaded_file.name.endswith(".gpkg"):
            try:
                gdf = gpd.read_file(uploaded_file)
                st.write("Vista previa del archivo GPKG:")
                st.dataframe(gdf.head())

                # Filtrar geometrías válidas
                gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty]

                # Calcular centro del mapa como el centro del bounds
                bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
                center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]  # [lat, lon]

                mapa = folium.Map(location=center, zoom_start=10)

                # Escala de color
                if "probabilidad" in gdf.columns and gdf.geometry.geom_type.isin(["Point"]).all():
                    from branca.colormap import linear
                    colormap = linear.Viridis_09.scale(gdf["probabilidad"].min(), gdf["probabilidad"].max())
                    colormap.caption = "Probabilidad"
                    colormap.add_to(mapa)

                    for _, row in gdf.iterrows():
                        folium.CircleMarker(
                            location=[row.geometry.y, row.geometry.x],
                            radius=5,
                            fill=True,
                            fill_color=colormap(row["probabilidad"]),
                            color=None,
                            fill_opacity=0.8,
                            popup=f"Probabilidad: {row['probabilidad']:.2f}"
                        ).add_to(mapa)
                else:
                    folium.GeoJson(gdf).add_to(mapa)

                st.markdown("🗺️ Mapa interactivo")
                st_folium(mapa, width=1200, height=600)

            except Exception as e:
                st.error(f"❌ Error leyendo GPKG: {e}")
        else:
            st.error("Formato de archivo no soportado. Usa GPKG o CSV.")
