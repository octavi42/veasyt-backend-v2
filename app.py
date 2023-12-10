from flask import Flask, request, jsonify
from utils.generate_location import process_story, interprete_prompt, get_transport_from_prompt
import json
import uuid

app = Flask(__name__)

with open("data.json", "r") as file:
    user_conditions_data = json.load(file)["users"]

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/generate_tour", methods=["POST"])
def generate_tour():
    try:
        req_prompt = request.get_json()["prompt"]
    except KeyError:
        return "Please provide a prompt in the request body with the key 'prompt'", 400


    prompt = interprete_prompt(req_prompt)
    
    try:
        prompt_dict = json.loads(prompt)
    except json.JSONDecodeError:
        return "Invalid JSON format"

    location = prompt_dict.get("location")
    days = prompt_dict.get("days")

    if not location:
        return "Please provide a location"
    
    if not days:
        return "Please provide the number of days"
    
    ret = {
        "location": location,
        "days": days,
        "tours": process_story(location, days)
    }
    
    return ret


@app.route("/get_transport", methods=["GET"])
def get_transport():
    return get_transport_from_prompt("wheelchair, blind", "Eiffel Tower", "Notre-Dame-Cathedral")


@app.route("/generate_tour_v2", methods=["GET"])
def generate_tour_v2():

    prompt = interprete_prompt("I want to visit the city of Paris from the 1st of January to the 5th of January and I am blind and I am in a wheelchair.")
    
    return prompt


@app.route("/get_user_conditions", methods=["POST"])
def get_user_conditions():

    req_id = request.get_json()["id"]
    
    print(req_id)

    user_conditions = find_user_conditions(req_id)

    # if not user_conditions:
    #     user_conditions = {
    #         "id": req_id,
    #         "conditions": []
    #     }


    return user_conditions["condition"]

def find_user_conditions(search_id):
    for user_condition in user_conditions_data:
        if user_condition.get("id") == search_id:
            return user_condition
    return None


def load_users():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
            if 'users' not in data:
                data['users'] = []
            return data
    except FileNotFoundError:
        return {'users': []}

def save_users(users_data):
    with open('data.json', 'w') as file:
        json.dump(users_data, file, indent=2)

@app.route('/user', methods=['POST'])
def create_user():
    user_data = request.json
    users_data = load_users()
    user_data['id'] = generate_cuid()
    users_data['users'].append(user_data)
    save_users(users_data)
    return jsonify({"message": "User created successfully"}), 201


def generate_cuid():
    cuid_prefix = "cj"
    cuid_suffix = str(uuid.uuid4().fields[-1])[:10]
    cuid = f"{cuid_prefix}{cuid_suffix}"
    return cuid


if __name__ == "__app__":
   app.run(debug=True, port=5002)



@app.route("/generate_tour_with_conditions", methods=["POST"])
def generate_tour_with_conditions():
    req_prompt = request.get_json()["prompt"]
    req_id = request.get_json()["id"]

    user_conditions = find_user_conditions(req_id)

    conditions = ""

    for condition in user_conditions["condition"]:
        conditions += condition["name"] + ", "

    conditions = conditions[:-2]

    print(conditions)

    # prompt = interprete_prompt(req_prompt)
    
    # try:
    #     prompt_dict = json.loads(prompt)
    # except json.JSONDecodeError:
    #     return "Invalid JSON format"

    # location = prompt_dict.get("location")
    # days = prompt_dict.get("days")

    # if not location:
    #     return "Please provide a location"
    
    # if not days:
    #     return "Please provide the number of days"
    
    return conditions