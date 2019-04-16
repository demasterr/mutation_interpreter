from typing import Dict
import pandas as pd

# Indicate which projects to analyze.
PROJECTS = {
    "jfreechart": True,
    "minimal-json": True,
    "jackson-core": True,
    "dnainator": True,
    "PoliteHarmony": False
}
# Indicate whether you only want to display violations of anti-patterns when there are surviving mutants.
SURVIVING_ONLY = True

# Indicate which rule to focus. Disable by setting this to a negative number.
FOCUS_RULE = -1


# ---------- End of configuration -------------


def check_method_smell(m: Dict) -> None:
    """
    Check for method smells with the anti-pattern rules.
    :param m: Dictionary of properties per found per method with the mutant_observer.
    """
    assertion_density = 0 if m['testNLOC'] == 0 else m['assertionNo'] / m['testNLOC']
    non_void_percent = 0 if m['total_method_no'] == 0 else 1 - (m['void_no'] / m['total_method_no'])
    assertion_McCabe = m['assertionNo'] / m['COMP']

    if m['test_distance'] > 5 and m['(loop(loop))'] <= 0 and not m['is_nested'] and not m['is_public'] \
            and m['XMET'] > 4 and m['(loop)'] <= 0 and m['NOCL'] <= 9 and (m['void_no'] / m['total_method_no']) <= 0.42:
        print_violation(1, m)
    if m['test_distance'] > 5 and m['(loop(loop))'] <= 0 and not m['is_nested'] and not m['is_public'] \
            and m['XMET'] > 4 and m['(loop)'] <= 0 and m['NOCL'] > 9:
        print_violation(2, m)
    if m['test_distance'] > 5 and m['(loop(loop))'] <= 0 and not m['is_nested'] and m['is_public'] \
            and 0 < m['NOCL'] <= 4 and not m['is_static'] and (m['getter_no'] / m['total_method_no']) <= 0.01 \
            and m['HBUG'] <= 0.02 and m['method_length'] > 3:
        print_violation(3, m)
    if m['test_distance'] > 5 and m['(loop(loop))'] <= 0 and not m['is_nested'] and m['is_public'] \
            and m['(cond)'] <= 0 and not m['is_static'] and m['LMET'] <= 1 and m['NOCL'] > 8 and m['NOPR'] > 5 \
            and m['is_void']:
        print_violation(4, m)
    if m['test_distance'] <= 5 and m['is_void'] and m['nested_depth'] <= 0 and m['NOS'] <= 2 and \
            assertion_density <= 0.14 and m['MOD'] > 1:
        print_violation(5, m)
    if m['test_distance'] <= 5 and m['is_void'] and m['nested_depth'] <= 0 and m['NOS'] > 2 and \
            assertion_density <= 0.22 and m['CREF'] > 1 and m['XMET'] > 0 and m['VDEC'] == 0 and m['NOCL'] <= 12:
        print_violation(6, m)

    # ---- RULES DERIVED FROM OUR DECISION TREE. ----
    if m['NOS'] > 2.5 and m['XMET'] == 0 and m['VDEC'] == 0:
        print_violation(7, m)
    if m['test_distance'] > 4.5 and m['NOPR'] <= 5.5:
        print_violation(8, m)

    # Identifies methods that already have many asserts, is highly testable but was missing branches.
    if m['test_distance'] <= 4.5 < m['assertionNo'] and non_void_percent > 0.132:
        print_violation(9, m)
    # Identifies functions which are likely to need many test but are most often not hard to test.
    if m['LMET'] >= 0.5 and not m['is_void'] and assertion_McCabe > 2.875:
        print_violation(10, m)



def print_violation(rule, m):
    """
    Print a violation message to the console.
    :param rule: Rule that is violated.
    :param m: Dict containing the method row.
    """
    global SURVIVING_ONLY, FOCUS_RULE
    survived = m['total_mut'] - m['kill_mut']
    # If only the surviving should be displayed and there is no surviving mutant, ignore.
    if SURVIVING_ONLY and survived == 0:
        return
    # If focus is enabled and rule is not the focused rule, ignore.
    if FOCUS_RULE > 0 and FOCUS_RULE != rule:
        return
    print('Rule ' + str(rule) + ' violation (to kill: ' + str(survived) + ') on method ' + m['full_name'])


if __name__ == '__main__':
    """
    Search for rule violations per method.
    """
    for project, enabled in PROJECTS.items():
        if enabled:
            methods = pd.read_csv('JHawkStarter/Output/' + project + '_all_result.csv', sep=';').to_dict(
                orient='records')

            for method in methods:
                check_method_smell(method)
