import logging
from pickle import load
import numpy as np

classes = ['Setosa', 'Versicolor', 'Virginica']


def validate(sepal_length: str, sepal_width: str):
    sepal_length = float(sepal_length)
    sepal_width = float(sepal_width)

    try:
        with open("./modules/scikitlearn_example/iris_tree.pkl", "rb") as f:
            clf = load(f)
    except FileNotFoundError:
        logging.error("File not found")
        return None

    input_data = np.array([[sepal_length, sepal_width]])
    predicted_species = clf.predict(input_data)
    result = "Predicted species: " + classes[predicted_species[0]]

    return [result]
