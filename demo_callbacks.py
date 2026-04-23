"""
This file is forked from apps/dash-clinical-analytics/app.py under the following license

MIT License

Copyright (c) 2019 Plotly

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Modifications are licensed under

Apache License, Version 2.0
(see ./LICENSE for details)

"""

import pathlib
import time

import dash
from dash import MATCH
from src.demo_enums import Model, SolverType
import plotly.graph_objs as go
from dash import ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


from demo_configs import (
    CLASSICAL_TAB_LABEL,
    DWAVE_TAB_LABEL,
    RESOURCE_NAMES,
    SCENARIOS,
)
from src.generate_charts import generate_gantt_chart, generate_output_table, get_empty_figure, get_minimum_task_times
from src.job_shop_scheduler import run_shop_scheduler
from src.model_data import JobShopData

BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("input").resolve()


@dash.callback(
    Output({"type": "to-collapse-class", "index": MATCH}, "className"),
    Output({"type": "collapse-trigger", "index": MATCH}, "aria-expanded"),
    inputs=[
        Input({"type": "collapse-trigger", "index": MATCH}, "n_clicks"),
        State({"type": "to-collapse-class", "index": MATCH}, "className"),
    ],
    prevent_initial_call=True,
)
def toggle_left_column(collapse_trigger: int, to_collapse_class: str) -> tuple[str, str]:
    """Toggles a 'collapsed' class that hides and shows some aspect of the UI.

    Args:
        collapse_trigger: The (total) number of times a collapse button has been clicked.
        to_collapse_class: Current class name of the thing to collapse, 'collapsed' if not
            visible, empty string if visible.

    Returns:
        str: The new class name of the thing to collapse.
        str: The aria-expanded value.
    """

    classes = to_collapse_class.split(" ") if to_collapse_class else []
    if "collapsed" in classes:
        classes.remove("collapsed")
        return " ".join(classes), "true"
    return to_collapse_class + " collapsed" if to_collapse_class else "collapsed", "false"


@dash.callback(
    Output("solver-select", "className"),
    Output("solver-select", "value"),
    Output("last-selected-solvers", "data"),
    inputs=[
        Input("model-select", "value"),
        State("solver-select", "value"),
        State("last-selected-solvers", "data"),
    ],
    prevent_initial_call=True,
)
def update_solver_options(
    model: int, selected_solvers: list[int], last_selected_solvers: list[int]
) -> tuple[str, list[int], list[int]]:
    """Hides and shows classical solver option using 'hide-classic' class

    Args:
        model_value: Currently selected model from model-select dropdown.
        selected_solvers: Currently selected solvers.
        last_selected_solvers: Previously selected solvers.

    Returns:
        str: The new class name of the solver-select checklist.
        list: Unselects MIP and selects Hybrid or updates to previously selected solvers.
        list: Updates last_selected_solvers with the list of solvers that were selected before updating.
    """
    model = Model(int(model))

    if model is Model.QM:
        return "hide-classic", [SolverType.HYBRID.value], selected_solvers
    return "", last_selected_solvers, dash.no_update


