import pandas as pd
import json
from IPython.display import Javascript, display
        
def plot(data, config):
    init()
    inject(data)
    inject(config, name='config')
    render()
      
### Internal utils
def _ix_to_time(ix):
    if isinstance(ix, pd.Timestamp):
        return int(ix.strftime('%s'))
    else:
        return int(ix)
    
# Use to process series into lw_data before using inject
def transform_series(series):
    return [
        {'time': _ix_to_time(ix), 'value': float(val)}
        for ix, val in series.iteritems()
    ]   

# Use if you want low level control over what's injected
def init():
    display(Javascript("""
        if (typeof window.chart_data !== 'object') {
            window.chart_data = {}
        }
    """))
    
def inject_json(data, name):
    display(Javascript(f'window.chart_data["{name}"] = {json.dumps(data)};'))

# Use to automatically transform and inject pd.Series
def inject_series(series, name=None):
    return inject_json(transform_series(series), series.name if name is None else name)
    
# Use to automatically transform and inject pd.DataFrame
def inject_df(df):
    for col in df.columns:
        inject_series(df[col])
    
def inject(data, name=None):
    if isinstance(data, pd.Series):
        inject_series(data, name)
    elif isinstance(data, pd.DataFrame):
        inject_df(data)
    else:
        inject_json(data, name)

def cleanup():
    display(Javascript("window.chart_data = undefined"))
        
def render():
    return display(Javascript("""
    // Describe dependencies
    require.config({
        paths: {
            'lightweight-charts': ['//unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production']
        },
        shim: {
            'lightweight-charts': {
                exports: "LightweightCharts",
            },
        }
    });
        
    require(['lightweight-charts'], function() {    
        // (Re-)create div to display the chart in
        $("#chart").remove();
        element.append("<div id='chart' style='margin-top: 1em;'></div>");

        // Create chart
        const chart = LightweightCharts.createChart('chart', { width: 800, height: 350 });

        
        // config and chart_data should be injected in advance by calling any inject_* function
        chart_data.config.forEach(it => {
            const params = {'title': it['name'], ...it['style']}
            const data = chart_data[it['name']]

            chart[it['fn']](params).setData(data)
        })
        
        // Apply settings
        chart.applyOptions({
            priceScale: {
                scaleMargins: {
                    top: 0.30,
                    bottom: 0.25,
                },
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: true,
                rightOffset: 5
            },
        });

        // Make prices fully visible
        document.querySelector("#chart > div > table > tr:nth-child(1) > td:nth-child(3) > div").style["left"] = "-30px";
        // Make legend fully visible
        document.querySelector("#chart > div > table > tr:nth-child(1) > td:nth-child(2) > div").style["left"] = "-30px"; 
    })
    """))