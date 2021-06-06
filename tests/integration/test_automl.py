import pytest
from hana_automl.automl import AutoML
from hana_automl.storage import Storage
from ..connection import connection_context, schema
from benchmarks.cleanup import clean

clean(connection_context, schema=schema)

m = AutoML(connection_context)
storage = Storage(connection_context, schema)  # replace with your schema


@pytest.mark.parametrize("optimizer", ["OptunaSearch", "BayesianOptimizer"])
def test_regression(optimizer):
    m.fit(
        table_name="TESTING_REG",
        file_path="data/boston_data.csv",
        target="medv",
        id_column="ID",
        steps=3,
        optimizer=optimizer,
        output_leaderboard=True,
        task="reg",
    )
    assert m.best_params["accuracy"] > 0.50
    m.model.name = "TESTING_MODEL_REG"
    storage.save_model(m)
    new = storage.load_model("TESTING_MODEL_REG", version=1)
    assert new.predict(file_path="./data/boston_test_data.csv").empty is False
    assert storage.list_preprocessors("TESTING_MODEL_REG").empty is False
    storage.delete_model("TESTING_MODEL_REG", version=1)


@pytest.mark.parametrize("optimizer", ["OptunaSearch", "BayesianOptimizer"])
def test_classification(optimizer):
    m.fit(
        table_name="TESTING_CLS",
        file_path="data/cleaned_train.csv",
        target="Survived",
        id_column="PASSENGERID",
        categorical_features=["Survived"],
        steps=3,
        optimizer=optimizer,
        task="cls",
        output_leaderboard=True,
    )
    assert m.best_params["accuracy"] > 0.50
    m.model.name = "TESTING_MODEL_CLS"
    storage.save_model(m)
    new = storage.load_model("TESTING_MODEL_CLS", version=1)
    assert (
        new.predict(
            file_path="./data/test_cleaned_train.csv", id_column="PassengerId"
        ).empty
        is False
    )
    assert storage.list_preprocessors("TESTING_MODEL_CLS").empty is False
    storage.delete_model("TESTING_MODEL_CLS", version=1)


@pytest.mark.parametrize("task", ["cls", "reg"])
def test_ensembles(task):
    if task == "reg":
        m.fit(
            table_name="TESTING_REG",
            file_path="data/boston_data.csv",
            target="medv",
            id_column="ID",
            steps=3,
            ensemble=True,
            output_leaderboard=True,
            task="reg",
        )
        assert m.best_params["accuracy"] > 0.50
        m.model.name = "TESTING_MODEL_REG_ENS"
        storage.save_model(m)
        new = storage.load_model("TESTING_MODEL_REG_ENS", version=1)
        assert new.predict(file_path="./data/boston_test_data.csv").empty is False
        assert storage.list_preprocessors("TESTING_MODEL_REG_ENS").empty is False
        storage.delete_model("TESTING_MODEL_REG_ENS", version=1)
        assert storage.list_models("TESTING_MODEL_REG_ENS").empty is True
    else:
        m.fit(
            table_name="TESTING_CLS",
            file_path="data/cleaned_train.csv",
            target="Survived",
            id_column="PASSENGERID",
            categorical_features=["Survived"],
            steps=3,
            ensemble=True,
            task="cls",
            output_leaderboard=True,
        )
        assert m.best_params["accuracy"] > 0.50
        m.model.name = "TESTING_MODEL_CLS_ENS"
        storage.save_model(m)
        new = storage.load_model("TESTING_MODEL_CLS_ENS", version=1)
        assert (
            new.predict(
                file_path="./data/test_cleaned_train.csv", id_column="PassengerId"
            ).empty
            is False
        )
        assert storage.list_preprocessors("TESTING_MODEL_CLS_ENS").empty is False
        storage.delete_model("TESTING_MODEL_CLS_ENS", version=1)
        assert storage.list_models("TESTING_MODEL_CLS_ENS").empty is True
