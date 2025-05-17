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
    - Puedes cambiar entre mapa base y vista satelital.
    """)

with st.form(key="form_carga_datos"):

    uploaded_file = st.file_uploader(
        "📂 Sube tu archivo GPKG", accept_multiple_files=False, type=["gpkg"]
    )

    submit_button = st.form_submit_button(label="Cargar archivo")

    if submit_button and uploaded_file is not None:
        try:
            gdf = gpd.read_file(uploaded_file)

            # Reproyectar a EPSG:4326 si es necesario
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                st.info(f"📐 Reproyectando desde {gdf.crs} a EPSG:4326 para visualización.")
                gdf = gdf.to_crs(epsg=4326)

            st.write("Vista previa del archivo:")
            st.dataframe(gdf.head())

            # Filtrar geometrías válidas
            gdf = gdf[gdf.geometry.notnull() & ~gdf.geometry.is_empty]

            # Extraer bounding box
            bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
            minx, miny, maxx, maxy = bounds

            # Crear polígono rectangular
            rectangle = Polygon([
                (minx, miny),
                (minx, maxy),
                (maxx, maxy),
                (maxx, miny),
                (minx, miny)
            ])
            gdf_rect = gpd.GeoDataFrame(geometry=[rectangle], crs=gdf.crs)

            # Crear mapa sin tiles base inicial
            mapa = folium.Map(location=[(miny + maxy) / 2, (minx + maxx) / 2], zoom_start=8, tiles=None)
            
            # Capas base
            folium.TileLayer("OpenStreetMap", name="Mapa Base").add_to(mapa)
            
            # Satélite puro
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri",
                name="Satélite (Esri World Imagery)",
                overlay=False,
                control=True
            ).add_to(mapa)

            #Etiquetas
            folium.TileLayer(
                tiles="https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
                attr="Esri",
                name="Nombres del Territorio",
                overlay=True,
                control=True
            ).add_to(mapa)
            
            # Añadir el bounding box
            folium.GeoJson(gdf_rect, name="Área de Estudio", tooltip="Área cubierta").add_to(mapa)
            
            # Centrar automáticamente el mapa en el polígono
            mapa.fit_bounds([[miny, minx], [maxy, maxx]])
            
            # Control de capas
            folium.LayerControl(collapsed=False).add_to(mapa)
            
            # Mostrar el mapa adaptado al ancho de pantalla
            st_folium(mapa, width='100%', height=600)


        except Exception as e:
            st.error(f"❌ Error leyendo el archivo: {e}")
    elif submit_button:
        st.warning("Debes seleccionar un archivo .gpkg para continuar.")
