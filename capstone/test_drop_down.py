from flask import Flask, render_template, request
import csv
from os import path
import pandas as pd
from call_bert import rankSimilarity
app = Flask(__name__)

script_dir = path.dirname(path.abspath(__file__))
prosper_df = pd.read_excel('./data/prosperdata/Data-Variable-Definitions.xlsx')
column_def = {key:val for key, val in zip(prosper_df.Variable.values, prosper_df.Description.values)}

@app.route ("/")
def index():
    return render_template("index.html", server_list=list(column_def)) 

@app.route("/submitted", methods=["GET", "POST"])
def hello():
    if request.method == "GET":
        return render_template("index.html", server_list=list(column_def)) 
    #filefullpath = script_dir + '//newTest.csv'
    input_column_name = request.form["columnDropdown"]
    match_result = rankSimilarity(column_def[input_column_name])
    result = pd.DataFrame.from_dict(match_result).T.sort_values('rank').to_html()
    
    return result


if __name__ == "__main__":
	app.run(debug=True)