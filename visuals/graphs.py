import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme_helper import *



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
            hovertemplate=f"Profit"+": %{y:.1f} €<br>Profit rate"+": %{customdata:.1f} %",
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
            hovertemplate=f"Sales"+": %{y:.1f} €",
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
            hovertemplate=f"Material cost"+": %{y:.1f} €<br>Material/Sales"+": %{customdata:.1f} %",
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
            hovertemplate=f"Staff cost"+": %{customdata[0]:.1f} €<br>Staff/Sales"+": %{customdata[1]:.1f} %",
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
            hovertemplate=f"Other cost"+": %{customdata[0]:.1f} €<br>Other cost/Sales"+": %{customdata[1]:.1f} %",
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
        bargap=0.6,
        hovermode='x',
        title=f"Profit/Sales/Cost Trend",
        xaxis_title=f"<b>{group_by.capitalize()}",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        barmode='relative',
    )

    return figure
