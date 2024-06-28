from flask import Flask, request, render_template, redirect, url_for, session, abort
import json
import logging
import validator

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


@app.route('/', methods=['GET', 'POST'])
def form():
    with open('config/spec.json', 'r') as file:
        config = json.load(file)
    form_spec = config['scripts']

    if request.method == "POST":
        form_data = request.form.to_dict()
        app.logger.info(form_data)
        choice = form_data.pop('choice')
        module = form_spec[choice]['module']

        result = validator.check_module(module, form_data)
        if result:
            session['result'] = str(result)
            session['output_type'] = form_spec[choice]['output']
            return redirect(url_for('submit_form'))
        else:
            print("Module not found.")
            abort(404)

    return render_template('form.html', choices=form_spec)


@app.route('/submit')
def submit_form():
    result = (session.pop('result', None))
    output_type = (session.pop('output_type', None))
    if result is not None:
        return render_template('result.html', result=result, output_type=output_type)
    else:
        return redirect(url_for('form'))


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('form.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
