import importlib
import logging


def check_module(module_name, form_data):
    # Check if the specified module exists in the server
    try:
        module = importlib.import_module(f"modules.{module_name}")
        importlib.reload(module)
        # Check if the validate function is present
        if hasattr(module, 'validate'):
            result = module.validate(**form_data)
            return result
        else:
            raise AttributeError
    except ImportError as e:
        logging.error("Error importing the specified module")
        raise
    except AttributeError as e:
        logging.error("Error in finding validate function")
        raise
    except TypeError as e:
        logging.error("Error in matching arguments")
        raise
    except Exception as e:
        raise
