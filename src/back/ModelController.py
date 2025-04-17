import Definitions

import numpy as np
import os.path as osp
import pandas as pd
from io import StringIO

import joblib
from src.model.DataPreprocessing import DataPreprocessing

class ModelController:

    def __init__(self):
        print("ModelController.__init__ ->")
        # Asegura en una variable la ruta de los modelos
        self.model_path = osp.join(Definitions.ROOT_DIR, "resources/models")
        # Almacena la ruta de cada modelo en una variable
        self.rf_model_path = osp.join(self.model_path, "rf_model.joblib")
        self.svc_model_path = osp.join(self.model_path, "svc_model.joblib")

        #Cargar los modelos
        self.rf_model = joblib.load(self.rf_model_path)
        self.svc_model = joblib.load(self.svc_model_path)

        # Inicializar variables
        self.input_df = ""
        # Clase de preprocesamiento de la información
        self.d_processing = DataPreprocessing()

    def validate_data(self, df):
        return self.d_processing.get_columns().issubset(df.columns)

    def load_input_data(self, input_data):
        print("ModelController.load_input_data ->")
        try:
            input_data_str = StringIO(input_data.decode("utf-8"))
            self.input_df = pd.read_csv(input_data_str)
            is_valid = self.validate_data(self.input_df)
            return self.input_df, is_valid

        except:
            raise("Ocurrió un error al leer la información de entrada")

    def predict(self):
        print("ModelController.predict ->")

        # Generamos la partición de la información
        #X_test, Y_test = self.input_df.drop([self.target_feature], axis=1), self.input_df[self.target_feature]
        X_test, Y_test = self.d_processing.transform(self.input_df)

        # Predicciones SVM y probabilidad (con redondeo)
        y_pred_svc = self.svc_model.predict(X_test)
        y_pred_proba_svc = self.svc_model.predict_proba(X_test)
        y_pred_proba_svc = np.round(y_pred_proba_svc * 100, 2)

        # Preparamos un dataframe para presentar al usuario final
        svc_result_df = X_test.copy()
        svc_result_df["Real"] = Y_test.values
        svc_result_df["Real"] = svc_result_df["Real"].replace(
            {0: self.d_processing.get_cat_name(0), 1: self.d_processing.get_cat_name(1)})
        svc_result_df["Predicción"] = y_pred_svc
        svc_result_df["Predicción"] = svc_result_df["Predicción"].replace(
            {0: self.d_processing.get_cat_name(0), 1: self.d_processing.get_cat_name(1)})
        svc_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(0)} (%)"] = y_pred_proba_svc[:, 0]
        svc_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(1)} (%)"] = y_pred_proba_svc[:, 1]

        # Predicciones RF y probabilidad (con redondeo)
        y_pred_rf = self.rf_model.predict(X_test)
        y_pred_proba_rf = self.svc_model.predict_proba(X_test)
        y_pred_proba_rf = np.round(y_pred_proba_rf * 100, 2)

        # Dataframe de los resultados para RandomForest
        rf_result_df = X_test.copy()
        rf_result_df["Real"] = Y_test.values
        rf_result_df["Real"] = rf_result_df["Real"].replace(
            {0: self.d_processing.get_cat_name(0), 1: self.d_processing.get_cat_name(1)})
        rf_result_df["Predicción"] = y_pred_rf
        rf_result_df["Predicción"] = rf_result_df["Predicción"].replace(
            {0: self.d_processing.get_cat_name(0), 1: self.d_processing.get_cat_name(1)})
        rf_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(0)} (%)"] = y_pred_proba_rf[:, 0]
        rf_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(1)} (%)"] = y_pred_proba_rf[:, 1]

        # Dataframe compilado
        full_result_df = X_test.copy()
        full_result_df["Real"] = svc_result_df["Real"]
        full_result_df["Predicción SVM"] = svc_result_df["Predicción"]
        full_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(0)} (%) SVM"] = svc_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(0)} (%)"]
        full_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(1)} (%) SVM"] = svc_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(1)} (%)"]
        full_result_df["Predicción RF"] = rf_result_df["Predicción"]
        full_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(0)} (%) RF"] = rf_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(0)} (%)"]
        full_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(1)} (%) RF"] = rf_result_df[f"Probabilidad Clase {self.d_processing.get_cat_name(1)} (%)"]

        return svc_result_df, rf_result_df, full_result_df

