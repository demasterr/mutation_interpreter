# Mutation interpreter
The mutation interpreter is a extension on the
[mutation observer](https://github.com/qianqianzhu/mutation_observer).
The scripts in this repository assume the use of this prototype project.
Furthermore, a license of JHawkStarter is required to generate additional
metrics required by the mutation observer. A license for JHawkStarter can
be obtained from [http://www.virtualmachinery.com/](http://www.virtualmachinery.com/).
JHawkStarter is assumed to be placed inside this repository in a folder called
`JHawkStarter/`.
This repository is meant as a prototype and should not be assumed to be stable
for daily use.

## Setup `main.py`
Main.py is used to check each anti-pattern rule for violations in projects.
The anti-pattern rules are generated read from the CSV file created with
the [mutation observer](https://github.com/qianqianzhu/mutation_observer).
The file is assumed to be located in `JHawkStarter/Output/`. All output generated
with JHawkStarter should be situated in this folder. The naming of the CSV
generated by the mutation observer is assumed to be `[project_name]_all_results.csv`.

For analyzing a specific project, the `PROJECTS` variable can be adapted at the
top of the file. Each key in the Dict set to `True` is assumed to be analyzed.
To only show the violations for which mutants have survived, the `SURVIVING_ONLY`
variable can be set to `True`. To focus on only one rule, the `FOCUS_RULE` variable
can be used. To disable any focus, set the variable to any arbitrary negative
number.

## Setup `decision.py`
Decision.py is used to generate a decision tree which enables for new
anti-pattern rule generation. The decision tree is based on the output
provided by the mutation observer.
Similar to the main.py script from above, the output of the JHawk and
mutation observer is assumed to
be located in the `JHawkStarter/Output` folder. The output CSV from the
mutation observer is again assumed to be `[project_name]_all_results.csv`.

To analyze different projects, one can alter the `PROJECTS` variable at the
top of the file. The list contains all projects to be considered for the
generation of the decision tree.

## Refactors.md
In refactors.md all refactors found with the above scripts are listed. Each of
these refactors are based on one of the rules provided in main.py. Please note
that we do not hold any premise on the quality of each refactor.
