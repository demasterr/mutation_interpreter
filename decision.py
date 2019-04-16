import os
from os import system
import pandas as pd
import numpy as np

from deprecated import deprecated
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz

# Path to current working directory.
PATH = os.getcwd() + "\\output\\"

# Projects to be considered for the decision tree generation.
PROJECTS = ['jackson-core', 'dnainator', 'jfreechart', 'minimal-json']


def main():
    """
    Run main script for decision tree generation.
    """
    # Generate tree for mutation_observer results. With classified groups based on survived mutants.
    print("------------ mutant_observer results (classify) ---------------")
    our_results(do_filter=True, do_classify=True)
    print("---------------------------------------------------------------\n")


def create_tree(filename: str, data, do_classify=False):
    """
    Create a tree with a specified filename on the data provided.
    The decision tree will be saved to the specified filename
    in PNG and .dot file format.
    :param filename: Filename of the target file (no extension should provided).
    :param data: Data on which the decision tree will be based. No headers should
            be included, data should be integers only.
    :param do_classify: Boolean indicating whether to use the classify column or the full_name.
    """
    # Retrieve the X and Y split.
    y_column = 'class' if do_classify else 'full_name'
    X = data.loc[:, data.columns != y_column]
    Y = data[y_column]

    # Create decision tree.
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=100)
    clf_gini = DecisionTreeClassifier(criterion="gini", random_state=100, max_depth=15, min_samples_leaf=100,
                                      min_samples_split=50)
    clf_gini.fit(x_train, y_train)

    print("   Tree size: %s" % clf_gini.tree_.capacity)

    print("   Accuracy of decision tree: " + str(accuracy_score(y_test, clf_gini.predict(x_test)) * 100))

    # Convert decision tree to image.
    dot_file = open(PATH + filename + ".dot", "w")
    export_graphviz(clf_gini, out_file=dot_file, filled=True, rounded=True, special_characters=True,
                    feature_names=X.columns)
    dot_file.close()
    system("cd output & dot -Tpng " + filename + ".dot -o " + filename + ".png & cd ..")


@deprecated(version='0.01', reason="You should use the own generated data")
def all_results(do_filter=False):
    """
    Run the decision tree script for all results.
    I.e. the project analyzed by the original paper. (all.csv)
    @deprecated The method is not tested anymore and might not work.
    """
    global PATH

    # Read the data.
    data = pd.read_csv('all.csv', sep=',')

    if do_filter:
        # Filter the, according to the paper, significant columns.
        data = [['is_public', 'is_static', 'is_void', 'is_nested', 'method_length',
                 'nested_depth', 'direct_test_no', 'test_distance', 'assertion',
                 '(cond)', '(cond(cond))', '(cond(loop))', '(loop)', '(loop(cond))',
                 '(loop(loop))', 'non_void_percent', 'getter_percent',
                 'assertion-McCabe', 'assertion-density', 'COMP', 'NOCL', 'NOS',
                 'HLTH', 'HVOC', 'HEFF', 'HBUG', 'CREF', 'XMET', 'LMET', 'NLOC',
                 'VDEC', 'TDN', 'NAND', 'LOOP', 'MOD', 'NOPR']]

    # Prepend an index column used as value for Y.
    data.columns = [int(col) + 1 for col in data.columns]
    data['idx'] = range(0, len(data))

    create_tree(filename='all_d_tree_' + ('filtered' if do_filter else 'unfiltered'), data=data)
    print("   Created decision tree for [all results]")


def our_results(do_filter=False, do_classify=True):
    """
    Run the decision tree script for our results.
    I.e. the projects that we analyzed with the mutant_observer.
    """
    global PATH, PROJECTS

    project_count = 0
    # Read the data.
    for project in PROJECTS:
        path = 'JHawkStarter/Output/' + project + '_all_result.csv'
        if project_count == 0:
            # Read the first project
            data = pd.read_csv(path, sep=';', na_filter=False)
            prev_columns = pd.read_csv(path, sep=';', nrows=0)
        else:
            data = pd.concat([data, pd.read_csv(path, sep=';', na_filter=False)])
            new_columns = pd.read_csv(path, sep=';', nrows=0)
            # Check if columns are equal of all dataframes.
            if not np.array_equal(prev_columns.columns, new_columns.columns):
                print("Columns should be equal.")
                exit(1)
            prev_columns = new_columns
        project_count += 1

    data['class'] = data.apply(lambda row: int(row['total_mut'] - row['kill_mut'] > 0), axis=1)
    if do_filter:
        data['non_void_percent'] = data['void_no'] / data['total_method_no']
        data['getter_percent'] = data['getter_no'] / data['total_method_no']
        data['assertion-McCabe'] = data['assertionNo'] / data['COMP']
        data['assertion-density'] = data['assertionNo'] / data['testNLOC']
        data['assertion-density'] = data['assertion-density'].fillna(0) # assertion-density may be NaN.

        columns = ['full_name', 'is_public', 'is_static', 'is_void', 'is_nested', 'method_length', 'nested_depth',
                     'direct_test_no', 'test_distance', 'assertionNo', '(cond)', '(cond(cond))', '(cond(loop))',
                     '(loop)', '(loop(cond))', '(loop(loop))', 'non_void_percent', 'getter_percent', 'assertion-McCabe',
                     'assertion-density', 'COMP', 'NOCL', 'NOS', 'HLTH', 'HVOC', 'HEFF', 'HBUG', 'CREF', 'XMET', 'LMET',
                     'NLOC', 'VDEC', 'TDN', 'NAND', 'LOOP', 'MOD', 'NOPR']
        if do_classify:
            columns[0] = 'class'

        # Filter the, according to the paper, significant columns.
        data = data[columns]
    else:
        # Convert the method sequence column to encoded integers.
        le = LabelEncoder()
        data['method_sequence'] = le.fit_transform(data['method_sequence'])

    # Convert strings of booleans to actual booleans.
    data = data.replace({'true': True, 'false': False})

    create_tree(filename='all_our_d_tree_' + ('class' if do_classify else 'noclass'), data=data, do_classify = do_classify)
    print("   Created decision tree for [our results]")


if __name__ == '__main__':
    """
    Decision tree script main.
    """
    if not os.path.exists(PATH):
        os.makedirs(PATH)

    main()
