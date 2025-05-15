import dash
import pandas as pd
from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

'''
AUTHOR: Josh Swan
DATE: 07/06/2023

This file declares the dashboard class which powers the visualisations that run in the main.py flask app. The dash app
that runs the data table and visualisation is declared here and runs within the flask app in main.py.
'''

class dashboard:
    def __init__(self, server, df, references, routes):
        self.dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                                  suppress_callback_exceptions=True, routes_pathname_prefix=routes, server=server)
        self.df = df
        self.references = references
        self.setup_layout()
        self.setup_callbacks()
        self.visualisation_callbacks()
        self.routes = routes

        self.ZERO = '\u200B'  # or '\u2060', whichever you’ve settled on

    def clean_label(self, s: str) -> str:
        # remove zero-width marks *and* your "(inaccessible)" tag
        return s.replace(self.ZERO, '').replace('(inaccessible)', '')

    def setup_layout(self):
        self.dash_app.layout = dbc.Container(fluid=True, children=[
            html.Div([
                html.Link(rel='icon', href='/assets/bsi.ico'),
                html.Br(),
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.H3("Lookup Table", style={'fontFamily': 'Noto Serif'}),
                            dcc.Input(id='global-search', type='text', placeholder='Global search...', style={"margin-bottom": "20px", "width": "75%"}),
                            dbc.Button("Search", id="search-button", className="btn", style={"background-color":"#24262e"}),
                            dbc.Button("Clear", id="clear-button", outline=True, color="secondary"),

                            html.Div(id='table-info-div', style={"font-weight": "bold", "padding-top": "10px"}),  # This displays record count for the table

                            dash_table.DataTable(
                                id='table',
                                columns=[{'name': i, 'id': i, 'deletable': False, 'selectable': False} for i in self.df.columns],
                                data=self.df.to_dict('records'),
                                filter_action='native',
                                sort_action='native',
                                sort_mode='multi',
                                column_selectable='single',
                                row_selectable="single", # was multi
                                row_deletable=False,
                                selected_columns=[],
                                selected_rows=[0],
                                page_action='native',
                                filter_options={"case": "insensitive"},# This makes the filter case-insensitive by default
                                page_current=0,
                                editable=False,
                                page_size=10,
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '15px',
                                    'user-select': 'text'
                                },
                                style_cell={
                                    'height': 'auto',
                                    'whiteSpace': 'normal',
                                    'padding': '10px',
                                    'fontFamily': 'Noto Sans',
                                    'fontSize': '11px',
                                    "maxWidth": 150,
                                },

                                style_cell_conditional=[
                                                           {'if': {'column_id': c}, 'textAlign': 'left'} for c in
                                                           self.df.columns
                                                       ] + [
                                                           {'if': {'column_id': 'Gov Associated Org'}, 'width': '200px'}
                                                           # Adjust width as needed
                               ],
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'borderBottom': '3px solid gray',
                                    'boxShadow': '3px 3px 6px 1px rgba(0,0,0,0.5)',
                                    'fontFamily': 'Noto Sans'
                                },
                                style_table={
                                    'overflowX': 'hidden',
                                    'border': '2px solid gray',
                                    'boxShadow': '3px 3px 6px 1px rgba(0,0,0,0.5)',
                                    'minWidth': '100%',
                                    "tableLayout": "fixed",   # Force columns to share the container width
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    },
                                    {
                                        'if': {
                                            'filter_query': '{Identifier} contains "A" || {Title} contains "A" || {ICS} contains "A" || {Published} contains "A" || {Type} contains "A" || {Designated Standard} contains "A" || {Connections} contains "A"',
                                            'column_id': 'Parent ID'
                                        },
                                        'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                        'border': '1px solid rgba(0, 116, 217, 1)'
                                    }
                                ],
                                tooltip_data=[
                                    {
                                        column: {'value': str(value), 'type': 'markdown'}
                                        for column, value in row.items()
                                    } for row in self.df.to_dict('records')
                                ],
                                tooltip_duration=1000000,
                                css=[{
                                    'selector': '.dash-spreadsheet td div',
                                    'rule': '''
                                    display: inline;
                                    white-space: inherit;
                                    overflow: inherit;
                                    text-overflow: inherit;
                                    line-height: 15px;
                                    max-height: 30px; min-height: 30px; height: 30px;
                                    display: block;
                                    overflow-y: auto;
                                    '''
                                }, {
                                    'selector': '.dash-spreadsheet tr:hover',
                                    'rule': 'background-color: rgba(0, 116, 217, 0.1) !important;'
                                }],
                                # supposed to allow a dropdown of fields but didn't work
                                # dropdown={'Status': {
                                #     'options': [{'label': i, 'value': i} for i in self.df['Status'].unique()]}},
                                # dropdown_conditional=[
                                #     {'if': {'column_id': 'Status'}, 'clearable': True, 'selectable': True}],
                            )
                        ]), width=12),
                ]),
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            html.H3("Layer Explorer", style={'fontFamily': 'Noto Serif'}),

                            html.Div(id='table-two-info-div', style={"font-weight": "bold", "padding-top": "10px"}),  # This displays record count for the table-two

                            dash_table.DataTable(
                                id='table_two',
                                columns=[{'name': i, 'id': i, 'deletable': False, 'selectable': False} for i in ["Identifier", "Title"]],
                                data=[],
                                filter_action='native',
                                sort_action='native',
                                sort_mode='multi',
                                column_selectable='single',
                                row_selectable="single", # was multi
                                row_deletable=False,
                                selected_columns=[],
                                selected_rows=[0],
                                page_action='native',
                                filter_options={"case": "insensitive"},
                                # This makes the filter case-insensitive by default
                                page_current=0,
                                editable=False,
                                page_size=10,
                                style_data={
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'lineHeight': '15px',
                                    'user-select': 'text'
                                },
                                style_cell={
                                    'height': 'auto',
                                    'whiteSpace': 'normal',
                                    'padding': '10px',
                                    'fontFamily': 'Noto Sans',
                                    'fontSize': '11px',
                                },
                                style_cell_conditional=[
                                    {'if': {'column_id': c}, 'textAlign': 'left'} for c in self.df.columns
                                ],
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'borderBottom': '3px solid gray',
                                    'boxShadow': '3px 3px 6px 1px rgba(0,0,0,0.5)',
                                    'fontFamily': 'Noto Sans'
                                },
                                style_table={
                                    'overflowX': 'auto',
                                    'border': '2px solid gray',
                                    'boxShadow': '3px 3px 6px 1px rgba(0,0,0,0.5)',
                                    'minWidth': '100%'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                    },
                                ],
                                tooltip_data=[],
                                tooltip_duration=1000000,
                                css=[{
                                    'selector': '.dash-spreadsheet td div',
                                    'rule': '''
                             display: inline;
                             white-space: inherit;
                             overflow: inherit;
                             text-overflow: inherit;
                             line-height: 15px;
                             max-height: 30px; min-height: 30px; height: 30px;
                             display: block;
                             overflow-y: auto;
                             '''
                                }, {
                                    'selector': '.dash-spreadsheet tr:hover',
                                    'rule': 'background-color: rgba(0, 116, 217, 0.1) !important;'
                                }],
                            ),

                            # html.Div(id='legend', children=[
                            #     html.P("Legend:", style={'fontFamily': 'Noto Sans'}),
                            #     html.Ul([
                            #         html.Li("DESIGNATED",
                            #                 style={"color": '#F6BA00', "fontSize": "18px", "fontWeight": "bold", 'fontFamily': 'Noto Sans'}),
                            #         html.Li("NORMATIVE",
                            #                 style={"color": '#030072', "fontSize": "18px", "fontWeight": "bold", 'fontFamily': 'Noto Sans'}),
                            #         html.Li("INFORMATIVE",
                            #                 style={"color": '#950200', "fontSize": "18px", "fontWeight": "bold", 'fontFamily': 'Noto Sans'})
                            #     ])
                            # ], style={'margin-top': '20px'}),
                            html.H3("Sunburst", style={'fontFamily': 'Noto Serif', 'margin-bottom': '5px', 'margin-top': '50px'}),
                            dcc.Checklist(
                                id='layer-toggle',
                                options=[{'label': ' Show Lowest Layer', 'value': 'show'}],
                                value=['show'],
                                style={'margin': '10px 0', 'fontFamily': 'Noto Sans', 'fontSize': '12pt'}
                            ),
                            dcc.Graph(id='sunburst-chart', style={"height": "1000px"}, className='graph-shadow')
                        ]), width=12)
                ])
            ], className="datatable-container"),
        ], className="container-fluid")

    def setup_callbacks(self):

        # Callbacks for showing current record range for both tables
        @self.dash_app.callback(
            Output('table-info-div', 'children'),
            [
                Input('table', 'page_current'),
                Input('table', 'page_size'),
                Input('table', 'derived_virtual_data'),
            ]
        )
        def update_table_info(page_current, page_size, rows):
            # rows is the data *after* filtering/sorting, so its length
            # is the “filtered” total. If it’s None or empty, just show 0
            if not rows:
                return "No rows to display"

            total_filtered = len(rows)
            # The table displays a slice of derived_virtual_data
            # from row indices [start-1 ... end-1]
            start = page_current * page_size + 1
            end = min((page_current + 1) * page_size, total_filtered)

            return f"Showing {start} - {end} of {total_filtered:,} records"

        @self.dash_app.callback(
            Output('table-two-info-div', 'children'),
            [
                Input('table_two', 'page_current'),
                Input('table_two', 'page_size'),
                Input('table_two', 'derived_virtual_data'),
            ]
        )
        def update_table_info_table2(page_current, page_size, rows):
            # rows is the data *after* filtering/sorting, so its length
            # is the “filtered” total. If it’s None or empty, just show 0
            if not rows:
                return "No rows to display"

            total_filtered = len(rows)
            # The table displays a slice of derived_virtual_data
            # from row indices [start-1 ... end-1]
            start = page_current * page_size + 1
            end = min((page_current + 1) * page_size, total_filtered)

            return f"Showing {start} - {end} of {total_filtered:,} records"

        #-----------------------------------------------------------------------------------------------------------

        # callback for table two
        @self.dash_app.callback(
            Output("table_two", "data"),
            Input("table", "selected_rows")
        )
        def update_table_two(selected_rows):
            if not selected_rows:
                return []

            output = []
            # Collect data for selected rows
            combined_data = self.df.iloc[selected_rows]["Identifier"].to_list()
            # print("combined_data", combined_data)

            #filtered_df = self.references[self.references["standard"].apply(self.clean_label).isin(combined_data)]
            filtered_df = self.references[(self.references["standard"].str.replace('\u200B', '').isin(combined_data)) | (self.references["parent"].str.replace('\u200B', '').isin(combined_data))].drop_duplicates(subset="standard")
            # filtered_df = self.references[self.references["parent"].str.replace('\u200B', '').isin(combined_data)]

            # print("filtered_df", filtered_df.to_string())

            output += filtered_df["standard"][filtered_df["parent"] == "Standard"].to_list()
            # print(f"output1: {output}")

            not_designated = filtered_df["parent"][filtered_df["parent"] != "Standard"].to_list()
            # print(f"not_designated1: {not_designated}")

            if len(not_designated) > 0:
                # dealing with layer 2s to find designated
                filtered_df = self.references[self.references["standard"].apply(self.clean_label).isin(not_designated)]

                output += filtered_df["standard"][filtered_df["parent"] == "Standard"].to_list()
                # print(f"output2: {output}")

                not_designated = filtered_df["parent"][filtered_df["parent"] != "Standard"].to_list()
                # print(f"not_designated2: {not_designated}")

                if len(not_designated) > 0:
                    # dealing with layer 2s to find designated
                    filtered_df = self.references[self.references["standard"].apply(self.clean_label).isin(not_designated)]

                    output += filtered_df["standard"][filtered_df["parent"] == "Standard"].to_list()
                    # print(f"output3: {output}")
                    # print("Output", output)

            combined_data = self.df[["Identifier", "Title"]][self.df["Identifier"].isin(output)]
            # print(combined_data.to_string(index=False))
            return combined_data.to_dict("records")

        @self.dash_app.callback(
            Output("table_two", "tooltip_data"),
            Input("table_two", "data")
        )
        def update_table_two_tooltips(table_two_data):
            if not table_two_data:
                return []
            return [
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                }
                for row in table_two_data
            ]

        @self.dash_app.callback(
            Output('table', 'style_data_conditional'),
            Input('global-search', 'value')
        )
        def update_styles(search_value):
            if not search_value:
                return [
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            else:
                search_values = [v.strip() for v in search_value.split(",")]

            conditions = []
            for sv in search_values:
                conditions.extend([
                    {
                        'if': {
                            'filter_query': '{{{0}}} icontains "{1}"'.format(column, sv),
                            'column_id': column
                        },
                        'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                        'border': '1px solid rgba(0, 116, 217, 1)'
                    } for column in self.df.columns
                ])
            return conditions

        @self.dash_app.callback(
            Output('table', 'filter_query'),
            [Input('global-search', 'value'), Input('search-button', 'n_clicks'), Input('global-search', 'n_submit')]
        )
        def update_filter_query(search_value, search_button_clicks, n_submit):
            ctx = dash.callback_context
            if not ctx.triggered:
                return ''
            if ctx.triggered[0]['prop_id'] in ['search-button.n_clicks', 'global-search.n_submit']:
                if search_value:
                    search_values = [v.strip() for v in search_value.split(",")]
                    filter_queries = []
                    for sv in search_values:
                        filter_query = ' || '.join(
                            [f'{{{col}}} icontains "{sv}"' for col in self.df.columns])
                        filter_queries.append(filter_query)
                    return ' || '.join(filter_queries)
            return ''

        @self.dash_app.callback(
            Output('global-search', 'value'),
            Input('clear-button', 'n_clicks')
        )
        def clear_search(clear_button_clicks):
            return ''

        @self.dash_app.callback(
            Output('table', 'selected_rows'),
            Input('clear-button', 'n_clicks')
        )
        def clear_selection(n):
            if n is None:
                return [0]
            else:
                return []

    def visualisation_callbacks(self):
        @self.dash_app.callback(
            Output('sunburst-chart', 'figure'),
            [
                Input('table', 'selected_rows'),  # Get selected rows from the main table
                Input('table', 'data'),  # Get data from the main table
                Input('table_two', 'derived_virtual_selected_rows'),
                Input('table_two', 'derived_virtual_data'),
                Input('layer-toggle', 'value')
            ]
        )
        def update_graph(selected_rows, table_data, table_two_selected_rows, derived_virtual_data, toggle_button):
            # Get the selected identifier from table based on selected_rows
            identifier = table_data[selected_rows[0]]['Identifier'] if selected_rows else None

            if table_two_selected_rows is None or len(table_two_selected_rows) == 0:
                fig = go.Figure()
                fig.update_layout(
                    xaxis=dict(showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(showgrid=False, zeroline=False, visible=False),
                    annotations=[
                        dict(
                            text='No data selected',
                            xref='paper', yref='paper',
                            showarrow=False,
                            font=dict(size=20)
                        )
                    ]
                )
                return fig

            # 1) grab the clean identifiers the user selected in table two
            clean_selected = [derived_virtual_data[i]['Identifier'] for i in table_two_selected_rows]

            # 2) find *all* variants of those selected (i.e. with any number of zero‐width spaces)
            designated = self.references[
                self.references['standard'].apply(self.clean_label).isin(clean_selected)
            ]['standard'].tolist()

            # 3) find *all* standards whose parent (cleaned) matches one of the clean_selected
            parents = self.references[
                self.references['parent'].apply(self.clean_label).isin(clean_selected)
            ]['standard'].tolist()

            # 4) optionally go down one more layer
            if 'show' in toggle_button:
                clean_parents = [self.clean_label(p) for p in parents]
                children = self.references[
                    self.references['parent'].apply(self.clean_label).isin(clean_parents)
                ]['standard'].tolist()
            else:
                children = []

            # 5) collect everything
            all_standards = sorted(designated + parents + children)


            all_standards = sorted(designated + parents + children)


            filtered = self.references[self.references["standard"].isin(all_standards)]
            filtered[['standard', 'parent']] = filtered[['standard', 'parent']].applymap(lambda x: self.clean_label(x))
            filtered = filtered.drop_duplicates()

            # filtered.to_excel("fiter_1.xlsx", index=False)

            zero_width_space = '\u2060'
            def add_zero_width_space(text, index):
                # zero_width_space = '<mark>'
                # zero_width_space = '\u200B'
                # zero_width_space = '\u2060'
                return text + zero_width_space * index


            filtered['standard'] = filtered.groupby('standard').cumcount().apply(lambda x: add_zero_width_space('', x)) + filtered[
                'standard']
            filtered = filtered.sort_values(by=["type", "standard"])

            marked = filtered["standard"][filtered["standard"].str.contains(zero_width_space)].to_list()

            for m in marked:
                cleaned = str(m).replace(zero_width_space, "")

                associated = filtered[filtered["parent"] == cleaned]

                associated["parent"] = m

                filtered = pd.concat([filtered, associated]).reset_index(drop=True)



            filtered.drop_duplicates(subset=["standard", "parent"], inplace=True)
            # filtered.to_excel("filtered_1.xlsx", index=False)

            def ensure_unique(series: pd.Series) -> pd.Series:
                """
                Return a copy of `series` (cast to string) where any duplicate values
                have '<mark>' prepended repeatedly until all entries are unique.
                """
                s = series.astype(str).copy()  # work on strings
                # As long as there are duplicates, mark them
                while not s.is_unique:
                    dup_mask = s.duplicated(keep='first')
                    # prepend '<mark>' to every duplicate beyond its first occurrence
                    s.loc[dup_mask] = zero_width_space + s.loc[dup_mask]
                return s

            filtered["standard"] = ensure_unique(filtered["standard"])

            # Function to limit levels
            def limit_levels(df):
                """This function prevents a 4th layer to appear which sometimes happens"""
                designated = df["standard"][df["parent"] == "Standard"].to_list()
                layer2_identifiers = df["standard"][df["parent"].isin(designated)].to_list()

                df = df[(df["parent"].isin([self.clean_label(std) for std in layer2_identifiers])) |
                        (df["parent"].isin([self.clean_label(std) for std in designated])) |
                        (df["parent"] == "Standard") | (df["parent"] == "root")]

                for standard in layer2_identifiers:
                    update_list = df[df["parent"] == self.clean_label(standard)]

                    for index, row in update_list.iterrows():
                        df.at[index, "parent"] = standard

                df["standard"] = df["standard"].apply(lambda x: self.clean_label(x) if x not in designated and x not in layer2_identifiers else x)

                return df


            filtered = limit_levels(filtered).reset_index(drop=True)

            #adding in type change to make segment green
            # Mark the selected node by appending (selected) to its type
            filtered.loc[filtered["standard"] == identifier, "type"] = (
                    filtered.loc[filtered["standard"] == identifier, "type"] + "(selected)"
            )

            # Create a separate column for color mapping
            filtered["color_type"] = filtered["type"]

            # For the selected node, override the color_type to be "selected"
            filtered.loc[filtered["standard"] == identifier, "color_type"] = "selected"

            # Remove the dummy root node by setting top-level parent to an empty string
            filtered.loc[filtered['parent'].isin(['Standard', 'root']), 'parent'] = ''

            # Create the sunburst chart using the new 'color_type' column for coloring
            fig = px.sunburst(
                filtered,
                names='standard',
                parents='parent',
                color="color_type",  # use color_type for coloring
                color_discrete_map={
                    'Designated': '#F6BA00',
                    'Normative': '#030072',
                    'Informative': '#950200',
                    'Normative-No Full Text': '#030072',
                    'Informative-No Full Text': '#950200',
                    'selected': "green"  # maps our selected node to green
                },
                hover_data=["standard", "Short_Title", "CommitteeReference", "Classification", "IssuingBody",
                            "PublicationDate", "type", "ACCode"],
            )

            # Define and update hover template as before
            hover_template = (
                '<br><b>ACCode:</b> %{customdata[6]}'
                '<br><b>Identifier:</b> %{customdata[0]}'
                '<br><b>Title:</b> %{customdata[1]}'
                '<br><b>Committee:</b> %{customdata[2]}'
                '<br><b>ICS:</b> %{customdata[3]}'
                '<br><b>Published:</b> %{customdata[4]}'
                '<br><b>Reference:</b> %{customdata[5]}<extra></extra>'
            )

            fig.update_traces(
                customdata=filtered[
                    ['standard', 'Short_Title', 'CommitteeReference', 'Classification', 'PublicationDate',
                     'type', "ACCode"]].values,
                hovertemplate=hover_template,
                insidetextorientation='radial',
                hoverinfo='label+value+text',
            )

            fig.update_layout(
                margin=dict(t=100, l=0, r=0, b=100)
            )

            return fig