@dash.callback(
    Output("dwave-tab", "children", allow_duplicate=True),
    Output("mip-tab", "children", allow_duplicate=True),
    Output("dwave-tab", "disabled", allow_duplicate=True),
    Output("mip-tab", "disabled", allow_duplicate=True),
    Output("run-button", "style", allow_duplicate=True),
    Output("cancel-button", "style", allow_duplicate=True),
    Output("running-dwave", "data", allow_duplicate=True),
    Output("running-classical", "data", allow_duplicate=True),
    Output("tabs", "value"),
    [
        Input("run-button", "n_clicks"),
        Input("cancel-button", "n_clicks"),
        State("solver-select", "value"),
    ],
    prevent_initial_call=True,
)
def update_tab_loading_state(
    run_click: int, cancel_click: int, solvers: list[str]
) -> tuple[str, str, bool, bool, str, str, str, str, bool, bool, str]:
    """Updates the tab loading state after the run button
    or cancel button has been clicked.

    Args:
        run_click: The number of times the run button has been clicked.
        cancel_click: The number of times the cancel button has been clicked.
        solvers: The list of selected solvers.

    Returns:
        str: The label for the D-Wave tab.
        str: The label for the Classical tab.
        bool: True if D-Wave tab should be disabled, False otherwise.
        bool: True if Classical tab should be disabled, False otherwise.
        str: Class name for the D-Wave tab.
        str: Class name for the Classical tab.
        dict: Run button style.
        dict: Cancel button style.
        bool: Whether Hybrid is running.
        bool: Whether MIP is running.
        str: The value of the tab that should be active.
    """

    if ctx.triggered_id == "run-button" and run_click > 0:
        run_hybrid = f"{SolverType.HYBRID.value}" in solvers
        run_mip = f"{SolverType.MIP.value}" in solvers

        return (
            "Loading..." if run_hybrid else dash.no_update,
            "Loading..." if run_mip else dash.no_update,
            True if run_hybrid else dash.no_update,
            True if run_mip else dash.no_update,
            {"display": "none"},
            {},
            run_hybrid,
            run_mip,
            "input-tab",
        )
    if ctx.triggered_id == "cancel-button" and cancel_click > 0:
        return (
            DWAVE_TAB_LABEL,
            CLASSICAL_TAB_LABEL,
            dash.no_update,
            dash.no_update,
            {},
            {"display": "none"},
            False,
            False,
            dash.no_update,
        )
    raise PreventUpdate


@dash.callback(
    Output("run-button", "style"),
    Output("cancel-button", "style"),
    background=True,
    inputs=[
        Input("running-dwave", "data"),
        Input("running-classical", "data"),
    ],
    prevent_initial_call=True,
)
def update_button_visibility(running_dwave: bool, running_classical: bool) -> tuple[dict, dict]:
    """Updates the visibility of the run and cancel buttons.

    Args:
        running_dwave: Whether the D-Wave solver is running.
        running_classical: Whether the Classical solver is running.

    Returns:
        dict: Run button style.
        dict: Cancel button style.
    """
    if not running_classical and not running_dwave:
        return {}, {"display": "none"}

    return {"display": "none"}, {} 


@dash.callback(
    Output("optimized-gantt-chart", "figure"),
    Output("dwave-summary-table", "figure"),
    Output("dwave-tab", "className"),
    Output("dwave-tab", "children"),
    Output("dwave-tab", "disabled"),
    Output("running-dwave", "data"),
    background=True,
    inputs=[
        Input("run-button", "n_clicks"),
        State("model-select", "value"),
        State("solver-select", "value"),
        State("scenario-select", "value"),
        State("solver-time-limit", "value"),
    ],
    cancel=[Input("cancel-button", "n_clicks")],
    prevent_initial_call=True,
)
def run_optimization_cqm(
    run_click: int, model: int, solvers: list[int], scenario: str, time_limit: int
) -> tuple[go.Figure, go.Figure, str, str, bool, bool]:
    """Runs optimization using the D-Wave hybrid solver.

    Args:
        run_click: The number of times the run button has been clicked.
        model: The model to use for the optimization.
        solvers: The solvers that have been selected.
        scenario: The scenario to use for the optimization.
        time_limit: The time limit for the optimization.

    Returns:
        go.Figure: Gantt chart for the D-Wave hybrid solver.
        go.Figure: Results table for the D-Wave hybrid solver.
        str: Class name for the D-Wave tab.
        str: The label for the D-Wave tab.
        bool: True if D-Wave tab should be disabled, False otherwise.
        bool: Whether D-Wave solver is running.
    """
    if ctx.triggered_id != "run-button" or run_click == 0:
        raise PreventUpdate

    if f"{SolverType.HYBRID.value}" not in solvers:
        return (dash.no_update, dash.no_update, "tab", DWAVE_TAB_LABEL, dash.no_update, False)

    start = time.perf_counter()
    model = Model(int(model))
    model_data = JobShopData()
    filename = SCENARIOS[scenario]

    model_data.load_from_file(DATA_PATH.joinpath(filename), resource_names=RESOURCE_NAMES)

    results = run_shop_scheduler(
        model_data,
        use_mip_solver=False,
        allow_quadratic_constraints=(model is Model.QM),
        solver_time_limit=time_limit,
    )

    fig = generate_gantt_chart(results)
    table = generate_output_table(results["Finish"].max(), time_limit, time.perf_counter() - start)

    return (fig, table, "tab-success", DWAVE_TAB_LABEL, False, False)


