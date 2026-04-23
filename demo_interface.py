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

from __future__ import annotations
from enum import EnumMeta

from dash import dcc, html

from demo_configs import (
    CLASSICAL_TAB_LABEL,
    DESCRIPTION,
    DWAVE_TAB_LABEL,
    MAIN_HEADER,
    SCENARIOS,
    SOLVER_TIME,
    THUMBNAIL
)
from src.demo_enums import Model, SolverType
import dash_mantine_components as dmc


THEME_COLOR = "#2d4376"


def dropdown(label: str, id: str, options: list) -> html.Div:
    """Dropdown element for option selection.

    Args:
        label: The title that goes above the dropdown.
        id: A unique selector for this element.
        options: A list of dictionaries of labels and values.
    """
    return html.Div(
        className="dropdown-wrapper",
        children=[
            html.Label(label, htmlFor=id),
            dmc.Select(
                id=id,
                data=options,
                value=options[0]["value"],
                allowDeselect=False,
            ),
        ],
    )

def checklist(label: str, id: str, options: list, values: list, inline: bool = True) -> html.Div:
    """Checklist element for option selection.

    Args:
        label: The title that goes above the checklist.
        id: A unique selector for this element.
        options: A list of dictionaries of labels and values.
        values: A list of values that should be preselected in the checklist.
        inline: Whether the options of the checklist are displayed beside or below each other.
    """
    return html.Div(
        className="checklist-wrapper",
        children=[
            dmc.CheckboxGroup(
                id=id,
                className=f"checklist{' checklist--inline' if inline else ''}",
                label=label,
                value=values,
                children=dmc.Group(
                    [
                        dmc.Checkbox(label=option["label"], value=option["value"], color=THEME_COLOR)
                        for option in options
                    ],
                ),
            ),
        ],
    )


# def generate_graph(visible: bool, type: str, index: int) -> html.Div:
#     """Generates graph either hidden or visible."""
#     return html.Div(
#         id={
#             "type": f"gantt-chart-{'visible' if visible else 'hidden'}-wrapper",
#             "index": index,
#         },
#         className="graph" if visible else "display-none",
#         children=[
#             dcc.Graph(
#                 id={"type": f"gantt-chart-{type}", "index": index},
#                 responsive=True,
#                 config={"displayModeBar": False},
#             ),
#         ],
#     )


def generate_options(options: list | EnumMeta) -> list[dict]:
    """Generates options for dropdowns, checklists, radios, etc."""
    if isinstance(options, EnumMeta):
        return [
            {"label": option.label, "value": f"{option.value}"} for option in options
        ]

    return [{"label": f"{option}", "value": f"{option}"} for option in options]


def generate_settings_form() -> html.Div:
    """This function generates settings for selecting the scenario, model, and solver.

    Returns:
        html.Div: A Div containing the settings for selecting the scenario, model, and solver.
    """

    scenario_options = generate_options(SCENARIOS)
    model_options = generate_options(Model)
    solver_options = generate_options(SolverType)

    return html.Div(
        id="control-card",
        children=[
            dropdown(
                "Scenario (jobs x resources)",
                "scenario-select",
                scenario_options,
            ),
            dropdown(
                "Model",
                "model-select",
                model_options,
            ),
            checklist(
                "Solver",
                "solver-select",
                solver_options,
                values=[solver_options[0]["value"]],
            ),
            html.Label("Solver Time Limit (seconds)", htmlFor="solver-time-limit"),
            dmc.NumberInput(
                id="solver-time-limit",
                type="number",
                **SOLVER_TIME,
            ),
        ],
    )


def generate_run_buttons() -> html.Div:
    """Run and cancel buttons to run the optimization."""
    return html.Div(
        id="button-group",
        children=[
            html.Button("Run Optimization", id="run-button", className="button"),
            html.Button(
                "Cancel Optimization",
                id="cancel-button",
                className="button",
                style={"display": "none"},
            ),
        ],
    )


