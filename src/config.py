import os
from dotenv import dotenv_values

__list_vars = ["VENUES", "RECEIVER_EMAILS"]
__int_vars = ["SMTP_PORT", "LOOK_AHEAD_DAYS"]

config = {
    **dotenv_values(".env"),
    **os.environ,
}

for key in __list_vars:
    config[key] = config[key].split(",")

for key in __int_vars:
    config[key] = int(config[key])
