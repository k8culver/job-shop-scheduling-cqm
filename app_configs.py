'''
This file stores input parameters for the app.
'''

import json

HTML_CONFIGS = {
    'title': 'Job Shop Scheduling Demo',
    'main_header': "Job Shop Scheduling",
    'welcome_message': "Welcome to the Job Shop Scheduling Dashboard",
    'welcome_instructions': "Run the job shop scheduling problem for several different scenarios. Explore the Gantt Chart for solution details",
    "solver_options": {
        "min_time_seconds": 5,
        "max_time_seconds": 300,
        "time_step_seconds": 5,
        "default_time_seconds": 5
    },
    "solver_messages": {
        "highs": {
            "quadratic_error": "Unable to run HiGHS solver with quadratic constraints",
            "no_solution": "No solution found for HiGHS solver",
            "solver_not_chosen": "Select HiGHS Classical Solver to run this solver"
            },
        'dwave': {
            "no_solution": "No solution found for D-Wave solver",
            "solver_not_chosen": "Select D-Wave Hybrid Solver to run this solver"
            }
    },
    "tabs": {
        "input": {
            "name": "Input",
            "header": "Jobs to be Scheduled",
        },
        "classical": {
            "name": "Classical",
            "header": "HiGHS Classical Solver",
        },
        "dwave": {
            "name": "D-Wave",
            "header": "D-Wave Hybrid Solver",
        }, 
    }
}


# The list of scenarios that the user can choose from in the app
SCENARIOS = {
    '15x15': "taillard15_15.txt",
    '20x15': "taillard20_15.txt",
    '20x20': "taillard20_20.txt",
    '30x15': "taillard30_15.txt",
    '30x20': "taillard30_20.txt",
    '50x15': "taillard50_15.txt",
    '50x20': "taillard50_20.txt",
}

# The list of models that the user can choose from in the app
MODEL_OPTIONS = {
    "Mixed Integer Linear Model": "MILP",
    "Mixed Integer Quadratic Model": "MIQP",
}

# The list of solvers that the user can choose from in the app
SOLVER_OPTIONS = {
    "D-Wave Hybrid Solver": "Hybrid",
    "HiGHS Classical Solver": "HiGHS"
}

# The list of resources that the user can choose from in the app
RESOURCE_NAMES = json.load(open('./src/data/resource_names.json', 'r'))['industrial']