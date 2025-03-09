import os

from dotenv import load_dotenv

load_dotenv()

# Constants: --------------------------------------------
ENV_LOC = ".env"


# Functions: --------------------------------------------


def build_import_string(env_name):
    return f'{env_name} = os.getenv("{env_name}")'


def load_envs(env_file):
    # Load the .env file:
    env_lines = []
    with open(env_file, "r") as f:
        env_lines = f.readlines()

    # Get the environment variables:
    env_vars = []
    for line in env_lines:
        env_name = line.split("=")[0]
        env_vars.append(env_name)

    # Build the import string:
    import_string = "\n".join([build_import_string(env_name) for env_name in env_vars])

    print(f"\n\nImport String: \n\n{import_string}\n\n")
    # Write the import string to the config file:
    # with open("config.py", "a") as f:
    #    f.write(import_string)


def print_envs():
    load_envs(ENV_LOC)  # Import Variables: -------------------------------------
