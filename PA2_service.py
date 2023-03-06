"""
author: Dibyanshu Chatterjee
username: dc7017
"""
from fastapi import FastAPI, Body, Request
import uvicorn
import app as PA1_app
import sqlite3
import datetime

app = FastAPI()

# create database
connection = sqlite3.connect("diet_chart_details.db")
# communicate with the database
cursor = connection.cursor()
# create database table
cursor.execute(
    "create table if not exists user_data_v1 (id INTEGER PRIMARY KEY AUTOINCREMENT, weight_in_kg varchar(5), height_in_cm varchar(5), age varchar (5), calculated_bmr varchar (5), weighing_date varchar (25))")
cursor.execute(
    "CREATE TABLE IF NOT EXISTS user_data_authenticate (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(25) UNIQUE, password VARCHAR(25))")

# save changes immediatley
connection.commit()
# flag value to ensure coordination
coordination_track = False


@app.get("/")
async def root():
    """
    root call
    """
    return {"message": "This service will help you generate a diet chart"}


def update_backend(data_list):
    """
    This function updates the backend database
    :param data_list: The list of tuples having hte data
    :return: None
    """
    cursor.executemany(
        "INSERT INTO user_data_v1 (weight_in_kg, height_in_cm, age, calculated_bmr, weighing_date) VALUES (?, ?, ?, ?, ?)",
        data_list)
    connection.commit()


@app.post("/generateDietChart/")
async def process_input(text_data: dict = Body(...)):
    """
    This function processes the input data to generate diet chart using the PA1 code
    :param text_data: The input data from client's side
    :return: json response
    """
    username = text_data.get('username')
    password = text_data.get('password')

    # insert the username and password only if they don't already exist
    query = "INSERT INTO user_data_authenticate (username, password) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM user_data_authenticate WHERE username=? AND password=?)"
    cursor.execute(query, (username, password, username, password))
    connection.commit()

    sex = text_data.get("sex")
    weight_unit = text_data.get("weight_unit")
    height_unit = text_data.get("height_unit")
    weight = text_data.get("weight")
    height = text_data.get("height")
    age = text_data.get("age")
    goal = text_data.get("goal")
    activity = text_data.get("activity")
    choice_of_cuisine = text_data.get("choice_of_cuisine")
    preffered_number_of_meals = text_data.get("preffered_number_of_meals")
    # converting the values to right unit if needed
    if weight_unit.lower() != "kgs" and weight_unit.lower() != "kg":
        weight_in_kg = weight / 2.2

    else:
        weight_in_kg = weight

    if height_unit.lower() != "cms" and height_unit.lower() != "cm":
        height_in_cm = height * 30.48

    else:
        height_in_cm = height
    calculated_bmr = PA1_app.calculate_bmr(sex=sex, weight=weight_in_kg, height=height_in_cm, age=age)

    suggested_calories_per_day = PA1_app.suggest_calories(bmr=calculated_bmr, goal=goal, activity=activity)

    macros_dict = PA1_app.evaluate_macros(calories=suggested_calories_per_day, goal=goal)

    result = PA1_app.generate_payload(choice_of_cuisine=choice_of_cuisine, macro_dict=macros_dict, age=age, sex=sex,
                                      goal=goal,
                                      preffered_number_of_meals=preffered_number_of_meals)

    if result is False:
        loc_result = "This application only works for fat loss or mass gain GOALS"
    else:
        payload = {
            "question": result,
            "max_response_time": 30
        }
        print("Below here are your details: ")
        print("Your weight in kgs: " + str(weight_in_kg))
        print("Your height in cms: " + str(height_in_cm))
        print("Your age: " + str(age))
        print("Your BMR: " + str(calculated_bmr))
        print()

        today_date = datetime.date.today()
        # input data for backend
        user_detail_list = [
            (str(weight_in_kg), str(height_in_cm), str(age), str(calculated_bmr), str(today_date))
        ]

        update_backend(data_list=user_detail_list)

        print("Below here is your diet chart: ")
        str_to_write = PA1_app.ask_chatGPT(payload=payload)
        if goal.lower() == "loose":
            filename = "Fat_Loss_Diet_Chart_Sample"
        elif goal.lower() == "gain":
            filename = "Mass_Gain_Diet_Chart_Sample"
        else:
            return "The application only works for fat loss or mass gain goals"
        loc_result = PA1_app.write_text(filename, str_to_write)
    connection.close()
    global coordination_track
    coordination_track = True
    return {"diet_chart": loc_result}


@app.get("/generateDietChart/showWeightProgress")
async def show_weights(num: int, request: Request):
    """
    This function aids in providing the weight progress by providing last 'num' number of weights tracked
    :param num: Integer
    :param request: The header request object
    :return: json response
    """
    if coordination_track is not True:
        search_res = "You need to get your diet chart first"
    else:
        username = request.headers.get('username')
        connection = sqlite3.connect("diet_chart_details.db")
        # communicate with the database
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM user_data_authenticate WHERE username=?", (username,))
        result = cursor.fetchone()
        if result is None:
            search_res = "The username does not exist in the database"
        else:
            # num = text_data.get("num_of_weights")
            cursor.execute("select weight_in_kg, weighing_date from user_data_v1 order by id desc LIMIT :c", {"c": num})
            search_res = cursor.fetchall()
        connection.close()
    return {"weights": search_res}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
