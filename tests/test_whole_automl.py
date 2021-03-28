from automl import AutoML

m = AutoML()
m.fit(
    file_path="data/train.csv",
    target="Survived",
    columns_to_remove=["PassengerId"],
    categorical_features=["Sex", "Embarked"],
)
assert m.best_params["params"]["target"] > 0.7
