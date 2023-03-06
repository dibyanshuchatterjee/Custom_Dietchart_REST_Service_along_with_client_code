"""
author: Dibyanshu Chatterjee
username: dc7017
"""
import json
from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    """
    This function serves to return the home page
    :return: index.html page
    """
    return render_template("index.html")


# routing the result into the result page
@app.route('/result', methods=['POST', 'GET'])
def result():
    """
    This function helps fetch data from the webpage and also projects the results.
    :return: The result page
    """

    endpoint = "http://127.0.0.1:8000/"
    # user inputs the following details:
    extracted_form = request.form.to_dict()
    weight_unit = extracted_form['Weight_Units']
    height_unit = extracted_form['height_unit']
    weight = float(extracted_form["Weight"])
    height = float(extracted_form['height'])
    age = int(extracted_form['age'])
    sex = extracted_form['sex']
    goal = extracted_form['goal']
    activity = int(extracted_form['activity'])
    choice_of_cuisine = extracted_form['choice_of_cuisine']
    preffered_number_of_meals = int(extracted_form['preffered_number_of_meals'])

    data = {
        "sex": sex,
        "weight_unit": weight_unit,
        "height_unit": height_unit,
        "weight": weight,
        "height": height,
        "age": age,
        "goal": goal,
        "activity": activity,
        "choice_of_cuisine": choice_of_cuisine,
        "preffered_number_of_meals": preffered_number_of_meals,
        "num_of_weights": 1,
        "username": "example_user1",
        "password": "example_password"
    }

    json_data = json.dumps(data)
    response1 = requests.post(endpoint + "generateDietChart", data=json_data)
    response2 = requests.get(endpoint + "generateDietChart/showWeightProgress?num=1", headers={'username': 'example_user1'})

    return render_template('index.html', tracked_weight_s=str(response2.json()), diet_chart=str(response1.json()))


if __name__ == '__main__':
    app.run(debug=True, port=8182)
