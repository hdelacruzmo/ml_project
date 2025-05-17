import Definitions
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import MultiPoint

st.set_page_config(layout="wide", page_title="MaxEnt - Contorno", page_icon="🧠")

st.title("🧠 Visualización de Contorno de Capa GPKG")

with st.expander("ℹ️ Instrucciones"):
    st.markdown("""
    - Sube un archivo `.gpkg` con geometrías tipo punto.
    - Se mostrará únicamente el **contorno general** (envolvente convexa) del conjunto de puntos.
    - Esto mejora el rendimiento y permite navegación fluida en el mapa.
    """)

with st.form(key="form_carga_datos"):

    uploaded_file = st.file_uploader(
        "📂 Sube tu archivo GPKG", accept_multiple_files=False, type=["gpkg"]
    )

    submit_button = st.form_submit_button(label="Cargar datos")

    if submit_button and uploaded_file is not None:
        st.success("✅ Archivo cargado correctamente")
        st.write(f"Nombre del archivo: `{uploaded_file.name}`")

        try:
            gdf = gpd.read_file(uploaded_file)
            st.write("Vista previa del archivo GPKG:")
            st.dataframe(gdf.head())

            # Filtrar geometrías válidas
            gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty]

            # Coordenadas fijas (si prefieres usar cálculo dinámico, usa total_bounds)
            center = [7.674, -75.067]
            mapa = folium.Map(location=center, zoom_start=10, tiles="OpenStreetMap")

            # Construir envolvente convexa del conjunto de puntos
            puntos = gdf.geometry.values
            contorno = MultiPoint(puntos).convex_hull
            gdf_contorno = gpd.GeoDataFrame(geometry=[contorno], crs=gdf.crs)

            # Agregar el contorno como capa GeoJson
            folium.GeoJson(gdf_contorno, name="Contorno", tooltip="Contorno de puntos").add_to(mapa)

            # Mostrar en Streamlit
            st.markdown("🗺️ Contorno del conjunto de puntos")
            st_folium(mapa, width=1200, height=600)

        except Exception as e:
            st.error(f"❌ Error procesando el archivo: {e}")
    elif submit_button:
        st.warning("Por favor selecciona un archivo .gpkg para continuar.")
