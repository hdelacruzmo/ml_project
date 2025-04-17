#Aseguramos el control de rutas en python
import Definitions
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
#from io import StringIO

from src.back.ModelController import ModelController

### Setup and configuration

st.set_page_config(
    layout="centered", page_title="Travel Insurance", page_icon="❄️"
)

### Support functions

def highlight_diff(row):
    if row["Real"] != row["Predicción"]:
        # return ["background-color: blue"] * len(row)
        return ["background-color: #F5F5F5; color: black; font-weight: bold"] * len(row)
    return [""] * len(row)

def highlight_full_diff(row):
    if row["Predicción SVM"] != row["Predicción RF"]:
        # return ["background-color: blue"] * len(row)
        return ["background-color: #F5F5F5; color: black; font-weight: bold"] * len(row)
    return [""] * len(row)

### My vars

ctrl = ModelController()

### My UI starting here

with st.expander("Tip"):
    f"""
    Please upload your file, click on submit. We will provide you the results. 
    """

with st.form(key="my_form"):

    uploaded_file = st.file_uploader(
        "Choose a CSV file", accept_multiple_files=False, type="csv"
    )

    submit_button = st.form_submit_button(label="Submit")

    with st.spinner("Processing your information...."):

        if submit_button and uploaded_file is not None:
            try:
                # Cargar la información del archivo csv
                bytes_data = uploaded_file.getvalue()
                st.write("Filename:", uploaded_file.name)

                #Asegurar la información de entrada como pandas dataframe
                input_df, is_valid = ctrl.load_input_data(bytes_data)

                if not is_valid:
                    st.warning("File structure not valid", icon="⚠️")

                # Presentamos la inforamción de forma tabulada o pestañas
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Input Data", "Stats", "SVM", "Random Forest", "Full View"])

                with tab1:
                    # Los datos deben ser presentados si son válidos, en este caso que pertenezcan a un pandas dataframe
                    if isinstance(input_df, pd.DataFrame) and not input_df.empty:
                        st.subheader("🧩 My Input Data")
                        st.dataframe(input_df)
                        svc_df, rf_df, full_df = ctrl.predict()
                    else:
                        is_valid = False

                with tab2:
                    df_long = full_df.melt(id_vars=["Real"], value_vars=["Predicción RF", "Predicción SVM"],
                                           var_name="Modelo", value_name="Predicción")

                    df_counts = df_long.groupby(["Modelo", "Predicción"]).size().reset_index(name="Cantidad")

                    fig = px.bar(df_counts, x="Modelo", y="Cantidad", color="Predicción",
                                 title="",
                                 barmode="stack",  # "group" para barras separadas
                                 text="Cantidad")

                    # Mostrar en Streamlit
                    st.subheader("📊 Model Predictions for class 'YES'")
                    # st.plotly_chart(fig, use_container_width=True)
                    st.plotly_chart(fig)
                with tab3:
                    svc_styled_df = svc_df.style.apply(highlight_diff, axis=1)
                    st.subheader("🏿 Original data and predictions")
                    # st.dataframe(svc_df)
                    st.dataframe(svc_styled_df)
                with tab4:
                    rf_styled_df = rf_df.style.apply(highlight_diff, axis=1)
                    st.subheader("🏿 Original data and predictions")
                    # st.dataframe(svc_df)
                    st.dataframe(rf_styled_df)
                with tab5:
                    full_styled_df = full_df.style.apply(highlight_full_diff, axis=1)
                    st.subheader("🏿 Original data and predictions")
                    # st.dataframe(full_df)
                    st.dataframe(full_styled_df)
                if is_valid:
                    st.success("✅ Done!")
            except:
                st.error("Something happened", icon="🚨")
        elif submit_button and uploaded_file is None:
            st.error("You must choose a csv file", icon="🚨")

