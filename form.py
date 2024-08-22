from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, DateField, TimeField, TextAreaField, SelectField, RadioField, FileField, SubmitField
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.numeric import DecimalField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, InputRequired
from flask_wtf.file import FileAllowed


def generate_form(fields):
    class DynamicForm(FlaskForm):
        pass

    for field in fields['inputFields']:
        field_args = {
            'label': field['label'],
            'validators': [],
            'description': field.get('description', ""),
            'default': field.get('default', None),
            'render_kw': {}
        }

        # Add validators
        if field.get('required') == 'true':
            if field['type'] in ['text', 'textarea']:
                field_args['validators'].append(DataRequired())
            else:
                field_args['validators'].append(InputRequired())
        else:
            field_args['validators'].append(Optional())

        # Add other attributes to render_kw
        if field.get('placeholder'):
            field_args['render_kw']['placeholder'] = field['placeholder']
        if field.get('readonly') == 'true':
            field_args['render_kw']['readonly'] = True

        # Check the input type
        if field['type'] == 'text':
            form_field = StringField(**field_args)
            if 'min' in field:
                field_args['validators'].append(Length(min=field['min']))
            if 'max' in field:
                field_args['validators'].append(Length(max=field['max']))
        elif field['type'] == 'textarea':
            form_field = TextAreaField(**field_args)
        elif field['type'] == 'number':
            form_field = IntegerField(**field_args)
        elif field['type'] == 'float':
            form_field = FloatField(**field_args)
        elif field['type'] == 'decimal':
            form_field = DecimalField(**field_args)
        elif field['type'] == 'hidden':
            form_field = HiddenField(**field_args)
        elif field['type'] == 'boolean':
            if field['default'] == 'false':
                field_args['default'] = False
            elif field['default'] == 'true':
                field_args['default'] = True
            form_field = BooleanField(**field_args)
        elif field['type'] == 'select':
            choices = field.get('choices', [])
            form_field = SelectField(choices=choices, **field_args)
        elif field['type'] == 'radio':
            choices = field.get('choices', [])
            form_field = RadioField(choices=choices, **field_args)
        elif field['type'] == 'file':
            allowed_extensions = field.get('extension', [])
            if allowed_extensions:
                field_args['validators'].append(FileAllowed(allowed_extensions))
            form_field = FileField(**field_args)
        elif field['type'] == 'date':
            form_field = DateField(**field_args)
        elif field['type'] == 'time':
            form_field = TimeField(**field_args)
        else:
            raise ValueError(f"Field type not supported: {field['type']}")

        # Add max min values for numerical inputs
        if field['type'] in ['number', 'float', 'decimal']:
            if 'min' in field:
                field_args['validators'].append(NumberRange(min=field['min']))
            if 'max' in field:
                field_args['validators'].append(NumberRange(max=field['max']))

        # Add the field into the form
        setattr(DynamicForm, field['name'], form_field)

    # Add the submit button
    setattr(DynamicForm, 'submit', SubmitField('Submit'))

    return DynamicForm

