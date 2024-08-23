import logging
from flask import Flask, request, render_template, session, abort, jsonify
import json
from flask_wtf import CSRFProtect
import validator
from form import generate_form
from asgiref.wsgi import WsgiToAsgi
import aiofiles
import uvicorn

app = Flask(__name__)
asgi_app = WsgiToAsgi(app)
app.config['SECRET_KEY'] = 'secret'  # change this in production
csrf = CSRFProtect(app)


async def load_config():
    try:
        async with aiofiles.open('config/spec.json', 'r') as file:
            config = json.loads(await file.read())
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


@app.route('/', methods=['GET', 'POST'])
async def index():
    config = await load_config()
    scripts = list(config['scripts'].keys())
    selected_option = request.args.get('script', '')
    return render_template('index.html', choices=scripts, selected_option=selected_option)


@app.route('/<script>', methods=['GET', 'POST'])
async def handle_form(script):
    config = await load_config()
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
                result = validator.check_module(module, form_data)
                session['result'] = result
                session['output_type'] = form_spec['output']
                return jsonify(success=True)
            except Exception as e:
                logging.error(e)
                return jsonify(success=False, err_message="Internal server error"), 500
        else:
            input_err = {field.name: field.errors for field in form if field.errors}
            return jsonify(success=False, input_err=input_err), 400

    return render_template('index.html', choices=scripts, selected_option=script, form=form)


@app.route('/load_form/<script>', methods=['GET'])
async def load_form(script):
    config = await load_config()

    if script not in config['scripts']:
        abort(404, description="Not found")

    form_spec = config['scripts'][script]
    DynamicForm = generate_form(form_spec)
    form = DynamicForm()

    return render_template('form.html', form=form, script=script)


@app.route('/submit')
def submit_form():
    result = session.pop('result', ["No result available"])
    output_type = session.pop('output_type', ["text"])

    return render_template('result.html', result=result, output_type=output_type)


@app.errorhandler(Exception)
async def handle_error(e):
    err_code = getattr(e, 'code', 500)
    err_message = getattr(e, 'description', 'Internal server error')
    return render_template("error.html", err_code=err_code, err_message=err_message), err_code


if __name__ == '__main__':
    host = '127.0.0.1'  # for local development
    port = 5000
    uvicorn.run(asgi_app, host=host, port=port)
