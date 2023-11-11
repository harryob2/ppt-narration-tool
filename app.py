import pandas as pd
import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output
from dash_split_pane import DashSplitPane
from datetime import datetime, timedelta
import numpy as np
import json
import os

# Load the dataset
file_path = r"half filt_scrap past year.csv"
scrap_data = pd.read_csv(file_path)

# Convert the 'Transaction Date' to datetime format for proper plotting
scrap_data['Booking Date'] = pd.to_datetime(scrap_data['Booking Date'], format='%d/%m/%Y')

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# This line is critical for Heroku deployment to work properly
server = app.server

# Filter out null or NaN values from 'Reason Code Disc'
valid_reason_codes = scrap_data['Reason Code Disc'].dropna().unique()

# Define options for the checklist
reason_code_disc_options = [{'label': reason, 'value': reason} for reason in valid_reason_codes]

# Define the layout of the app
app.layout = html.Div([
    DashSplitPane(
        id='split-pane',
        children=[
            # Left Pane
            html.Div([
                html.Div([
                    html.Label("Select the number of days for the trend:", className='label-style'),
                    html.Div([
                        html.Button('7 Days', id='button-7-days', className='button-style'),
                        html.Button('Month to Date', id='button-month-to-date', className='button-style'),
                        html.Button('1 Month', id='button-1-month', className='button-style'),
                        html.Button('3 Months', id='button-3-month', className='button-style'),
                        html.Button('6 Months', id='button-6-month', className='button-style'),
                        html.Button('Year to Date', id='button-year-to-date', className='button-style'),
                        html.Button('1 Year', id='button-1-year', className='button-style')
                    ], className='buttons-container'),
                    dcc.Dropdown(
                        id='category-filter',
                        options=[{'label': category, 'value': category} for category in scrap_data['Category'].unique()],
                        value='Daily Scrap',
                        clearable=False,
                        className='dropdown-style'
                    ),
                    dcc.RadioItems(
                        id='metric-toggle',
                        options=[
                            {'label': 'Scrap Value', 'value': 'Scrap Value'},
                            {'label': 'Scrap Quantity', 'value': 'Scrap Qty'}
                        ],
                        value='Scrap Value',  # Default selection
                        className='radio-button-style'
                    ),
                ], className='pane-container'),
            ], className='left-pane-style'),


            # Right Pane
            html.Div([
                html.H1("Factory Scrap Data Dashboard"),
                dcc.Graph(id='scrap-bar-chart'),
                dcc.Store(id='selected-date-range', storage_type='memory', 
                          data=json.dumps((datetime.now() - timedelta(days=7)).isoformat())),
                html.Label("Select 'Reallocate Dept' to display:"),
                dcc.Checklist(
                    id='dept-checklist',
                    options=[{'label': dept, 'value': dept} for dept in scrap_data['Reallocate Dept'].unique()],
                    value=scrap_data['Reallocate Dept'].unique(),
                    inline=True
                ),
                dcc.Graph(id='scrap-line-chart'),
                html.Label("Filter by Reason Code:"),
                dcc.Checklist(
                    id='reason-code-checklist',
                    options=reason_code_disc_options,
                    value=list(valid_reason_codes),
                    inline=True
                ),
                dcc.Graph(id='foundry-scrap-line-chart'),
                dcc.Checklist(
                    id='reallocate-dept-checklist',
                    options=[{'label': dept, 'value': dept} for dept in scrap_data['Reallocate Dept'].unique()],
                    value=scrap_data['Reallocate Dept'].unique(),
                    inline=True
                ),
                dcc.Graph(id='scrap-by-reason')
            ])
        ],
        split="vertical",
        pane1ClassName='left-pane-style',
        pane2ClassName='right-pane-style',
        size=300  # This is the initial size of the left pane in pixels
    )
])

# Define callback for setting date range
@app.callback(
    Output('selected-date-range', 'data'),
    [Input('button-7-days', 'n_clicks'),
     Input('button-month-to-date', 'n_clicks'),
     Input('button-1-month', 'n_clicks'),
     Input('button-3-month', 'n_clicks'),
     Input('button-6-month', 'n_clicks'),
     Input('button-year-to-date', 'n_clicks'),
     Input('button-1-year', 'n_clicks')],
    prevent_initial_call=True
)
def update_date_range(btn_7_days, btn_month_to_date, btn_1_month, btn_3_month, btn_6_month, btn_year_to_date, btn_1_year):
    ctx = dash.callback_context

    # Identify which button was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    now = datetime.now()
    date_range = None

    if button_id == 'button-7-days':
        date_range = now - timedelta(days=7)
    elif button_id == 'button-month-to-date':
        date_range = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif button_id == 'button-1-month':
        date_range = now - timedelta(days=30)
    elif button_id == 'button-3-month':
        date_range = now - timedelta(days=90)
    elif button_id == 'button-6-month':
        date_range = now - timedelta(days=180)
    elif button_id == 'button-year-to-date':
        date_range = now.replace(day=1, month=1)
    elif button_id == 'button-1-year':
        date_range = now - timedelta(days=365)

    # Return the date range as a JSON string
    return json.dumps(date_range.isoformat() if date_range else None)


