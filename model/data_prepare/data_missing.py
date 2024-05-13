import pandas as pd
import numpy as np

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

data_train = pd.read_csv('dataset/train_encoded.csv')
data_test = pd.read_csv('dataset/test_encoded.csv')


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


data_train['remainder__GarageYrBlt'] = data_train['remainder__GarageYrBlt'].fillna(0)

data_test['remainder__GarageYrBlt'] = data_test['remainder__GarageYrBlt'].fillna(0)
data_test['remainder__BsmtHalfBath'] = data_test['remainder__BsmtHalfBath'].fillna(0)
data_test['remainder__BsmtFullBath'] = data_test['remainder__BsmtFullBath'].fillna(0)
data_test['remainder__TotalBsmtSF'] = data_test['remainder__TotalBsmtSF'].fillna(0)
data_test['remainder__BsmtUnfSF'] = data_test['remainder__BsmtUnfSF'].fillna(0)
data_test['remainder__BsmtFinSF2'] = data_test['remainder__BsmtFinSF2'].fillna(0)
data_test['remainder__BsmtFinSF1'] = data_test['remainder__BsmtFinSF1'].fillna(0)

missing_data_train = data_train.isnull().sum().sort_values(ascending=False) / data_train.shape[0]

missing_data_test = data_test.isnull().sum().sort_values(ascending=False) / data_test.shape[0]

print("Missing values in train data")
print(missing_data_train[missing_data_train != 0.0])

print("Missing values in test data")
print(missing_data_test[missing_data_test != 0.0])


list_missing_cols_train = missing_data_train[missing_data_train != 0.0].index
list_missing_cols_test = missing_data_test[missing_data_test != 0.0].index

list_missing_cols = list_missing_cols_train.union(list_missing_cols_test)

list_missing_cols_categ  = ['remainder__MasVnrType', 'remainder__Electrical', 'remainder__MSZoning','remainder__Utilities','remainder__Functional','remainder__SaleType','remainder__Exterior1st','remainder__KitchenQual']

from sklearn.neighbors import KNeighborsClassifier

for col in list_missing_cols_categ:
    train = data_train[data_train[col].notna()]
    train = train.drop(columns=['remainder__Id'])
    train = train.drop(columns=['SalePrice'])

    X_train = train.drop(columns=list_missing_cols)
    y_train = train[col]

    model = KNeighborsClassifier()

    model.fit(X_train,y_train)

    if col in ['remainder__MasVnrType', 'remainder__Electrical']:
        test = data_train[data_train[col].isna()]
        test = test.drop(columns=['remainder__Id','SalePrice'])
        X_test = test.drop(columns=list_missing_cols)

        y_pred = model.predict(X_test)

        data_train.loc[data_train[col].isna(),col] = y_pred
    if col != 'remainder__Electrical':
        test = data_test[data_test[col].isna()]
        test = test.drop(columns=['remainder__Id'])
        X_test = test.drop(columns=list_missing_cols)

        y_pred = model.predict(X_test)

        data_test.loc[data_test[col].isna(),col] = y_pred


list_missing_cols = list_missing_cols.drop(list_missing_cols_categ)

print(list_missing_cols)

from sklearn.neighbors import KNeighborsRegressor

for col in list_missing_cols:
    train = data_train[data_train[col].notna()]
    train = train.drop(columns=['remainder__Id'])
    train = train.drop(columns=['SalePrice'])

    X_train = train.drop(columns=list_missing_cols)
    y_train = train[col]

    model = KNeighborsRegressor()

    model.fit(X_train,y_train)

    if col in ['remainder__LotFrontage','remainder__MasVnrArea']:
        test = data_train[data_train[col].isna()]
        test = test.drop(columns=['remainder__Id','SalePrice'])
        X_test = test.drop(columns=list_missing_cols)

        y_pred = model.predict(X_test)

        data_train.loc[data_train[col].isna(),col] = y_pred
    
    test = data_test[data_test[col].isna()]
    test = test.drop(columns=['remainder__Id'])
    X_test = test.drop(columns=list_missing_cols)

    y_pred = model.predict(X_test)

    data_test.loc[data_test[col].isna(),col] = y_pred

missing_data_train = data_train.isnull().sum().sort_values(ascending=False) / data_train.shape[0]

missing_data_test = data_test.isnull().sum().sort_values(ascending=False) / data_test.shape[0]

print("Missing values in train data")
print(missing_data_train[missing_data_train != 0.0])

print("Missing values in test data")
print(missing_data_test[missing_data_test != 0.0])

data_train['remainder__Id'] = data_train['remainder__Id'].astype(int)
data_test['remainder__Id'] = data_test['remainder__Id'].astype(int)

data_train.to_csv('dataset/train_encoded_imputed.csv',index=False)
data_test.to_csv('dataset/test_encoded_imputed.csv',index=False)







