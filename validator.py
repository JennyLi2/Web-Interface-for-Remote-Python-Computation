import importlib


def check_module(module_name: str, form_data: dict):
    # to check if the specified module exist in the server
    try:
        module = importlib.import_module(f"modules.{module_name}")
        result = module.validate(**form_data)
        return result
    except (ImportError, NameError):
        return False