# Define callback to update bar chart
@app.callback(
    Output('scrap-bar-chart', 'figure'),
    [Input('category-filter', 'value'),
     Input('metric-toggle', 'value')]
)
def update_bar_chart(selected_category, selected_metric):
    # Filter data based on selected category
    filtered_data = scrap_data[scrap_data['Category'] == selected_category]

    # Group and sum scrap value by 'Reallocate Dept'
    grouped_data = filtered_data.groupby('Reallocate Dept')[selected_metric].sum().reset_index()

    # Sort the data in descending order of 'Scrap Value'
    sorted_data = grouped_data.sort_values(selected_metric, ascending=False)

    # Create the bar chart
    fig_bar = px.bar(
        sorted_data,
        x='Reallocate Dept',
        y=selected_metric,
        title=f"Total Scrap Value by Reallocate Dept for Category: {selected_category}"
    )
    return fig_bar


# Define callback to update line chart
@app.callback(
    Output('scrap-line-chart', 'figure'),
    [Input('category-filter', 'value'), 
     Input('selected-date-range', 'data'), 
     Input('dept-checklist', 'value'), 
     Input('metric-toggle', 'value')]
)
def update_line_chart(selected_category, selected_date_range_json, selected_depts, selected_metric):
    # Parse the selected date range from JSON
    selected_date_range = json.loads(selected_date_range_json) if selected_date_range_json else None

    # Filter data based on selected category and selected 'Reallocate Dept'
    filtered_data = scrap_data[
        (scrap_data['Category'] == selected_category) & 
        (scrap_data['Reallocate Dept'].isin(selected_depts))
    ]

    if selected_date_range:
        # Convert the selected date range into a datetime object
        cutoff_date = datetime.fromisoformat(selected_date_range)
    else:
        # Default behavior if no date range is selected
        cutoff_date = filtered_data['Booking Date'].min()

    # Filter the data to only include dates after the cutoff date
    filtered_data = filtered_data[filtered_data['Booking Date'] >= cutoff_date]

    # Group and sum scrap value by 'Booking Date' and 'Reallocate Dept'
    time_grouped_data = filtered_data.groupby(['Booking Date', 'Reallocate Dept'])[selected_metric].sum().reset_index()

    # Create the line chart
    fig_line = px.line(
        time_grouped_data,
        x='Booking Date',
        y=selected_metric,
        color='Reallocate Dept',
        title=f"Scrap Value Over Time for Category: {selected_category}"
    )
    return fig_line

