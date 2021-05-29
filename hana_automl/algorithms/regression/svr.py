from hana_ml.algorithms.pal.svm import SVR

from hana_automl.algorithms.base_algo import BaseAlgorithm


class SVReg(BaseAlgorithm):
    def __init__(self):
        super(SVReg, self).__init__()
        self.title = "SupportVectorRegressor"
        self.params_range = {
            "c": (50, 300),
            "kernel": (0, 3),
            "shrink": (0, 1),
            "tol": (0.001, 1),
            "scale_info": (0, 1),
        }

    def set_params(self, **params):
        params1 = {}
        params1["c"] = params.get("с", 30)
        params1["kernel"] = ["linear", "poly", "rbf", "sigmoid"][
            round(params["kernel"])
        ]
        params1["shrink"] = [True, False][round(params["shrink"])]
        params1["scale_info"] = ["no", "standardization", "rescale"][
            round(params["scale_info"])
        ]
        self.model = SVR(**params1)

    def optunatune(self, trial):
        c = trial.suggest_float("c", 0.03125, 30000, log=True)
        kernel = trial.suggest_categorical(
            "kernel", ["linear", "poly", "rbf", "sigmoid"]
        )
        shrink = trial.suggest_categorical("shrink", [True, False])
        tol = trial.suggest_float("tol", 1e-5, 1e-1, log=True)
        scale_info = trial.suggest_categorical(
            "scale_info", ["no", "standardization", "rescale"]
        )
        model = SVR(c=c, kernel=kernel, shrink=shrink, scale_info=scale_info, tol=tol)
        self.model = model
