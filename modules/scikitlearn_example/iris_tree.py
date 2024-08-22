from sklearn.datasets import load_iris
from sklearn import tree
from pickle import dump


iris = load_iris()
X = iris.data
y = iris.target

clf = tree.DecisionTreeClassifier()
X = iris.data[:, :2]
clf = clf.fit(X, y)

with open("iris_tree.pkl", "wb") as f:
    dump(clf, f, protocol=5)
