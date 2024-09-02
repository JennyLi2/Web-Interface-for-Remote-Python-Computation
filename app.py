import logging
import uuid
from flask import Flask, request, render_template, abort, jsonify, url_for
import json
from flask_wtf import CSRFProtect
from waitress import serve
import validator
from form import generate_form
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'  # change this in production
csrf = CSRFProtect(app)
executor = ThreadPoolExecutor(max_workers=5)    # change the number of workers according to need
temp = {}


def load_config():
    try:
        with open('config/spec.json', 'r') as file:
            config = json.loads(file.read())
    except FileNotFoundError:
        logging.error("Configuration file not found")
        abort(500)
    except json.decoder.JSONDecodeError:
        logging.error("Error decoding configuration file")
        abort(500)
    except Exception as e:
        logging.error(e)
        abort(500)
    return config


@app.route('/', methods=['GET'])
def index():
    config = load_config()
    scripts = list(config['scripts'].keys())
    selected_option = request.args.get('script', '')
    return render_template('index.html', choices=scripts, selected_option=selected_option)


@app.route('/<script>', methods=['GET', 'POST'])
def handle_form(script):
    config = load_config()
    scripts = list(config['scripts'].keys())

    if script not in config['scripts']:
        abort(404, description="Not found")

    form_spec = config['scripts'][script]
    DynamicForm = generate_form(form_spec)
    form = DynamicForm()

    if request.method == "POST":
        if form.validate_on_submit():
            form_data = {}
            for field_name, field in form._fields.items():
                if field_name not in ['csrf_token', 'submit']:
                    form_data[field_name] = field.data

            if request.files:
                for key, file in request.files.items():
                    if file.filename:
                        form_data[key] = file

            module = form_spec['module']

            try:
                future = executor.submit(validator.check_module, module, form_data)
                result = future.result()
                result_id = str(uuid.uuid4())
                temp[result_id] = {'result': result, 'output_type': form_spec['output']}
                redirect_url = url_for('submit_result', result_id=result_id)
                return jsonify(success=True, redirect_url=redirect_url)
            except Exception as e:
                logging.error(e)
                return jsonify(success=False, err_message="Internal server error"), 500
        else:
            input_err = {field.name: field.errors for field in form if field.errors}
            return jsonify(success=False, input_err=input_err), 400

    return render_template('index.html', choices=scripts, selected_option=script, form=form)


@app.route('/load_form/<script>', methods=['GET'])
def load_form(script):
    config = load_config()

    if script not in config['scripts']:
        abort(404, description="Not found")

    form_spec = config['scripts'][script]
    DynamicForm = generate_form(form_spec)
    form = DynamicForm()

    return render_template('form.html', form=form, script=script)


@app.route('/result/<result_id>')
def submit_result(result_id):
    data = temp.pop(result_id)
    result, output_type = data.values()

    return render_template('result.html', result=result, output_type=output_type)


@app.errorhandler(Exception)
def handle_error(e):
    err_code = getattr(e, 'code', 500)
    err_message = getattr(e, 'description', 'Internal server error')
    return render_template("error.html", err_code=err_code, err_message=err_message), err_code


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('waitress')

    logger.setLevel(logging.DEBUG)  # for development stage use debug level

    # or use app.run(threaded=True) if running with Flask server for development
    serve(app, host='127.0.0.1', port=5000, threads=4)
