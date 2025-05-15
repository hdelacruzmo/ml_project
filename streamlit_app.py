import Definitions
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from branca.colormap import linear

st.set_page_config(layout="wide", page_title="MaxEnt Probabilidad", page_icon="🧠")

st.title("🧠 Visualización Modelo MaxEnt")

with st.expander("ℹ️ Instrucciones"):
    st.markdown("""
    - Sube un archivo `.gpkg` o `.csv` que contenga los datos espaciales o tabulares.
    - Si el archivo contiene una columna llamada `probabilidad`, se mostrará sobre el mapa con escala de color.
    - Si hay muchos puntos, se mostrará solo una muestra para mejorar el rendimiento.
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

                # Coordenadas fijas definidas por el usuario
                center = [7.674, -75.067]
                mapa = folium.Map(location=center, zoom_start=4, tiles="OpenStreetMap")

                # Si es tipo punto y tiene probabilidad
                if "probabilidad" in gdf.columns and gdf.geometry.geom_type.isin(["Point"]).all():

                    # Escala de color
                    colormap = linear.Viridis_09.scale(gdf["probabilidad"].min(), gdf["probabilidad"].max())
                    colormap.caption = "Probabilidad"
                    colormap.add_to(mapa)

                    # Reducir tamaño si es muy grande
                    if len(gdf) > 500:
                        gdf_muestra = gdf.sample(n=500, random_state=42)
                        st.warning("⚠️ Mostrando solo 500 puntos por rendimiento.")
                    else:
                        gdf_muestra = gdf

                    # Crear clúster de marcadores
                    cluster = MarkerCluster().add_to(mapa)

                    for _, row in gdf_muestra.iterrows():
                        folium.CircleMarker(
                            location=[row.geometry.y, row.geometry.x],
                            radius=4,
                            fill=True,
                            fill_color=colormap(row["probabilidad"]),
                            color=None,
                            fill_opacity=0.7,
                        ).add_to(cluster)

                else:
                    # Si no es punto, simplificar geometría y agregar como GeoJson
                    gdf["geometry"] = gdf["geometry"].simplify(0.0005, preserve_topology=True)
                    folium.GeoJson(gdf).add_to(mapa)

                st.markdown("🗺️ Mapa interactivo")
                st_folium(mapa, width=1200, height=600)

            except Exception as e:
                st.error(f"❌ Error leyendo GPKG: {e}")
        else:
            st.error("Formato de archivo no soportado. Usa GPKG o CSV.")

