import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.theme_helper import *
from analytics.query import *

def make_performance_overview_graph(df, group_by="period"):
    df = df.copy()
    df['material_rate'] = df['material_rate']*100
    df['staff_rate'] = df['staff_rate']*100
    df['other_rate'] = df['other_rate']*100
    df['profit_rate'] = df['profit_rate']*100

    COLOR_4 = color_gradient(n=4)

    figure = make_subplots(specs=[[{"secondary_y": True}]])

    figure.add_trace(
        go.Scatter(
            x=df[group_by],
            y=df['amount_calc'],
            customdata=df['profit_rate'],
            mode='lines+markers+text',
            name='Profit',
            line_color=COLOR_4[-1],
            text=df['amount_calc'],
            textfont=dict(color='white'),
            hovertemplate=f"Profit"+": %{y:.2f} €<br>Profit rate"+": %{customdata:.2f} %",
            textposition='top center',
            texttemplate='%{y:d} €',
            showlegend=True,
        ),
        secondary_y=False,
    )


    figure.add_trace(
        go.Bar(
            x=df[group_by],
            y=df['amount_calc_sales'],
            hovertemplate=f"Sales"+": %{y:.2f} €",
            base=0,
            marker_color=COLOR_4[0],
            name='Sales',
        ),
    )

    figure.add_trace(
        go.Bar(
            x=df[group_by],
            y=df['amount_calc_material'],
            customdata=df['material_rate'],
            hovertemplate=f"Material cost"+": %{y:.2f} €<br>Material/Sales"+": %{customdata:.2f} %",
            base=0,
            marker_color=COLOR_4[1],
            name='Material cost',
        ),
    )

    figure.add_trace(
        go.Bar(
            x=df[group_by],
            y=df['amount_calc_staff'],
            customdata=np.stack((df['amount_calc_staff'], df['staff_rate']), axis=-1),
            hovertemplate=f"Staff cost"+": %{customdata[0]:.2f} €<br>Staff/Sales"+": %{customdata[1]:.2f} %",
            base=df['amount_calc_material'],
            marker_color=COLOR_4[2],
            name='Staff cost',
        ),
    )

    figure.add_trace(
        go.Bar(
            x=df[group_by],
            y=df['amount_calc_other'],
            customdata=np.stack((df['amount_calc_other'], df['other_rate']), axis=-1),
            hovertemplate=f"Other cost"+": %{customdata[0]:.2f} €<br>Other cost/Sales"+": %{customdata[1]:.2f} %",
            base=df['amount_calc_staff']+df['amount_calc_material'],
            marker_color=COLOR_4[3],
            name='Other cost',
        ),
    )

    figure.update_yaxes(
        title_text=f"<b>Amount</b> (€)",
        titlefont=dict(color=COLOR_4[0]),
        tickfont=dict(color=COLOR_4[0]),
        secondary_y=False,
    )


    figure.update_layout(
        # bargap=0.6,
        hovermode='x',
        # title=f"Profit/Sales/Cost Trend",
        xaxis_title=f"<b>{group_by.capitalize()}",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        barmode='relative',
    )

    return figure


def make_turnover_structure_graph(df, group_by="period", department_name=None):
    df = df.copy()

    COLOR_4 = color_gradient(n=4)
    figure = make_subplots(specs=[[{"secondary_y": True}]])

    if department_name is None:
        figure.add_trace(
            go.Bar(
                x=df[group_by],
                y=df['Food Kiosk Sushibar'],
                hovertemplate=f"Sushibar"+": %{y:.2f} €",
                # base=0,
                marker_color=COLOR_4[0],
                name='Sushibar',
            ),
        )

        figure.add_trace(
            go.Bar(
                x=df[group_by],
                y=df['Restaurant'],
                marker_color=COLOR_4[1],
                hovertemplate=f"Restaurant"+": %{y:.2f} €",
                name='Restaurant',
            ),
        )

        figure.add_trace(
            go.Bar(
                x=df[group_by],
                y=df['Food Plant'],
                hovertemplate=f"Food Plant"+": %{y:.2f} €",
                marker_color=COLOR_4[2],
                name='Food Plant',
            ),
        )


        figure.add_trace(
            go.Bar(
                x=df[group_by],
                y=df['Head Office'],
                marker_color=COLOR_4[3],
                hovertemplate=f"Office"+": %{y:.2f} €",
                name='Office',
            ),
        )
    else:
        figure.add_trace(
            go.Bar(
                x=df[group_by],
                y=df[department_name],
                hovertemplate=f"{department_name}"+": %{y:.2f} €",
                # base=0,
                marker_color=COLOR_4[0],
                name=department_name,
            ),
        )

    figure.update_yaxes(
        title_text=f"<b>Turnover</b> (€)",
        titlefont=dict(color=COLOR_4[0]),
        tickfont=dict(color=COLOR_4[0]),
        secondary_y=False,
    )

    figure.update_layout(
        hovermode='x',
        xaxis_title=f"<b>{group_by.capitalize()}",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        barmode='group',
    )

    return figure



