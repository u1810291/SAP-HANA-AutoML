import optuna

from optimizers.base_optimizer import BaseOptimizer
from pipeline.leaderboard import Leaderboard
from pipeline.modelres import ModelBoard


class OptunaOptimizer(BaseOptimizer):
    """Optuna hyperparameters optimizer. (https://optuna.org/)

    Attributes
    ----------
    data : Data
        Input data.
    algo_list : list
        List of algorithms to be tuned and compared.
    algo_dict : dict
        Dictionary of algorithms to be tuned and compared.
    iter : int
        Number of iterations.
    problem : str
        Machine learning problem.
    tuned_params : str
        Final tuned hyperparameters of best algorithm.
    categorical_features : list
        List of categorical features in dataframe.
    imputer
        Imputer for preprocessing.
    model
        Tuned HANA ML model in algorithm.
    droplist_columns
        Columns in dataframe to be dropped.
    """

    def __init__(
        self,
        algo_list,
        data,
        problem,
        iterations,
        algo_dict,
        categorical_features=None,
        droplist_columns=None,
    ):
        self.algo_list = algo_list
        self.data = data
        self.iterations = iterations
        self.problem = problem
        self.algo_dict = algo_dict
        self.categorical_features = categorical_features
        self.droplist_columns = droplist_columns
        self.model = None
        self.imputer = None
        self.leaderboard: Leaderboard = Leaderboard()
        self.accuracy = 0

    def tune(self):
        opt = optuna.create_study(direction="maximize")
        opt.optimize(self.objective, n_trials=self.iterations)
        self.tuned_params = opt.best_params
        self.imputer = opt.best_params.pop("imputer")

        # Model in Leaderboard is not tuned
        self.model = self.leaderboard.board[0].model
        data = self.data.clear(
            num_strategy=self.imputer,
            cat_strategy=None,
            dropempty=False,
            categorical_list=None,
        )
        self.fit(self.model, data)

    def objective(self, trial):
        """Objective function. Optimizer uses it to search for best algorithm and preprocess method.

        Parameters
        ----------
        trial
            Optuna trial. Details here: https://optuna.readthedocs.io/en/stable/reference/trial.html

        Returns
        -------
        Score
            Model perfomance.

        """
        algo = self.algo_dict.get(
            trial.suggest_categorical("algo", self.algo_dict.keys())
        )
        imputer = trial.suggest_categorical("imputer", ["mean", "median", "zero"])
        data = self.data.clear(
            num_strategy=imputer,
            cat_strategy=None,
            dropempty=False,
            categorical_list=None,
        )
        model = algo.optunatune(trial)
        self.fit(model, data)
        acc = model.score(data.valid, key=data.id_colm, label=data.target)
        self.leaderboard.addmodel(ModelBoard(model, acc))
        return acc

    def get_tuned_params(self):
        """Returns tuned hyperparameters."""
        return {
            "title": self.tuned_params.pop("algo"),
            "accuracy": self.leaderboard.board[0].accuracy,
            "info": self.tuned_params,
        }

    def get_model(self):
        """Returns tuned model."""
        return self.model

    def get_preprocessor_settings(self):
        """Returns tuned preprocessor settings."""
        return {"imputer": self.imputer}

    def fit(self, model, data):
        """Fits given model from data. Small method to reduce code repeating."""
        ftr: list = data.train.columns
        ftr.remove(data.target)
        ftr.remove(data.id_colm)
        model.fit(
            data.train,
            key=data.id_colm,
            features=ftr,
            categorical_variable=self.categorical_features,
            label=data.target,
        )
