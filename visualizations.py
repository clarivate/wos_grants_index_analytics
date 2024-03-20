import pandas as pd
import plotly.express as px
from plotly import offline


def visualize_data(df):
    """Create a number of html div object with various grant data visualizations with Plotly.

    :param df: pandas dataframe.
    :return: tuple of str.
    """
    # Visualizing Grants by Years.
    df['Grant Amount, USD'] = df['Grant Amount, USD'].replace(to_replace='', value=0)
    gby = df.groupby('Publication Year')['Grant Amount, USD'].sum()

    fig = px.bar(data_frame=gby, title='Grant Funding by Year, USD')
    fig.update_traces(marker_color='#BC99FF')
    fig.update_layout({'plot_bgcolor': '#FFFFFF', 'paper_bgcolor': '#FFFFFF'},
                      font_family='Calibri',
                      font_color='#646363',
                      font_size=18,
                      title_font_family='Calibri',
                      title_font_color='#646363',
                      legend_title_text=None,
                      legend=dict(
                          yanchor="bottom",
                          y=-0.4,
                          xanchor="center",
                          x=0.5
                      ))
    fig.update_yaxes(title_text=None, showgrid=True, gridcolor='#9D9D9C')
    fig.update_xaxes(title_text=None, linecolor='#9D9D9C')
    grants_by_years_plot = offline.plot(fig, output_type='div')

    # Visualizing top organizations receiving grant funding.
    df['Principal Investigator Institution'] = (df['Principal Investigator Institution'].
                                                replace(to_replace='', value='(name unavailable)'))
    gbo = df.groupby('Principal Investigator Institution')['Grant Amount, USD'].sum('').to_frame().reset_index()
    gbo.sort_values('Grant Amount, USD', ascending=False, inplace=True)
    gbo['Principal Investigator Institution, Concatenated'] = (gbo['Principal Investigator Institution'].
                                                               apply(lambda x: f'{x[:30]}...' if len(x) > 30 else x))

    fig = px.bar(
        data_frame=gbo[:50],
        x='Principal Investigator Institution, Concatenated',
        y='Grant Amount, USD',
        hover_name='Principal Investigator Institution',
        title='Top Grant Receivers by funding volumes, USD'
    )
    fig.update_traces(marker_color='#BC99FF')
    fig.update_layout({'plot_bgcolor': '#FFFFFF', 'paper_bgcolor': '#FFFFFF'},
                      font_family='Calibri',
                      font_color='#646363',
                      font_size=18,
                      title_font_family='Calibri',
                      title_font_color='#646363',
                      legend_title_text=None,
                      legend=dict(
                          yanchor="bottom",
                          y=-0.4,
                          xanchor="center",
                          x=0.5
                      ))
    fig.update_yaxes(title_text=None, showgrid=True, gridcolor='#9D9D9C')
    fig.update_xaxes(title_text=None, linecolor='#9D9D9C')
    top_grant_receivers_plot = offline.plot(fig, output_type='div')

    # Visualizing top funding agencies by funding volume.
    df['Funding Agency'] = (df['Funding Agency'].replace(to_replace='', value='(name unavailable)'))
    gbf = df.groupby('Funding Agency')['Grant Amount, USD'].sum('').to_frame().reset_index()
    gbf.sort_values('Grant Amount, USD', ascending=False, inplace=True)
    gbf['Funding Agency, Concatenated'] = (gbf['Funding Agency'].dropna().
                                           apply(lambda x: f'{x[:30]}...' if len(x) > 30 else x))

    fig = px.bar(
        data_frame=gbf[:50],
        x='Funding Agency, Concatenated',
        y='Grant Amount, USD',
        hover_name='Funding Agency',
        title='Top Funding Agencies by funding volumes, USD'
    )
    fig.update_traces(marker_color='#BC99FF')
    fig.update_layout({'plot_bgcolor': '#FFFFFF', 'paper_bgcolor': '#FFFFFF'},
                      font_family='Calibri',
                      font_color='#646363',
                      font_size=18,
                      title_font_family='Calibri',
                      title_font_color='#646363',
                      legend_title_text=None,
                      legend=dict(
                          yanchor="bottom",
                          y=-0.4,
                          xanchor="center",
                          x=0.5
                      )
                      )
    fig.update_yaxes(title_text=None, showgrid=True, gridcolor='#9D9D9C')
    fig.update_xaxes(title_text=None, linecolor='#9D9D9C')
    top_funders_plot = offline.plot(fig, output_type='div')

    # Visualizing top funding countries by funding volume.
    df['Funding Country'] = (df['Funding Country'].replace(to_replace='', value='(name unavailable)'))
    gbc = df.groupby('Funding Country')['Grant Amount, USD'].sum('').to_frame().reset_index()
    gbc.sort_values('Grant Amount, USD', ascending=False, inplace=True)

    fig = px.bar(
        data_frame=gbc[:50],
        x='Funding Country',
        y='Grant Amount, USD',
        title='Top Funding Countries by funding volumes, USD'
    )
    fig.update_traces(marker_color='#BC99FF')
    fig.update_layout(
        {'plot_bgcolor': '#FFFFFF', 'paper_bgcolor': '#FFFFFF'},
        font_family='Calibri',
        font_color='#646363',
        font_size=18,
        title_font_family='Calibri',
        title_font_color='#646363',
        legend_title_text=None,
        legend=dict(
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5
        )
    )
    fig.update_yaxes(title_text=None, showgrid=True, gridcolor='#9D9D9C')
    fig.update_xaxes(title_text=None, linecolor='#9D9D9C')
    top_countries_plot = offline.plot(fig, output_type='div')

    # Visualizing Average Grant Size by Years
    agvby = pd.merge(gby, df.groupby('Publication Year')['UT'].count(), on='Publication Year')
    agvby['Average Grant Volume'] = agvby['Grant Amount, USD'] / agvby['UT']
    agvby = agvby.rename(columns={'UT': 'Number of Grants', 'Grant Amount, USD': 'Total Funding Volume'})

    fig = px.bar(
        data_frame=agvby,
        y='Average Grant Volume',
        hover_data=['Number of Grants', 'Total Funding Volume'],
        title='Average Grant Volume by Year, USD'
    )
    fig.update_traces(marker_color='#BC99FF')
    fig.update_layout({'plot_bgcolor': '#FFFFFF', 'paper_bgcolor': '#FFFFFF'},
                      font_family='Calibri',
                      font_color='#646363',
                      font_size=18,
                      title_font_family='Calibri',
                      title_font_color='#646363',
                      legend_title_text=None,
                      legend=dict(
                          yanchor="bottom",
                          y=-0.4,
                          xanchor="center",
                          x=0.5
                      ))
    fig.update_yaxes(title_text=None, showgrid=True, gridcolor='#9D9D9C')
    fig.update_xaxes(title_text=None, linecolor='#9D9D9C')
    average_grants_volume_by_years_plot = offline.plot(fig, output_type='div')

    # Visualizing Top Grants by Associated Web of Science Records
    df.sort_values('Related WoS Records Count', ascending=False, inplace=True)
    df['Document Title, Concatenated'] = (df['Document Title'].dropna().
                                          apply(lambda x: f'{x[:120]}...' if len(str(x)) > 120 else x))

    fig = px.bar(
        data_frame=df[:50],
        x='UT',
        y='Related WoS Records Count',
        hover_name='Document Title, Concatenated',
        title='Top Grants by Associated Web of Science Records'

    )
    fig.update_traces(marker_color='#BC99FF')
    fig.update_layout({'plot_bgcolor': '#FFFFFF', 'paper_bgcolor': '#FFFFFF'},
                      font_family='Calibri',
                      font_color='#646363',
                      font_size=18,
                      title_font_family='Calibri',
                      title_font_color='#646363',
                      legend_title_text=None,
                      legend=dict(
                          yanchor="bottom",
                          y=-0.4,
                          xanchor="center",
                          x=0.5
                      ))
    fig.update_yaxes(title_text=None, showgrid=True, gridcolor='#9D9D9C')
    fig.update_xaxes(title_text=None, linecolor='#9D9D9C')
    top_grants_by_associated_wos_records_plot = offline.plot(fig, output_type='div')
    return (grants_by_years_plot,
            top_grant_receivers_plot,
            top_funders_plot,
            top_countries_plot,
            average_grants_volume_by_years_plot,
            top_grants_by_associated_wos_records_plot)
