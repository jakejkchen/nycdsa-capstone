from flask import Flask, render_template, request
import csv
from os import path
app = Flask(__name__)

script_dir = path.dirname(path.abspath(__file__))

@app.route ("/")
def index():
    return render_template("index.html", server_list=[1, 2, 3]) 

@app.route("/submitted", methods=["GET", "POST"])
def hello():
    if request.method == "GET":
        return render_template("index.html", server_list=[1, 2, 3]) 
    filefullpath = script_dir + '//newTest.csv'
    myvariable = request.form["teamDropdown"]
    with open(filefullpath, mode="w+") as file:
        fileWriter = csv.writer(file)
        fileWriter.writerow([myvariable])
    file.close()
    return "hello world"


if __name__ == "__main__":
	app.run(debug=True)