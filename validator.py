import importlib
import logging


def check_module(module_name, form_data):
    # Check if the specified module exists in the server
    try:
        module = importlib.import_module(f"modules.{module_name}")
        result = module.validate(**form_data)
        return result
    except (ImportError, NameError) as e:
        logging.error("Error importing the specified module")
        raise e
    except TypeError as e:
        logging.error("Error in matching arguments of the module validator")
        raise e
    except Exception as e:
        raise e