def make_cost_structure_graph(df, group_by="period", denominator="sales"):
    df = df.copy()
    df['material_rate'] = df['material_rate']*100
    df['staff_rate'] = df['staff_rate']*100
    df['other_rate'] = df['other_rate']*100
    df['profit_rate'] = df['profit_rate']*100

    COLOR_4 = color_gradient(n=4)
    # Determine the bar mode based on the value of 'denominator'
    if denominator == "sales":
        barmode = 'group' # or any other default mode you wish to use
    else:
        barmode = 'relative'

    figure = make_subplots(specs=[[{"secondary_y": True}]])

    if denominator == "sales":
        figure.add_trace(
            go.Bar(
                x=df[group_by],
                y=df['profit_rate'],
                hovertemplate=f"Profit rate"+": %{y:.2f} %",
                # base=0,
                marker_color=COLOR_4[0],
                name='Profit rate',
            ),
        )

    figure.add_trace(
        go.Bar(
            x=df[group_by],
            y=df['material_rate'],
            hovertemplate=f"Material ratio"+": %{y:.2f} %",
            marker_color=COLOR_4[1],
            name='Material ratio',
        ),
    )

    figure.add_trace(
        go.Bar(
            x=df[group_by],
            y=df['staff_rate'],
            marker_color=COLOR_4[2],
            hovertemplate=f"Staff ratio"+": %{y:.2f} %",
            name='Staff ratio',
        ),
    )

    figure.add_trace(
        go.Bar(
            x=df[group_by],
            y=df['other_rate'],
            marker_color=COLOR_4[3],
            hovertemplate=f"Other Op. ratio"+": %{y:.2f} %",

            name='Other ratio',
        ),
    )

    figure.update_yaxes(
        title_text=f"<b>Ratio</b> (%)",
        titlefont=dict(color=COLOR_4[0]),
        tickfont=dict(color=COLOR_4[0]),
        secondary_y=False,
    )


    figure.update_layout(
        hovermode='x',
        xaxis_title=f"<b>{group_by.capitalize()}",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        barmode=barmode,
    )

    return figure



def make_cost_structure_breakdown_by_department_graph(df, group_by="period"):
    df = df.copy()
    departments = sorted(df['department_name'].unique().tolist())
    COLOR_4 = color_gradient(n=4)
    figure = make_subplots(rows=4, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=departments,
                        )

    for i in range(len(departments)):
        filtered_df = prepare_cost_structure_breakdown(df, department_name=departments[i])
        figure.add_trace(
            go.Bar(
                x=filtered_df[group_by],
                y=filtered_df['amount_calc'],
                hovertemplate=f"Profit"+": %{y:.2f} €",
                marker_color=COLOR_4[0],
                name='Profit',
                legendgroup='Profit',
                showlegend=True if i == 0 else False,
            ),
            row=i+1, col=1,
        )

        figure.add_trace(
            go.Bar(
                x=filtered_df[group_by],
                y=filtered_df['amount_calc_material'],
                hovertemplate=f"Material cost"+": %{y:.2f} €",
                marker_color=COLOR_4[1],
                name='Material',
                legendgroup='Material cost',
                showlegend=True if i == 0 else False,

            ),
            row=i+1, col=1,
        )

        figure.add_trace(
            go.Bar(
                x=filtered_df[group_by],
                y=filtered_df['amount_calc_staff'],
                marker_color=COLOR_4[2],
                hovertemplate=f"Staff cost"+": %{y:.2f} €",
                name='Staff',
                legendgroup='Staff cost',
                showlegend=True if i == 0 else False,
            ),
            row=i+1, col=1,
        )

        figure.add_trace(
            go.Bar(
                x=filtered_df[group_by],
                y=filtered_df['amount_calc_other'],
                marker_color=COLOR_4[3],
                hovertemplate=f"Other Op. cost"+": %{y:.2f} €",
                name='Other',
                legendgroup='Other Op. cost',
                showlegend=True if i == 0 else False,
            ),
            row=i+1, col=1,

        )

        figure.update_yaxes(
            title_text=f"<b>Amount</b> (€)",
            titlefont=dict(color=COLOR_4[0]),
            tickfont=dict(color=COLOR_4[0]),
            secondary_y=False,
        )


    figure.update_layout(
        hovermode='x',
        bargap=0.4,
        xaxis_title=f"<b>{group_by.capitalize()}",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        barmode='group',
        height=350*len(departments),
    )

    return figure


