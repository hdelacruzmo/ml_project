import numpy as np
import pandas as pd

class DataPreprocessing:

    def __init__(self):
        print("DataPreprocessing.__init__ ->")
        self.target_feature = "TravelInsurance"

    def transform(self, df):
        print("DataPreprocessing.transform ->")
        X_test, Y_test = df.drop([self.target_feature], axis=1), df[self.target_feature]
        return X_test, Y_test

    def get_categories(self):
        print("DataPreprocessing.get_categories ->")
        return ["NO", "YES"]

    def get_cat_name(self, index):
        print("DataPreprocessing.get_cat_name ->")
        if index < 0 or index > 1:
            return ""
        return self.get_categories()[index]

    def get_columns(self):
        print("DataPreprocessing.get_columns ->")
        return {'Age', 'Employment Type', 'GraduateOrNot', 'AnnualIncome', 'FamilyMembers',
                'ChronicDiseases', 'FrequentFlyer', 'EverTravelledAbroad', 'TravelInsurance'}