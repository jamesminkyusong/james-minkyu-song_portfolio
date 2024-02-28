import os
import configparser

config_file = r"C:\Users\Lenovo\Desktop\Coursework\23_fall\fingerspelling\settings.ini"
def get_config():
    """Read the configuration file and return the settings."""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_path(section_name, var_name):
    """Return the path for the given section_name, var_name from the config."""
    config = get_config()
    return config.get(section_name, var_name)


def list_all_files(path):
    """Return a list of all files in a directory and its subdirectories."""
    file_list = []

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            file_list.extend(list_all_files(full_path))  # Recursive call for subdirectories
        else:
            file_list.append(full_path)

    return file_list

def write_to_csv(df, section_name, var_name):
    path = get_path(section_name, var_name)
    df.to_csv(path, index=False)