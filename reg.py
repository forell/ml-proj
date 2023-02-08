import numpy as np
import pandas as pd 
import itertools as it
import csv
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.model_selection import train_test_split

#['TMAX', 'TMIN', 'STD', 'TMNG', 'SMDB', 'opad', 'PKSN', 'RWSN', 'USL', 'DESZ', 'SNEG', 'DISN', 'GRAD', 'MGLA', 'ZMGL', 'SADZ', 'GOLO', 'ZMNI', 'ZMWS', 'ZMET', 'FF10', 'FF15', 'BRZA', 'ROSA', 'SZRO', 'DZPS', 'DZBL', 'grun', 'IZD', 'IZG', 'AKTN']

# more convenient names
labels_dict = {
    "STD" : "TAVG",
    "TMNG": "TMIN_GRUN",
    "SMDB": "SUM_OPAD",
    "PKSN": "WYS_SNG",
    "RWSN": "ROW_WOD_SNG",
    "DESZ": "t_DESZ",
    "SNEG": "t_SNG",
    "DISN": "t_DESZ_ZE_SNG",
    "ZMNI": "ZAM_SN_NIS",
    "ZMWS": "ZAM_SN_WYS",
    "ZMET": "ZMĘTNIENIE",
    "FF10": "t_WIATR_>10ms",
    "FF15": "t_WIATR_>15ms",
    "DZPS": "POK_SNG?",
    "DZBL": "BŁYSK?",
    "IZD" : "IZOTERMA_DLN",
    "IZG" : "IZOTERMA_GRN",
    "AKTN": "AKTYNOMETRIA"    
}


def create_long_labels(labels):
    res = []
    for label in labels:
        if label in labels_dict:
            label = labels_dict[label]   
        res.append(label)
    return res

    
def X_of_given_params(X, labels, param_list):
    indices = [labels.index(param) for param in param_list]
    return X[:,indices]


def read_data(X_file, y_file):
    with open(X_file) as f:
        reader = csv.reader(f)
        labels_from_file = next(reader)
    X = np.genfromtxt(X_file, delimiter=",")[1:]
    labels = create_long_labels(labels_from_file)
    y = np.genfromtxt(y_file, delimiter=",")[1:]    
    return X, y, labels

    
def test_regressors(reg_list, X, y, params_names):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    for reg in reg_list:
        print(type(reg))
        reg.fit(X_train, y_train)
        y_test_pred = reg.predict(X_test)
        print("MSE:", mean_squared_error(y_test, y_test_pred))
        y_train_pred = reg.predict(X_train)
        print("train MSE:", mean_squared_error(y_train, y_train_pred))
        coeffs = [(coef, param) for coef, param in zip(reg.coef_, params_names)]
        coeffs.sort()
        for coef, param in coeffs:
            print(param, coef) 
        print()


if __name__ == "__main__":
    X_all, y, labels = read_data("X.csv", "y.csv")
    params = ["t_DESZ", "t_SNG", "SUM_OPAD", "WYS_SNG", "GRAD", "MGLA", "ZAM_SN_NIS", "ZAM_SN_WYS","t_WIATR_>15ms", "BRZA" ]
    X = X_of_given_params(X_all, labels, params)
    reg_list = [LinearRegression(), Ridge(alpha=1)] 
    test_regressors(reg_list, X, y, params)
    
    
    