@app.callback(
    Output('foundry-scrap-line-chart', 'figure'),
    [Input('category-filter', 'value'), 
     Input('selected-date-range', 'data'), 
     Input('reason-code-checklist', 'value'), 
     Input('metric-toggle', 'value')]
)
def update_foundry_line_chart(selected_category, selected_date_range_json, selected_reason_codes, selected_metric):
    # Filter data based on selected category and reason codes
    category_filtered_data = scrap_data[
        (scrap_data['Category'] == selected_category) & 
        (scrap_data['Reason Code Disc'].isin(selected_reason_codes))
    ]

    # Parsing the selected date range
    selected_date_range = json.loads(selected_date_range_json) if selected_date_range_json else None

    # Filtering the data for 'foundry' reallocations
    foundry_scrap_external = category_filtered_data[
        (category_filtered_data['Reallocate Dept'] == 'Foundry') & 
        (category_filtered_data['GL BU'] != 'Foundry')
    ]
    foundry_scrap_internal = category_filtered_data[
        (category_filtered_data['Reallocate Dept'] == 'Foundry') & 
        (category_filtered_data['GL BU'] == 'Foundry')
    ]

    if selected_date_range:
        # Convert the selected date range into a datetime object
        cutoff_date = datetime.fromisoformat(selected_date_range)
    else:
        # Default behavior if no date range is selected
        cutoff_date = scrap_data['Booking Date'].min()

    # Filter the data to only include dates within the selected range for both datasets
    filtered_foundry_scrap_external = foundry_scrap_external[foundry_scrap_external['Booking Date'] > cutoff_date]
    filtered_foundry_scrap_internal = foundry_scrap_internal[foundry_scrap_internal['Booking Date'] > cutoff_date]

    # Group and sum both scrap quantity and scrap value by 'Booking Date' for both datasets
    grouped_foundry_scrap_external = filtered_foundry_scrap_external.groupby('Booking Date').agg({'Scrap Qty': 'sum', 'Scrap Value': 'sum'}).reset_index()
    grouped_foundry_scrap_internal = filtered_foundry_scrap_internal.groupby('Booking Date').agg({'Scrap Qty': 'sum', 'Scrap Value': 'sum'}).reset_index()

    # Add a prefix to each column based on external or internal for clarity
    external_columns = {metric: f'{metric}_External' for metric in ['Scrap Qty', 'Scrap Value']}
    internal_columns = {metric: f'{metric}_Internal' for metric in ['Scrap Qty', 'Scrap Value']}

    # Rename the columns for clarity
    grouped_foundry_scrap_external.rename(columns=external_columns, inplace=True)
    grouped_foundry_scrap_internal.rename(columns=internal_columns, inplace=True)

    # Merge the two datasets on 'Booking Date' to create a single dataframe for plotting
    merged_scrap_data = pd.merge(
        grouped_foundry_scrap_external, 
        grouped_foundry_scrap_internal, 
        on='Booking Date', 
        how='outer'
    ).fillna(0)

    # Calculate the ratio of internal to external for each date based on the selected metric
    external_column = f'{selected_metric}_External'
    internal_column = f'{selected_metric}_Internal'

    # Replace any inf or NaN values with 0 (or another appropriate value)
    merged_scrap_data['Ratio'] = (merged_scrap_data[external_column] / merged_scrap_data[internal_column]).replace([np.inf, -np.inf], np.nan).fillna(0)

    # Prepare the data for a stacked bar chart by melting the merged dataframe
    melted_scrap_data = pd.melt(
        merged_scrap_data, 
        id_vars='Booking Date', 
        value_vars=[external_column, internal_column],  # Dynamically select columns based on metric
        var_name='Scrap Type', 
        value_name=selected_metric
    )

    # Create the stacked bar chart
    fig_foundry_scrap = px.bar(
        melted_scrap_data,
        x='Booking Date',
        y=selected_metric,
        color='Scrap Type',
        title='Foundry Scrap Internal vs External'
    )

    # Add text annotations for the ratio on top of each bar
    for i, date in enumerate(merged_scrap_data['Booking Date']):
        ratio = merged_scrap_data.loc[i, 'Ratio']
        total_height = merged_scrap_data.loc[i, external_column] + merged_scrap_data.loc[i, internal_column]
        # Only add annotation if the ratio is not 0
        if ratio > 0:
            fig_foundry_scrap.add_annotation(
                x=date,
                y=total_height,
                text=f"Ratio: {ratio:.2f}",
                showarrow=False,
                yshift=10
            )

    # Customize layout for better appearance
    fig_foundry_scrap.update_layout(
        barmode='stack',
        annotations=[{
            'x': date,
            'y': total_height + 0.05 * total_height,  # Adjust the height if needed
            'text': f"{100*ratio:.2f}%",
            'font': {'color': 'black'},
            'xref': 'x',
            'yref': 'y',
            'showarrow': False,
        } for date, ratio, total_height in zip(
            merged_scrap_data['Booking Date'],
            merged_scrap_data['Ratio'],
            merged_scrap_data[external_column] + merged_scrap_data[internal_column]
        ) if ratio > 0]  # Add condition to filter out dates with ratio <= 0
    )

    return fig_foundry_scrap



@app.callback(
    Output('scrap-by-reason', 'figure'),
    [Input('reallocate-dept-checklist', 'value'),
     Input('selected-date-range', 'data')]
)
def update_scrap_bar_chart(selected_depts, selected_date_range_json):
    # Filter data based on the selected departments
    if selected_depts:
        filtered_data = scrap_data[scrap_data['Reallocate Dept'].isin(selected_depts)]
    else:
        filtered_data = scrap_data

    # Apply date range filter
    selected_date_range = json.loads(selected_date_range_json) if selected_date_range_json else None
    filtered_data = filtered_data[filtered_data['Booking Date'] >= selected_date_range]

    # Aggregate data for the bar chart
    aggregated_data = filtered_data.groupby('Reason Code Disc')['Scrap Value'].sum().reset_index().sort_values(by='Scrap Value', ascending=False)

    # Create the bar chart
    fig = px.bar(
        aggregated_data,
        x='Reason Code Disc',
        y='Scrap Value',
        title='Scrap Value by Reason Code'
    )

    return fig




# Run the app
if __name__ == '__main__':
    # Heroku assigns the port number via the PORT environment variable.
    # We don't need to (and shouldn't) specify the port and host in our code.
    # Heroku will handle it when deploying the app.
    # We only provide a default for local development.
    port = int(os.environ.get('PORT', 5000))
    # Host '0.0.0.0' is set to allow connections on all network interfaces.
    app.run_server(host='0.0.0.0', port=port, debug=False)