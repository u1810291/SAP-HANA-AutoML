import pandas as pd
from hana_ml.algorithms.pal.metrics import r2_score
from hana_ml.dataframe import create_dataframe_from_pandas

from algorithms.ensembles.bagging import Bagging
from pipeline.leaderboard import Leaderboard


class BaggingReg(Bagging):
    def __init__(self, categorical_features, id_col, connection_context, table_name, model_list: list = None,
                 leaderboard: Leaderboard = None):
        super(BaggingReg, self).__init__(categorical_features, id_col, connection_context,
                                         table_name, model_list, leaderboard)
        self.title = "BaggingClassifier"

    def score(self, data=None, df=None):
        hana_df = self.predict(data=data, df=df)
        ftr: list = data.valid.columns
        ftr.remove(data.target)
        dat = data.valid.drop(ftr)
        itg = hana_df.join(dat, "1 = 1")
        print(itg.collect().head())
        return r2_score(data=itg, label_true=data.target, label_pred="PREDICTION")

    def predict(self, data=None, df=None):
        predictions = super(BaggingReg, self).predict(data=data, df=df)
        pd_res = list()
        for res in predictions:
            pd_res.append(res.collect())
        pred = list()
        for i in range(pd_res[0].shape[0]):
            if pd_res[0].at[i, pd_res[0].columns[1]] == pd_res[1].at[i, pd_res[1].columns[1]]:
                pred.append(pd_res[0].at[i, pd_res[0].columns[1]])
            else:
                pred.append((pd_res[0].at[i, pd_res[0].columns[1]] + pd_res[1].at[i, pd_res[1].columns[1]] +
                             pd_res[2].at[i, pd_res[2].columns[1]])/3)
        d = {'PREDICTION': pred}
        df = pd.DataFrame(data=d)
        hana_df = create_dataframe_from_pandas(
            self.connection_context, df, self.table_name + "_bagging", force=True, drop_exist_tab=True
        )
        return hana_df
