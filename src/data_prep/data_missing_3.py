import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import make_column_transformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import KNeighborsRegressor
from ..utils.data_transformation import load_data, binarize_data, get_missing_data

def train_model(data, column, model, cols = []):
    train = data[data[column].notna()]
    train = train.drop(columns=['remainder__Id'])
    if 'SalePrice' in train.columns:
        train = train.drop(columns=['SalePrice'])
    X_train = train.dropna()
    y_train = X_train[column]
    X_train = X_train.drop(columns = [column])

    if len(cols) != 0:
        X_train = X_train[cols]

    model.fit(X_train,y_train)

    return model

def predict_values(data_train, data_test, column, model):
    test = data_train[data_train[column].isna()]
    if not test.empty:
        test = test.drop(columns=['remainder__Id','SalePrice'])
        X_test = test.drop(columns=[column])
        na_index = X_test[X_test.notna().all(axis=1)].index
        X_test = X_test.dropna()

        if(len(na_index) != 0):
            y_pred = model.predict(X_test)
            data_train.loc[na_index,column] = y_pred
    

    test = data_test[data_test[column].isna()]
    if not test.empty:
        test = test.drop(columns=['remainder__Id'])
        X_test = test.drop(columns=[column])
        na_index = X_test[X_test.notna().all(axis=1)].index
        X_test = X_test.dropna()

        if(len(na_index) != 0):
            y_pred = model.predict(X_test)
            data_test.loc[na_index,column] = y_pred

def predict_intersection(data_train, data_test, column, model):
    test = data_train[data_train[column].isna()]
    if not test.empty:
        test = test.drop(columns=['remainder__Id','SalePrice'])
        X_test = test.drop(columns=[column])
        X_test = X_test.dropna(axis=1)
        cols_after_drop = X_test.columns
        model = train_model(data_train,column,model,cols_after_drop)
        
        y_pred = model.predict(X_test)
        data_train.loc[data_train[column].isna(),column] = y_pred
    
    test = data_test[data_test[column].isna()]
    if not test.empty:
        test = test.drop(columns=['remainder__Id'])
        X_test = test.drop(columns=[column])
        X_test = X_test.dropna(axis=1)
        cols_after_drop = X_test.columns
        model = train_model(data_test,column,model,cols_after_drop)
        
        y_pred = model.predict(X_test)
        data_test.loc[data_test[column].isna(),column] = y_pred

def main():
    data_train,data_test = load_data("train_encoded", "test_encoded")
    
    #atributos nos quais valores falantes representam ausência de uma característica
    missing_zero_cols = ['remainder__GarageYrBlt','remainder__BsmtHalfBath','remainder__BsmtFullBath','remainder__TotalBsmtSF','remainder__BsmtUnfSF','remainder__BsmtFinSF2','remainder__BsmtFinSF1']
    data_train[missing_zero_cols] = data_train[missing_zero_cols].fillna(0)
    data_test[missing_zero_cols] = data_test[missing_zero_cols].fillna(0)

    #lista de colunas que possuem pelo menos 1 valor faltante
    list_missing_cols = pd.concat([data_train, data_test]).columns[pd.concat([data_train, data_test]).isnull().any()].tolist()

    #identificando atributos categóricos
    list_missing_cols_categ = list_missing_cols.filter(regex='cat__').columns.tolist()
    
    model = KNeighborsClassifier()
    
    for col in list_missing_cols_categ:
        model = train_model(data_train,col,model)
        predict_values(data_train,data_test,col,model)

    print(" Depois de inferir algumas variáveis categóricas ")
    
    intersection_train = get_missing_data(data_train[list_missing_cols_categ])
    intersection_test = get_missing_data(data_test[list_missing_cols_categ])

    intersection_train = intersection_train[intersection_train != 0.0]
    intersection_test = intersection_test[intersection_test != 0.0]

    intersection = pd.concat([intersection_train,intersection_test]).index.drop_duplicates()
    """ VARIÁVEIS COM INTERSECÇÃO DE VALORES FALTANTES )
    remainder__MasVnrType ( treino )
    remainder__MasVnrType ( teste ) 
    remainder__MSZoning ( teste )
    remainder__Utilities ( todas as linhas com interseção )
    remainder__Functional ( teste )"""

    intersection_model = KNeighborsClassifier()

    for col in intersection:
        predict_intersection(data_train,data_test,col,intersection_model)

    print("Depois de inferir as variáveis categóricas com interseção")
    missing_data_train = get_missing_data(data_train[list_missing_cols_categ])
    missing_data_test = get_missing_data(data_test[list_missing_cols_categ])


    list_missing_cols = list_missing_cols.drop(list_missing_cols_categ)

    model = KNeighborsRegressor()

    for col in list_missing_cols:
        model = train_model(data_train,col,model)
        predict_values(data_train,data_test,col,model)

    print("Depois de inferir as variáveis númericas")
    intersection_train = get_missing_data(data_train[list_missing_cols])
    intersection_test = get_missing_data(data_test[list_missing_cols])

    intersection = pd.concat([intersection_train,intersection_test]).index.drop_duplicates()
    """ 
    remainder__GarageArea com todas as linhas do teste com interseção
    remainder__GarageCars com todas as linhas do teste com interseção
    remainder__LotFrontage ( treino e teste ) com interseção
    remainder__MasVnrArea ( treino e teste ) com interseção
    """

    intersection_model = KNeighborsRegressor()

    for col in intersection:
        predict_intersection(data_train,data_test,col,intersection_model)

    print("Depois de inferir as variáveis númericas com interseção")
    missing_data_train = get_missing_data(data_train)
    missing_data_test = get_missing_data(data_test)

    data_train['remainder__Id'] = data_train['remainder__Id'].astype(int)
    data_test['remainder__Id'] = data_test['remainder__Id'].astype(int)

    columns_to_binarize = ['MSZoning', 'Utilities', 'Exterior1st', 'SaleType', 'Functional', 'Electrical', 'MasVnrType']
    data_train,data_test = binarize_data(data_train,data_test,columns_to_binarize)
    
    data_train.to_csv('dataset/train_encoded_imputed.csv',index=False)
    data_test.to_csv('dataset/test_encoded_imputed.csv',index=False)

