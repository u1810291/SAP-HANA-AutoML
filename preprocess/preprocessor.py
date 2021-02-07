import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

from algorithms.classification.decisiontree import DecisionTree
from algorithms.classification.kneighbors import KNeighbors
from algorithms.classification.logregression import LogRegression
from algorithms.classification.randomforest import RandomForest
from algorithms.classification.sgd import SGD
from algorithms.regression.ridge import RidgeRegression
from algorithms.regression.svr import SVRRegression
from preprocess.impsettings import ImputerSettings
from utils.error import PreprocessError
from pipeline.data import Data
from algorithms.regression.svr import SVRRegression
from algorithms.regression.lassoReg import LassoReg


class Preprocessor:
    def clean(
        self,
        data: Data,
        droplist_columns=None,
        categorical_list=None,
        predict_column_importance=True,
        dropempty=False,
        encoder_method="OneHotEncoder",
        numimpset=ImputerSettings(),
        stringimpset=ImputerSettings(basicvars="string"),
        boolimpset=ImputerSettings(basicvars="bool"),
    ):
        if data is None:
            raise PreprocessError("Enter not null data!")
        if droplist_columns is not None:
            data.X_train = self.removecolumns(columns=droplist_columns, df=data.X_train)
            data.X_test = self.removecolumns(columns=droplist_columns, df=data.X_test)
        if predict_column_importance:
            data.X_train = self.autoremovecolumns(df=data.X_train)
            data.X_test = self.autoremovecolumns(df=data.X_test)

        data.X_train = self.autoimput(
            df=data.X_train,
            dropempty=dropempty,
            numimpset=numimpset,
            stringimpset=stringimpset,
            boolimpset=boolimpset,
        )
        data.X_test = self.autoimput(
            df=data.X_test,
            dropempty=dropempty,
            numimpset=numimpset,
            stringimpset=stringimpset,
            boolimpset=boolimpset,
        )
        data.X_train = self.catencoder(
            df=data.X_train, columns=categorical_list, method=encoder_method
        )
        data.X_test = self.catencoder(
            df=data.X_test, columns=categorical_list, method=encoder_method
        )

        return data

    def autoimput(self, df, numimpset, stringimpset, boolimpset, dropempty=False):
        if df is None:
            raise PreprocessError("Enter not null data!")
        if not dropempty:
            numimputer = SimpleImputer(
                fill_value=numimpset.fill_value,
                strategy=numimpset.strategy,
                missing_values=numimpset.missing_values,
            )
            stringimputer = SimpleImputer(
                fill_value=stringimpset.fill_value,
                strategy=stringimpset.strategy,
                missing_values=stringimpset.missing_values,
            )
            boolimputer = SimpleImputer(
                fill_value=boolimpset.fill_value,
                strategy=boolimpset.strategy,
                missing_values=boolimpset.missing_values,
            )
            for column in df:
                df2 = df.copy()
                dtype = str(df[column].dtype)
                if "object" == dtype:
                    df2[column] = stringimputer.fit_transform(
                        df[column].values.reshape(-1, 1)
                    )[:, 0]
                    df = df2.copy()
                if "uint8" == dtype or "float64" == dtype or "int64" == dtype:
                    df2[column] = numimputer.fit_transform(
                        df[column].values.reshape(-1, 1)
                    )[:, 0]
                    df = df2.copy()
                if "bool" == dtype:
                    df2[column] = boolimputer.fit_transform(
                        df[column].values.reshape(-1, 1)
                    )[:, 0]
                    df = df2.copy()
        else:
            df.dropna()
        return df

    def catencoder(self, columns, df, method):
        if df is None:
            raise PreprocessError("Enter not null data!")
        if columns is not None:
            for column in columns:
                if method == "LabelEncoder":
                    encoder = LabelEncoder()
                    encoder.fit(df[column])
                    df[column] = encoder.transform(df[column])
                elif method == "OneHotEncoder":
                    # encoder = OneHotEncoder()
                    # encoder.fit(df[column])
                    # df[column] = encoder.transform(df[column])
                    df = pd.get_dummies(df, prefix=[column], columns=[column])
                else:
                    raise PreprocessError("Encoder type not found!")
        return df

    def removecolumns(self, columns, df):
        if df is None:
            raise PreprocessError("Enter not null data!")
        if columns is not None:
            for cl in df:
                if cl in columns:
                    df = df.drop([cl], axis=1)
        return df

    def autoremovecolumns(self, df):
        for cl in df:
            if (
                "object" == str(df[cl].dtype)
                and df[cl].nunique() > df[cl].shape[0] / 100 * 7
            ) or (df[cl].nunique() > df[cl].shape[0] / 100 * 9):
                df = df.drop([cl], axis=1)
        return df

    def set_task(self, y, algo_exceptions=None):
        if algo_exceptions is None:
            algo_exceptions = []
        for column in y:
            if y[column].nunique() == 2 or y[column].nunique() < 10:
                clslist = [DecisionTree(), LogRegression(), SGD(), KNeighbors(), RandomForest()]
                clsdict = {"DecisionTree": DecisionTree(), "Logistic Regression": LogRegression(), "SGD": SGD(), "KNeighbors": KNeighbors(), "RandomForest": RandomForest()}
                if "DecisionTree" in algo_exceptions:
                    clslist.remove(DecisionTree())
                    clsdict.pop("DecisionTree")
                if "Logistic Regression" in algo_exceptions:
                    clslist.remove(LogRegression())
                    clsdict.pop("Logistic Regression")
                if "SGD" in algo_exceptions:
                    clslist.remove(SGD())
                    clsdict.pop("SGD")
                if "KNeighbors" in algo_exceptions:
                    clslist.remove(KNeighbors())
                    clsdict.pop("KNeighbors")
                if "RandomForest" in algo_exceptions:
                    clslist.remove(RandomForest())
                    clsdict.pop("RandomForest")
                return clslist, 'cls', clsdict
            else:
                reglist = [RidgeRegression(), LassoReg(), SVRRegression()]
                regdict = {"RidgeRegression": RidgeRegression(), "LassoReg": LassoReg(), "SVRRegression": SVRRegression()}
                if "RidgeRegression" in algo_exceptions:
                    reglist.remove(RidgeRegression())
                    regdict.pop("RidgeRegression")
                if "LassoReg" in algo_exceptions:
                    reglist.remove(LassoReg())
                    regdict.pop("LassoReg")
                if "SVRRegression" in algo_exceptions:
                    reglist.remove(SVRRegression())
                    regdict.pop("Logistic Regression")
                return reglist, 'reg', regdict
