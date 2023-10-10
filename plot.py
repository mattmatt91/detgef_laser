import plotly.express as px
import pandas as pd


def plot(path:str):
    # path  = "data\\08-30-2023_14-51-05.csv"


    df = pd.read_csv(path, delimiter=',', decimal='.')
    print(df)

    df.set_index('timestamp', inplace=True)
    fig = px.line(df)
    path = path.replace('.csv','.html')
    fig.write_html(path
    )
    fig.show()