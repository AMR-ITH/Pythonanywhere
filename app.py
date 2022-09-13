
from dash import Dash, html, dcc, Output, Input, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import json

recipe = pd.read_excel(r'recipe_final_list.xlsx')

app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME])
server = app.server
india_states = json.load(open('states_india.geojson', 'r'))

recipe['total time(min)'] = recipe['preparation time(min)'] + recipe['cooking time(min)']

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Span([
                html.I(className="fa-solid fa-bowl-rice"),
                " India's best food recipes ",
                html.I(className="fa-solid fa-bowl-rice")], className='h2')
        ], width=20)
    ], justify='center', className='my-2'),

    dbc.Row([
        dbc.Col([html.Label('Food List', className='bg-secondary')], width=3),
        dbc.Col([html.Label("Top 10 Food Recipe's", className='bg-secondary')], width={"size": 4, "offset": 5}),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(options=[
                {'label': 'topmost', 'value': '0-10'},
                {'label': '2nd topmost', 'value': '11-21'},
                {'label': '3rd topmost', 'value': '22-32'},
                {'label': '4th topmost', 'value': '33-43'},
                {'label': '5th topmost', 'value': '44-54'},
                {'label': '6th topmost', 'value': '55-65'},
                {'label': '7th topmost', 'value': '66-76'},
                {'label': '8th topmost', 'value': '77-87'},
                {'label': '9th topmost', 'value': '88-98'},
                {'label': '10th topmost', 'value': '99-109'}
            ], multi=False, id='top_ten_dpdn'),
            html.Label('Diet', className='bg-secondary'),
            dcc.Dropdown([diet for diet in sorted(recipe['type of diet'].unique())], multi=True, id='diet_dpdn'),
            html.Label('Course of Meal', className='bg-secondary'),
            dcc.Dropdown([meal for meal in sorted(recipe['course of meal'].unique())], multi=True,
                         id='course_of_meal_dpdn'),
            html.Label('Time ', className='bg-secondary'),
            dcc.Dropdown(options=[dict(label='20min', value=20),
                                  dict(label='30min', value=30),
                                  dict(label='50min', value=50),
                                  dict(label='1h', value=60),
                                  dict(label='1.5h', value=90),
                                  dict(label='2h', value=120),
                                  dict(label='2.5h', value=150),
                                  dict(label='3h', value=180),
                                  dict(label='3.5h', value=210),
                                  dict(label='greater_than_4h', value=240)],
                         multi=False, id='time_dpdn')

        ], width=3),
        dbc.Col([
            dcc.Graph(id='bar_h', config={'displayModeBar': False})
        ], width=9)
    ]),
    dbc.Row([html.Br()]),
    dbc.Row([
        dbc.Col([html.Label('Preparation vs Cooking vs Total time', className='bg-secondary')],
                width={"size": 4, "offset": 1}),
        dbc.Col([html.Label("Location of Recipe State wise", className='bg-secondary')],
                width={"size": 4, "offset": 3}),
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id='line', config={'displayModeBar': False})], width=6),
        dbc.Col([dcc.Graph(id='choro', config={'displayModeBar': False})], width={"size": 6})
    ]),
    dbc.Row([html.Br()]),
    dbc.Row([
        dbc.Col([html.Label("Protein vs Carb vs Fat vs Fibre of Recipe's", className='bg-secondary')],
                width={"size": 4, "offset": 1}),
        dbc.Col([html.Label("Energy Content in Recipe's", className='bg-secondary')],
                width={"size": 4, "offset": 3})
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id='bubble_scatter', config={'displayModeBar': False})], width=6),
        dbc.Col([dcc.Graph(id='bar_v', config={'displayModeBar': False})], width={"size": 6, "offset": 0})
    ])

])


