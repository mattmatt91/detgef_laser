
import pandas as pd
import plotly.express as px
from os.path import join
 
 
def read_data(path: str):
    df = pd.read_csv(join(path, "data.csv"), sep=',', decimal='.')
    df['timestamp'] = pd.to_datetime(
        df['timestamp'], format='%H:%M:%S').dt.time
    df.set_index("timestamp", inplace=True)
    # print(df)
    return df
 
def make_plot(path:str , df: pd.DataFrame):
    fig = px.line(df, x=df.index, y=['sensor 1', 'sensor 2'] , color='names', markers=False, title='Sensor Data')
    fig.update_layout(xaxis_title='Timestamp', yaxis_title='Sensor Values')
    fig.write_html(join(path, "plot_coloured.html"))
    fig.show()
 
def plot(path:str):
    df = read_data(path)
    make_plot(path, df)