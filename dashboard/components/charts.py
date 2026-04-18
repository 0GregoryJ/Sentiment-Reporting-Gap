import plotly.express as px
import streamlit as st

def generate_main_chart(filtered_data, data_selection, range_selection):
    main_chart = px.line(
        filtered_data,
        x="date",
        y=f"{data_selection}_gap",
    )
    #chart title
    title_dict = {
        "labor": f"Labor Market Stress: Sentiment-Reporting Gap Over the Last {range_selection}",
        "spending": f"Consumer Spending: Sentiment-Reporting Gap Over the Last {range_selection}",
    }
    main_chart.update_layout(title=title_dict[data_selection])
    
    #remove gridlines
    main_chart.update_yaxes(showgrid=False)

    #remove axis labels
    main_chart.update_layout(xaxis_title=None, yaxis_title=None)

    st.plotly_chart(main_chart, use_container_width=True)

def generate_mini_chart(filtered_data, keyword):
    mini_chart = px.line(
        filtered_data,
        x="date",
        y=keyword,
    )
    #chart title
    title_and_label_dict = {
        "LNS14000000": ["Unemployment Rate", "Percent"],
        "CES0500000002": ["Average weekly hours", "Hours"],
        "CES0000000001": ["Payroll Employment", "Thousands of Paid Workers"],
        "unemployment_benefits": ['"Unemployment Benefits"', "Google Trends Units"],
        "second_job": ['"Second Job"', "Google Trends Units"],
        "layoffs": ['"Layoffs"', "Google Trends Units"]
    }
    mini_chart.update_layout(title=title_and_label_dict[keyword][0])
    
    #remove gridlines
    mini_chart.update_yaxes(showgrid=False)

    #remove axis labels
    mini_chart.update_layout(xaxis_title=None, yaxis_title=title_and_label_dict[keyword][1])

    #connectgaps
    mini_chart.update_traces(connectgaps = True)

    st.plotly_chart(mini_chart, use_container_width=True)