def make_cost_structure_cumulative_by_department_graph(data):
    labels = data['departments']
    COLOR_4 = color_gradient(n=4)
    widths = np.array([
        100*data['total_sushibar_cost']/data['total_cost'],
        100*data['total_plant_cost']/data['total_cost'],
        100*data['total_office_cost']/data['total_cost'],
        100*data['total_restaurant_cost']/data['total_cost'],
    ])

    data = {
        "Material ratio": [
            100*data['total_sushibar_material']/data['total_sushibar_cost'],
            100*data['total_plant_material']/data['total_plant_cost'],
            100*data['total_office_material']/data['total_office_cost'],
            100*data['total_restaurant_material']/data['total_restaurant_cost'],
        ],
        "Staff ratio": [
            100*data['total_sushibar_staff']/data['total_sushibar_cost'],
            100*data['total_plant_staff']/data['total_plant_cost'],
            100*data['total_office_staff']/data['total_office_cost'],
            100*data['total_restaurant_staff']/data['total_restaurant_cost'],
        ],
        "Other ratio": [
            100*data['total_sushibar_other']/data['total_sushibar_cost'],
            100*data['total_plant_other']/data['total_plant_cost'],
            100*data['total_office_other']/data['total_office_cost'],
            100*data['total_restaurant_other']/data['total_restaurant_cost'],
        ]
    }

    figure = go.Figure()
    for i in range(len(data)):
        figure.add_trace(go.Bar(
            name=list(data.keys())[i],
            y=data[list(data.keys())[i]],
            x=np.cumsum(widths)-widths,
            width=widths,
            offset=0,
            customdata=np.transpose([labels, widths*data[list(data.keys())[i]]/100]),
            textposition="inside",
            textfont_color="white",
            marker_color=COLOR_4[i+1],
            hovertemplate="<br>".join([
                "Department: %{customdata[0]}",
                "Cost/total cost: %{customdata[1]:.2f} %",
                "Department/total cost: %{width:.2f} %",
            ])
        ))

    figure.update_xaxes(
        tickvals=np.cumsum(widths)-widths/2,
        ticktext=labels,
    )

    figure.update_yaxes(range=[0,100])
    figure.update_xaxes(range=[0,100])

    figure.update_layout(
        barmode="stack",
        uniformtext=dict(mode="hide", minsize=10),
        height=600,
    )
    return figure


def make_cost_structure_cumulative_icicle_graph(df):
    custom_color_scale = [
        [0.0, color_gradient(n=2)[0]],  # Blue at the lowest end of the scale
        [1.0, color_gradient(n=2)[1]]    # Red at the highest end of the scale
    ]

    figure = make_subplots(1, 1, specs=[[{"type": "domain"}]],)

    figure.add_trace(go.Icicle(
        labels=df['id'],
        parents=df['parent'],
        values=df['value'],
        branchvalues='total',
        marker=dict(
            colors=df['color'],
            # colorscale='Gnbu',
            colorscale=custom_color_scale,
            cmid=1
            ),
        hovertemplate='<b>%{label} </b> <br> Costs: %{value}<br> €',
        name=''
        ), 1, 1)

    figure.update_layout(height=700,)
    return figure