import logging
import uuid
from flask import Flask, request, render_template, abort, jsonify, url_for
from flask_wtf import CSRFProtect
from waitress import serve
from utils import validator
from utils import generate_form
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from models import ConfigModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'  # change this in production
csrf = CSRFProtect(app)

# for threading
executor = ThreadPoolExecutor(max_workers=5)    # change the number of workers according to need

# for multiprocessing
# executor = ProcessPoolExecutor(max_workers=2) # change the number of workers according to need

# a temporary storage for results
temp = {}


@app.route('/', methods=['GET'])
def index():
    scripts = ConfigModel.get_script_keys()
    selected_option = request.args.get('script', '')
    return render_template('index.html', choices=scripts, selected_option=selected_option)


@app.route('/load_form/<script>', methods=['GET'])
def load_form(script):
    form_spec = ConfigModel.get_script_spec(script)

    if form_spec is None:
        abort(404, description="Not found")

    # generate the form
    DynamicForm = generate_form(form_spec)
    form = DynamicForm()

    return render_template('form.html', form=form, script=script)


@app.route('/<script>', methods=['GET', 'POST'])
def handle_form(script):
    scripts = ConfigModel.get_script_keys()
    form_spec = ConfigModel.get_script_spec(script)
    if form_spec is None:
        abort(404, description="Not found")

    DynamicForm = generate_form(form_spec)
    form = DynamicForm()

    if request.method == "POST":
        # validate the inputs
        if form.validate_on_submit():
            form_data = {}

            # get all the form data
            for field_name, field in form._fields.items():
                if field_name not in ['csrf_token', 'submit']:
                    form_data[field_name] = field.data

            if request.files:
                for key, file in request.files.items():
                    if file.filename:
                        # store the file as bytes as FileStorage type is not serialisable for multiprocessing
                        with file.stream as file_stream:
                            file_data = file_stream.read()
                            form_data[key] = file_data

            module = form_spec['module']

            try:
                # create a new thread/process for the task
                future = executor.submit(validator.check_module, module, form_data)
                result = future.result()
                result_id = str(uuid.uuid4())
                # store the result temporarily
                temp[result_id] = {'result': result, 'output_type': form_spec['output']}
                redirect_url = url_for('submit_result', result_id=result_id)
                return jsonify(success=True, redirect_url=redirect_url)
            except Exception as e:
                logging.error(e)
                return jsonify(success=False, err_message="Internal server error"), 500
        else:
            # if have invalid input
            input_err = {field.name: field.errors for field in form if field.errors}
            return jsonify(success=False, input_err=input_err), 400

    return render_template('index.html', choices=scripts, selected_option=script, form=form)


@app.route('/result/<result_id>')
def submit_result(result_id):
    # pop the result from the temporary storage
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

    # for development stage use debug level
    logger.setLevel(logging.DEBUG)

    # use app.run(threaded=True) if running with Flask server for development
    # remove threads=4 when running in multiprocessing environment
    serve(app, host='127.0.0.1', port=5000, threads=4)
