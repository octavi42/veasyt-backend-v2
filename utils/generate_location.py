import os

import json
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
import requests

from dotenv import load_dotenv



load_dotenv()
# client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model="gpt-4-1106-preview"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ['OPENAI_API_KEY'],
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e



def process_story(location, days, conditions="None"):

    number_of_tours = days
    if days < 5:
        number_of_tours = days * 2

    model = "gpt-4-1106-preview"
    messages = [
        {"role": "system", "content": "you are a guide trip planner for persons with disabilities"},
        {"role": "user", "content": f'what are the best {number_of_tours} trips to take for the person with this disabilities {conditions} can take in {location}?'},
    ]

    tools = [
        {
        "type": "function",
        "function": {
            "name": "get_tours",
            "description": "Get the best trip for the person with disabilities",
            "parameters": {
                "type": "object",
                "properties": {
                    "tour": {
                        "type": "array",
                        "items": {
                            "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "the name of the tour"
                                        },
                                    "lat": {
                                        "type": "string",
                                        "description": "the latitude of the tour"
                                        },
                                    "lon": {
                                        "type": "string",
                                        "description": "the longitude of the tour"
                                        },
                                    "what_todo": {
                                        "type": "string",
                                        "description": "the description of what to do at the tour"
                                    },
                                    "near_help": {
                                        "type": "object",
                                        "description": "nearby hospital if there is one",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "description": "the name of the tour"
                                                },
                                            "lat": {
                                                "type": "string",
                                                "description": "the latitude of the tour"
                                                },
                                            "lon": {
                                                "type": "string",
                                                "description": "the longitude of the tour"
                                                },
                                        }
                                    }
                                }
                        }
                    }
                },
                "required": ["tours"],
            },
        }
        },
    ]


    chat_response = chat_completion_request(
        messages, tools=tools, tool_choice={"type": "function", "function": {"name": "get_tours"}},
    )

    output = chat_response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]

    print(chat_response.json()["choices"][0]["message"])

    return output


def interprete_prompt(prompt):

    messages = [
        {"role": "system", "content": "you are an advanced prompt interpreter"},
        {"role": "user", "content": f'give me the location and the number of days of the trip that the person wants to take, {prompt}'},
    ]

    tools = [
        {
        "type": "function",
        "function": {
            "name": "get_interpretation",
            "description": "the location and number of the days of the trip and medical disabilities of the person",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "city that the person wants to visit"
                    },
                    "days": {
                        "type": "number",
                        "description": "give me the number of days, if the user gives you the date do tha calculation to get the number of days"
                    },
                    "disabilities": {
                        "type": "array",
                        "description": "the disabilities of the person if it has any",
                        "items": {
                            "type": "string",
                            "description": "the disability of the person"
                        }
                    },
                },
                "required": ["get_interpretation"],
            },
        }
        },
    ]


    chat_response = chat_completion_request(
        messages, tools=tools, tool_choice={"type": "function", "function": {"name": "get_interpretation"}},
    )

    output = chat_response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]

    return output




def get_transport_from_prompt(conditions, location, destination):

    messages = [
        {"role": "system", "content": "you are an advanced medical prompt helper for people with disabilities"},
        {"role": "user", "content": f'considering I have the following disabilities {conditions}, what is the best transport for me from {location} to {destination}?'},
    ]

    tools = [
        {
        "type": "function",
        "function": {
            "name": "get_transport",
            "description": "the name of the transport",
            "parameters": {
                "type": "object",
                "properties": {
                    "transportation_type": {
                        "type": "string",
                        "description": "give me in one word the type of transportation"
                    },
                    "duration": {
                        "type": "number",
                        "description": "the duration of the trip in seconds"
                    },
                    "additional_info": {
                        "type": "string",
                        "description": "the additional information I need to know about the trip considering my disabilities"
                    },
                },
                "required": ["duration"],
            },
        }
        },
    ]


    chat_response = chat_completion_request(
        messages, tools=tools, tool_choice={"type": "function", "function": {"name": "get_transport"}},
    )

    output = chat_response.json()["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]

    return output


    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_tours",
    #         "description": "Get the best trip for the person with disabilities",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "tour": {
    #                     "type": "array",
    #                     "items": {
    #                         "type": "object",
    #                             "properties": {
    #                                 "name": {
    #                                     "type": "string",
    #                                     "description": "the name of the tour"
    #                                     },
    #                                 "lat": {
    #                                     "type": "string",
    #                                     "description": "the latitude of the tour"
    #                                     },
    #                                 "lon": {
    #                                     "type": "string",
    #                                     "description": "the longitude of the tour"
    #                                     },
    #                                 "what_todo": {
    #                                     "type": "string",
    #                                     "description": "the description of what to do at the tour"
    #                                 },
    #                                 "near_help": {
    #                                     "type": "object",
    #                                     "description": "nearby hospital if there is one",
    #                                     "properties": {
    #                                         "name": {
    #                                             "type": "string",
    #                                             "description": "the name of the tour"
    #                                             },
    #                                         "lat": {
    #                                             "type": "string",
    #                                             "description": "the latitude of the tour"
    #                                             },
    #                                         "lon": {
    #                                             "type": "string",
    #                                             "description": "the longitude of the tour"
    #                                             },
    #                                     }
    #                                 }
    #                             }
    #                     }
    #                 }
    #             },
    #             "required": ["tours"],
    #         },
    #     }
    #     },