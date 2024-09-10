import json
import logging
import os.path


class ConfigModel:
    _config = None
    _last_modified = None

    # Check whether the file has been updated since last retrieved
    @staticmethod
    def check_update(path):
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            logging.error("Configuration file not found")
            raise

    @staticmethod
    def load_config():
        path = 'config/spec.json'
        modify_time = ConfigModel.check_update(path)

        # only read the file for the first time or if it is updated
        if ConfigModel._config is None or modify_time != ConfigModel._last_modified:
            try:
                with open(path, 'r') as file:
                    ConfigModel._config = json.loads(file.read())
                # update the modified time
                ConfigModel._last_modified = modify_time
            except json.decoder.JSONDecodeError:
                logging.error("Error decoding configuration file")
                raise
            except Exception as e:
                logging.error(e)
                raise

    # get the list of available scripts
    @staticmethod
    def get_script_keys():
        ConfigModel.load_config()
        config = ConfigModel._config
        return list(config['scripts'].keys())

    # get the specification of the selected script
    @staticmethod
    def get_script_spec(script):
        ConfigModel.load_config()
        config = ConfigModel._config

        if script not in config['scripts']:
            return None

        return config['scripts'][script]
