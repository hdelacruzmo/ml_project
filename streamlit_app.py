import Definitions
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Polygon
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="MaxEnt Bounding Box", page_icon="🧠")

st.title("🧠 Área Aproximada del Archivo Cargado")

with st.expander("ℹ️ Instrucciones"):
    st.markdown("""
    - Esta visualización muestra un polígono rectangular que representa el área cubierta por los datos del archivo `.gpkg` cargado.
    - No se cargan puntos ni polígonos pesados, lo que mejora notablemente el rendimiento.
    """)

with st.form(key="form_carga_datos"):

    uploaded_file = st.file_uploader(
        "📂 Sube tu archivo GPKG", accept_multiple_files=False, type=["gpkg"]
    )

    submit_button = st.form_submit_button(label="Cargar archivo")

    if submit_button and uploaded_file is not None:
        try:
            gdf = gpd.read_file(uploaded_file)

            # Reproyectar de EPSG:9377 a EPSG:4326 si es necesario
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                st.info(f"📐 Reproyectando desde {gdf.crs} a EPSG:4326 para visualización.")
                gdf = gdf.to_crs(epsg=4326)
    
            st.write("Vista previa del archivo:")
            st.dataframe(gdf.head())

            # Asegurarse de trabajar solo con geometrías válidas
            gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty]

            # Extraer límites del bounding box
            bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
            minx, miny, maxx, maxy = bounds

            # Crear polígono rectangular (bounding box)
            rectangle = Polygon([
                (minx, miny),
                (minx, maxy),
                (maxx, maxy),
                (maxx, miny),
                (minx, miny)
            ])
            gdf_rect = gpd.GeoDataFrame(geometry=[rectangle], crs=gdf.crs)

            # Calcular centro aproximado para el mapa
            center = [(miny + maxy) / 2, (minx + maxx) / 2]

            # Crear mapa y agregar rectángulo
            mapa = folium.Map(location=center, zoom_start=10, tiles="OpenStreetMap")
            folium.GeoJson(gdf_rect, name="Bounding Box", tooltip="Área cubierta").add_to(mapa)

            st.markdown("🗺️ Área aproximada del archivo:")
            st_folium(mapa, width=1200, height=600)

        except Exception as e:
            st.error(f"❌ Error leyendo el archivo: {e}")
    elif submit_button:
        st.warning("Debes seleccionar un archivo .gpkg para continuar.")