@callback(
    Output('bar_h', 'figure'),
    Output('line', 'figure'),
    Output('choro', 'figure'),
    Output('bubble_scatter', 'figure'),
    Output('bar_v', 'figure'),
    Input('top_ten_dpdn', 'value'),
    Input('diet_dpdn', 'value'),
    Input('course_of_meal_dpdn', 'value'),
    Input('time_dpdn', 'value')

)
def update_graph(top_ten_v, diet_v, course_of_meal_v, time_v):
    dff = recipe.copy()
    dff.columns = [column.replace(" ", "_") for column in dff.columns]
    # print(type(diet_v))
    if any([top_ten_v, diet_v, course_of_meal_v, time_v]):

        if diet_v is not None:
            if len(diet_v) > 0:
                dff = dff.query(f"type_of_diet in {diet_v}")
        if course_of_meal_v is not None:
            if len(course_of_meal_v) > 0:
                dff = dff.query(f"course_of_meal in {course_of_meal_v}")
        if time_v is not None:
            if time_v != 240:
                dff = dff[dff['total_time(min)'] <= time_v]
                # dff = dff.sort_values(by=['total_time(min)'],ascending=False)
            else:
                dff = dff[dff['total_time(min)'] >= time_v]
                # dff = dff.sort_values(by=['total_time(min)'])
        if top_ten_v is not None:
            dff = dff.iloc[int(top_ten_v.split('-')[0]):int(top_ten_v.split('-')[1])]

        dff = dff.reset_index(drop='True').head(10)
        dff = dff.drop_duplicates(subset='name_of_the_dish')
        fig_bar = px.bar(data_frame=dff,
                         x="content_view", y="name_of_the_dish", orientation='h',
                         hover_data={'total_time(min)': True, 'servings': True, 'name_of_the_dish': False},
                         labels=dict(content_view="content views", name_of_the_dish="dish names"))
        fig_bar.update_layout(margin=dict(l=5, r=5, t=5, b=5), yaxis=dict(autorange="reversed"))
        # dff = dff.reset_index(drop='True').head(10)
        names = [name.split()[0] for name in dff['name_of_the_dish']]
        name_lst = [name for name in dff['name_of_the_dish']]
        fig_line_second = px.line(data_frame=dff, x='name_of_the_dish',
                                  y=['preparation_time(min)', 'cooking_time(min)', 'total_time(min)'],
                                  text='value', labels=dict(name_of_the_dish="dish names", value="time(min)"),
                                  markers=True, hover_data={'name_of_the_dish': False, 'dish name': (True, name_lst)})
        fig_line_second.update_layout(margin=dict(l=1, r=1, t=1, b=1),
                                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                                  title=None))
        fig_line_second.update_xaxes(tickvals=np.arange(10), ticktext=names, zeroline=False, showgrid=False)
        fig_line_second.update_yaxes(zeroline=False, showgrid=False)
        fig_line_second.update_traces(textfont_size=10, textposition="bottom right",
                                      cliponaxis=False)

        dff_state = list(dff['state'].fillna(0))
        recipe_name_states = []
        rep_state = set()
        rep_state_index = []

        for state in dff_state:
            if state != 0:
                if dff_state.count(state) > 1:
                    if state not in rep_state:
                        rep_state.add(state)

        for state in list(rep_state):
            lst = [i for i, x in enumerate(dff_state) if x == state]
            rep_state_index.append(lst[-1])

        for data in dff_state:
            index_value = dff_state.index(data)
            if data in rep_state or data == 0:
                dff_state[index_value] = None

        for count, indexes in enumerate(rep_state_index, 0):
            lst_rep_state = list(rep_state)
            dff_state[indexes] = lst_rep_state[count]

        for state in dff_state:
            if state is not None:
                ind_dff_lst = list((dff[dff['state'] == state]).index.values)
                string = ''
                if len(ind_dff_lst) > 1:
                    for value in ind_dff_lst:
                        string = string + dff.loc[value, 'name_of_the_dish']
                        string = string + '<br>'
                    recipe_name_states.append(string[:-4])
                elif len(ind_dff_lst) == 1:
                    value = ind_dff_lst[0]
                    recipe_name = dff.loc[value, 'name_of_the_dish']

                    recipe_name_states.append(recipe_name)
            else:
                recipe_name_states.append(None)

        fig_choropleth = px.choropleth(dff, locations='state', geojson=india_states, color='state_id',
                                       featureidkey='properties.st_nm', scope='asia',
                                       hover_data={'dish name': (True, recipe_name_states), 'state_id': False})
        fig_choropleth.update_geos(fitbounds="locations", visible=True)
        fig_choropleth.update_coloraxes(showscale=False)
        fig_choropleth.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 50})

        fig_bubble_scatter = px.scatter(dff, x='name_of_the_dish',
                                        y=[dff['protein_gms'], dff['carb_gms'], dff['fat_gms'], dff['fibre_gms']],
                                        size='value',
                                        hover_data={'name_of_the_dish': False, 'dish name': (True, name_lst)},
                                        labels=dict(name_of_the_dish="dish names", value="grams"))
        fig_bubble_scatter.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right",
                                                     x=1, title=None))
        fig_bubble_scatter.update_xaxes(tickvals=np.arange(10), ticktext=names, zeroline=False)
        fig_bubble_scatter.update_yaxes(zeroline=False)
        fig_bubble_scatter.update_layout(margin=dict(l=1, r=1, t=40, b=1))

        fig_bar_v = px.bar(data_frame=dff, x='name_of_the_dish', y='energy_Kcal', text='energy_Kcal',
                           hover_data={'name_of_the_dish': False, 'dish name': (True, name_lst)},
                           labels=dict(name_of_the_dish="dish names", energy_Kcal="energy(Kcal)"))
        fig_bar_v.update_layout(margin=dict(l=1, r=1, t=40, b=1))
        fig_bar_v.update_xaxes(tickvals=np.arange(10), ticktext=names, showgrid=False)
        fig_bar_v.update_yaxes(showgrid=False)
        fig_bar_v.update_traces(textfont_size=10, textposition="outside")
        return fig_bar, fig_line_second, fig_choropleth, fig_bubble_scatter, fig_bar_v

    if not any([top_ten_v, diet_v, course_of_meal_v, time_v]):
        dff = dff.reset_index(drop='True').head(10)
        fig_bar = px.bar(data_frame=dff,
                         x="content_view", y="name_of_the_dish", orientation='h',
                         hover_data={'total_time(min)': True, 'servings': True, 'name_of_the_dish': False},
                         labels=dict(content_view="content views", name_of_the_dish="dish names"))
        fig_bar.update_layout(margin=dict(l=5, r=5, t=5, b=5), yaxis=dict(autorange="reversed"))

        names = [name.split()[0] for name in dff['name_of_the_dish']]
        name_lst = [name for name in dff['name_of_the_dish']]

        fig_line_second = px.line(data_frame=dff, x='name_of_the_dish',
                                  y=['preparation_time(min)', 'cooking_time(min)', 'total_time(min)'],
                                  text='value', labels=dict(name_of_the_dish="dish names", value="time(min)"),
                                  markers=True, hover_data={'name_of_the_dish': False, 'dish name': (True, name_lst)})
        fig_line_second.update_layout(margin=dict(l=1, r=1, t=1, b=1),
                                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                                  title=None))
        fig_line_second.update_xaxes(tickvals=np.arange(10), ticktext=names, zeroline=False, showgrid=False)
        fig_line_second.update_yaxes(zeroline=False, showgrid=False)
        fig_line_second.update_traces(textfont_size=10, textposition="bottom right",
                                      cliponaxis=False)

        fig_choropleth = px.choropleth(dff, locations='state', geojson=india_states, color='state_id',
                                       featureidkey='properties.st_nm', scope='asia',
                                       hover_data={'name_of_the_dish': True, 'state_id': False})
        fig_choropleth.update_geos(fitbounds="locations", visible=True)
        fig_choropleth.update_coloraxes(showscale=False)
        fig_choropleth.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 50})

        fig_bubble_scatter = px.scatter(dff, x='name_of_the_dish',
                                        y=[dff['protein_gms'], dff['carb_gms'], dff['fat_gms'], dff['fibre_gms']],
                                        size='value',
                                        hover_data={'name_of_the_dish': False, 'dish name': (True, name_lst)},
                                        labels=dict(name_of_the_dish="dish names", value="grams"))
        fig_bubble_scatter.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right",
                                                     x=1, title=None))
        fig_bubble_scatter.update_xaxes(tickvals=np.arange(10), ticktext=names, zeroline=False)
        fig_bubble_scatter.update_yaxes(zeroline=False)
        fig_bubble_scatter.update_layout(margin=dict(l=1, r=1, t=40, b=1))

        fig_bar_v = px.bar(data_frame=dff, x='name_of_the_dish', y='energy_Kcal', text='energy_Kcal',
                           hover_data={'name_of_the_dish': False, 'dish name': (True, name_lst)},
                           labels=dict(name_of_the_dish="dish names", energy_Kcal="energy(Kcal)"))
        fig_bar_v.update_layout(margin=dict(l=1, r=1, t=40, b=1))
        fig_bar_v.update_xaxes(tickvals=np.arange(10), ticktext=names, showgrid=False)
        fig_bar_v.update_yaxes(showgrid=False)
        fig_bar_v.update_traces(textfont_size=10, textposition="outside")

        return fig_bar, fig_line_second, fig_choropleth, fig_bubble_scatter, fig_bar_v


#

if __name__ == '__main__':
    app.run(debug=True)

