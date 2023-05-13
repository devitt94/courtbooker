from dotenv import dotenv_values

__list_vars = ["VENUES", "RECEIVER_EMAILS"]

config = dotenv_values(".env")
for key in __list_vars:
    config[key] = config[key].split(",")
