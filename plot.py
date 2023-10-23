
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
    fig = px.line(df, x=df.index, y=[df['sensor laser'], df['sensor no laser']] , color='step_id', markers=False, title='Sensor Data')
    fig.update_layout(xaxis_title='Timestamp', yaxis_title='Sensor Values')
    fig.write_html(join(path, "plot.html"))
    fig.show()
 
def plot(path:str):
    df = read_data(path)
    print(df)
    make_plot(path, df)


if __name__ == '__main__':
    path = 'data\\10-19-2023_08-55-50'
    plot(path)