if __name__ == '__main__':
    main()

# Imputação dos dados númericos, pois os categoricos foram codificados e os NA representam uma categoria
# variáveis categóricas que possui valores faltantes sem explicação : 
# MasVnrType: Masonry veneer type ( categoria "nan" = None e NA ) -> Teste e treino
# MasVnrArea: Masonry veneer area in square feet OK ----> Regrediu alguns valores negativos para alguns NA, levando a crer que não possui masonry veneer (MasVnrType = None)
# LotFrontage: Linear feet of street connected to property OK --> Regrediu valores coerentes e positivos para os NA
# Electrical: Electrical system  --> Possui uma categoria "nan" que representa um valor faltante, mesmo o Nan nao sendo uma informação  ( TREINO APENAS)
# Mszoning : Identifies the general zoning classification of the sale. ( TESTE APENAS ) --> Valor faltante não representa uma categoria, mas esta codificado quando todas as categorias é 0
# KitchenQual: Kitchen quality ( TESTE APENAS ) ->  ((((( Valor faltante = 0 ))))), uma linha apenas
# Utilities : Type of utilities available ( TESTE APENAS ) -> ((((( Valor faltante = 0 ))))), uma linha apenas
# Functional: Home functionality ( TESTE APENAS ) -> ((((( Valor faltante = 0 ))))), uma linha apenas
# SaleType: Type of sale ( TESTE APENAS ) -> ((((( Valor faltante = 0 ))))), uma linha apenas
# Exterior1st: Exterior covering on house ( TESTE APENAS ) -> ((((( Valor faltante = 0 ))))), uma linha apenas





"""Missing values in train data
remainder__LotFrontage    0.177397
remainder__GarageYrBlt    0.055479  NA significa que nao tem garagem
remainder__MasVnrType     0.008904
remainder__MasVnrArea     0.005479
remainder__Electrical     0.000685
dtype: float64
Missing values in test data
remainder__LotFrontage     0.155586
remainder__GarageYrBlt     0.053461 NA significa que nao tem garagem
remainder__MasVnrType      0.012337
remainder__MasVnrArea      0.010281
remainder__MSZoning        0.002742
remainder__Utilities       0.001371
remainder__BsmtFullBath    0.001371 Na significa que nao tem porao
remainder__BsmtHalfBath    0.001371 Na significa que nao tem porao
remainder__Functional      0.001371
remainder__SaleType        0.000685
remainder__GarageCars      0.000685 
remainder__BsmtFinSF1      0.000685 Na significa que nao tem porao
remainder__BsmtFinSF2      0.000685 Na significa que nao tem porao
remainder__BsmtUnfSF       0.000685 Na significa que nao tem porao
remainder__TotalBsmtSF     0.000685 Na significa que nao tem porao
remainder__Exterior1st     0.000685
remainder__GarageArea      0.000685
remainder__KitchenQual     0.000685
dtype: float64"""







 


