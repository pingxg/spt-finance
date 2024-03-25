import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme_helper import *


# month_df_copied = month_df.copy()
# month_df_grouped = month_df_copied.groupby([group_date_by])['amount_calc'].sum().reset_index().sort_values(by=[group_date_by], kind='mergesort', ascending=[True])
# month_df_grouped_sales = month_df_copied.loc[month_df_copied['account_type']=="Sales"].groupby([group_date_by])['amount_calc'].sum().reset_index().sort_values(by=[group_date_by], kind='mergesort', ascending=[True])
# month_df_grouped_material = month_df_copied.loc[month_df_copied['account_type']=="Material"].groupby([group_date_by])['amount_calc'].sum().reset_index().sort_values(by=[group_date_by], kind='mergesort', ascending=[True])
# month_df_grouped_staff = month_df_copied.loc[month_df_copied['account_type']=="Staff"].groupby([group_date_by])['amount_calc'].sum().reset_index().sort_values(by=[group_date_by], kind='mergesort', ascending=[True])
# month_df_grouped_other = month_df_copied.loc[month_df_copied['account_type']=="Other cost"].groupby([group_date_by])['amount_calc'].sum().reset_index().sort_values(by=[group_date_by], kind='mergesort', ascending=[True])
# month_df_grouped = pd.merge(month_df_grouped, month_df_grouped_sales, on=group_date_by,validate="1:1",suffixes=(None,'_sales'),how='left')
# month_df_grouped = pd.merge(month_df_grouped, month_df_grouped_material, on=group_date_by,validate="1:1",how='left',suffixes=(None,'_material'))
# month_df_grouped = pd.merge(month_df_grouped, month_df_grouped_staff, on=group_date_by,validate="1:1",how='left',suffixes=(None,'_staff'))
# month_df_grouped = pd.merge(month_df_grouped, month_df_grouped_other, on=group_date_by,validate="1:1",how='left',suffixes=(None,'_other'))
# month_df_grouped['material_rate'] = (month_df_grouped['amount_calc_material']/month_df_grouped['amount_calc_sales']).abs()*100
# month_df_grouped['staff_rate']= (month_df_grouped['amount_calc_staff']/month_df_grouped['amount_calc_sales']).abs()*100
# month_df_grouped['other_rate']= (month_df_grouped['amount_calc_other']/month_df_grouped['amount_calc_sales']).abs()*100
# month_df_grouped['profit_rate']= (month_df_grouped['amount_calc']/month_df_grouped['amount_calc_sales'])*100
# month_df_grouped.fillna(0,inplace=True)

def make_performance_overview_graph(df, group_by="month"):
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
            hovertemplate=f"Profit"+": %{y:d} €<br>Profit rate"+": %{customdata:d} %",
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
            hovertemplate=f"Sales"+": %{y:d} €",
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
            hovertemplate=f"Material cost"+": %{y:d} €<br>Material/Sales"+": %{customdata:d} %",
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
            hovertemplate=f"Staff cost"+": %{customdata[0]:d} €<br>Staff/Sales"+": %{customdata[1]:d} %",
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
            hovertemplate=f"Other cost"+": %{customdata[0]:d} €<br>Other cost/Sales"+": %{customdata[1]:d} %",
            base=df['amount_calc_staff']+df['amount_calc_material'],
            marker_color=COLOR_4[3],
            name='Other cost',
        ),
    )

    figure.update_yaxes(
        title_text=f"<b>Profit</b> (€)",
        titlefont=dict(color=COLOR_4[0]),
        tickfont=dict(color=COLOR_4[0]),
        secondary_y=False,
    )


    figure.update_layout(
        bargap=0.6,
        hovermode='x',
        title=f"Profit/Sales/Cost Trend",
        xaxis_title=group_by,
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        barmode='relative',
    )

    return figure