def create_interface():
    """Set the application HTML."""
    return html.Div(
        id="app-container",
        children=[
            html.A(  # Skip link for accessibility
                "Skip to main content",
                href="#main-content",
                id="skip-to-main",
                className="skip-link",
                tabIndex=1,
            ),
            dcc.Store("last-selected-solvers"),
            dcc.Store("running-dwave"),
            dcc.Store("running-classical"),
            # Settings and results columns
            html.Main(
                className="columns-main",
                id="main-content",
                children=[
                    # Left column
                    html.Div(
                        id={"type": "to-collapse-class", "index": 0},
                        className="left-column",
                        children=[
                            html.Div(
                                className="left-column-layer-1",  # Fixed width Div to collapse
                                children=[
                                    html.Div(
                                        className="left-column-layer-2",  # Padding and content wrapper
                                        children=[
                                            html.Div(
                                                [
                                                    html.H1(MAIN_HEADER),
                                                    html.P(DESCRIPTION),
                                                ],
                                                className="title-section",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        html.Div(
                                                            [
                                                                generate_settings_form(),
                                                                generate_run_buttons(),
                                                            ],
                                                            className="settings-and-buttons",
                                                        ),
                                                        className="settings-and-buttons-wrapper",
                                                    ),
                                                    # Left column collapse button
                                                    html.Div(
                                                        html.Button(
                                                            id={
                                                                "type": "collapse-trigger",
                                                                "index": 0,
                                                            },
                                                            className="left-column-collapse",
                                                            title="Collapse sidebar",
                                                            children=[
                                                                html.Div(className="collapse-arrow")
                                                            ],
                                                            **{"aria-expanded": "true"},
                                                        ),
                                                    ),
                                                ],
                                                className="form-section",
                                            ),
                                        ],
                                    )
                                ],
                            ),
                        ],
                    ),
                                        # Right column
                    html.Div(
                        className="right-column",
                        children=[
                            dmc.Tabs(
                                id="tabs",
                                value="input-tab",
                                color="white",
                                children=[
                                    html.Header(
                                        className="banner",
                                        children=[
                                            html.Nav(
                                                [
                                                    dmc.TabsList(
                                                        [
                                                            dmc.TabsTab("Input", value="input-tab"),
                                                            dmc.TabsTab(
                                                                DWAVE_TAB_LABEL,
                                                                value="dwave-tab",
                                                                id="dwave-tab",
                                                                disabled=True,
                                                            ),
                                                            dmc.TabsTab(
                                                                CLASSICAL_TAB_LABEL,
                                                                value="mip-tab",
                                                                id="mip-tab",
                                                                disabled=True,
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            html.Img(src=THUMBNAIL, alt="D-Wave logo"),
                                        ],
                                    ),
                                    dmc.TabsPanel(
                                        value="input-tab",
                                        tabIndex="12",
                                        children=[
                                            html.Div(
                                                className="tab-content-wrapper",
                                                children=[
                                                    html.Div([
                                                        html.H2(
                                                            "Unscheduled Jobs and Resources",
                                                            className="gantt-title",
                                                        ),
                                                        dcc.Loading(
                                                            parent_className="graph-wrapper",
                                                            type="circle",
                                                            delay_show=300,
                                                            color=THEME_COLOR,
                                                            children=[
                                                                dcc.Graph(
                                                                    id="unscheduled-gantt-chart",
                                                                    responsive=True,
                                                                    config={"displayModeBar": False},
                                                                ),
                                                            ],
                                                        )
                                                    ])
                                                    
                                                ]
                                            )
                                        ],
                                    ),
                                    dmc.TabsPanel(
                                        value="dwave-tab",
                                        tabIndex="13",
                                        children=[
                                            html.Div(
                                                className="tab-content-wrapper",
                                                children=[
                                                    html.Div([
                                                        html.H2(
                                                            "D-Wave Hybrid Solver",
                                                            className="gantt-title",
                                                        ),
                                                        dcc.Loading(
                                                            parent_className="graph-wrapper",
                                                            type="circle",
                                                            delay_show=300,
                                                            color=THEME_COLOR,
                                                            children=[
                                                                dcc.Graph(
                                                                    id="optimized-gantt-chart",
                                                                    responsive=True,
                                                                    config={"displayModeBar": False},
                                                                ),
                                                            ]
                                                        )
                                                    ]),
                                                    dcc.Graph(id="dwave-summary-table"),
                                                ],
                                            )
                                        ],
                                    ),
                                    dmc.TabsPanel(
                                        value="mip-tab",
                                        tabIndex="13",
                                        children=[
                                            html.Div(
                                                className="tab-content-wrapper",
                                                children=[
                                                    html.Div([
                                                        html.H2(
                                                            "Classical Solver (COIN-OR Branch-and-Cut)",
                                                            className="gantt-title",
                                                        ),
                                                        dcc.Loading(
                                                            parent_className="graph-wrapper",
                                                            type="circle",
                                                            delay_show=300,
                                                            color=THEME_COLOR,
                                                            children=[
                                                                dcc.Graph(
                                                                    id="mip-gantt-chart", responsive=True,
                                                                    config={"displayModeBar": False},
                                                                ),
                                                            ]
                                                        )
                                                    ]),
                                                    dcc.Graph(id="mip-summary-table"),
                                                ],
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ],
    )