@dash.callback(
    Output("mip-gantt-chart", "figure"),
    Output("mip-summary-table", "figure"),
    Output("mip-tab", "className"),
    Output("mip-tab", "children"),
    Output("mip-tab", "disabled"),
    Output("running-classical", "data"),
    background=True,
    inputs=[
        Input("run-button", "n_clicks"),
        State("solver-select", "value"),
        State("scenario-select", "value"),
        State("solver-time-limit", "value"),
    ],
    cancel=[Input("cancel-button", "n_clicks")],
    prevent_initial_call=True,
)
def run_optimization_mip(
    run_click: int, solvers: list[int], scenario: str, time_limit: int
) -> tuple[go.Figure, go.Figure, str, str, bool, bool]:
    """Runs optimization using the COIN-OR Branch-and-Cut solver.

    Args:
        run_click: The number of times the run button has been clicked.
        solvers: The solvers that have been selected.
        scenario: The scenario to use for the optimization.
        time_limit: The time limit for the optimization.

    Returns:
        go.Figure: Gantt chart for the Classical solver.
        go.Figure: Results table for the Classical solver.
        str: Class name for the Classical tab.
        str: The label for the Classical tab.
        bool: True if Classical tab should be disabled, False otherwise.
        bool: Whether Classical solver is running.
    """
    if ctx.triggered_id != "run-button" or run_click == 0:
        raise PreventUpdate

    if f"{SolverType.MIP.value}" not in solvers:
        return (dash.no_update, dash.no_update, "tab", CLASSICAL_TAB_LABEL, dash.no_update, False)

    start = time.perf_counter()
    model_data = JobShopData()
    filename = SCENARIOS[scenario]

    model_data.load_from_file(DATA_PATH.joinpath(filename), resource_names=RESOURCE_NAMES)

    results = run_shop_scheduler(
        model_data,
        use_mip_solver=True,
        allow_quadratic_constraints=False,
        solver_time_limit=time_limit,
    )

    if results.empty:
        fig = get_empty_figure("No solution found for Classical solver")
        table = generate_output_table(0, time_limit, time.perf_counter() - start)
        return (fig, table, "tab-fail", CLASSICAL_TAB_LABEL, False, False)

    fig = generate_gantt_chart(results)
    mip_table = generate_output_table(results["Finish"].max(), time_limit, time.perf_counter() - start)
    return (fig, mip_table, "tab-success", CLASSICAL_TAB_LABEL, False, False)


@dash.callback(
    Output("unscheduled-gantt-chart", "figure"),
    [
        Input("scenario-select", "value"),
    ],
)
def generate_unscheduled_gantt_chart(scenario: str) -> go.Figure:
    """Generates a Gantt chart of the unscheduled tasks for the given scenario.

    Args:
        scenario: The name of the scenario; must be a key in SCENARIOS.

    Returns:
        go.Figure: A Plotly figure object with the input data
    """
    model_data = JobShopData()
    model_data.load_from_file(DATA_PATH.joinpath(SCENARIOS[scenario]), resource_names=RESOURCE_NAMES)
    df = get_minimum_task_times(model_data)
    fig = generate_gantt_chart(df)
    return fig
