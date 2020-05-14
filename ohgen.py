#!/usr/bin/env python3
# A template based OpenHAB things and items definition generator
# https://github.com/jimtng/openhab-items-generator

import sys
import os
from jinja2 import Template
import re
import yaml

templates = {}
settings = {}
output_buffer = {}
base_path = ''

def warn(msg):
    print("# [WARNING] " + msg)

# load template from file into the templates dict if not already loaded
def load_template(template_name):
    global templates
    if template_name in templates:
        return

    things_template = ''
    items_template = ''

    things_nest_level = 0

    # Is the template file specified?
    try:
        template_file_name = settings['templates'][template_name]['template-file']
    except:
        template_file_name = 'templates/{}.tpl'.format(template_name)

    template_file_name = os.path.join(base_path, template_file_name)

    with open(template_file_name) as template_file:
        for line in template_file:
            line_stripped = line.strip()
            if line_stripped == '' or line_stripped.startswith('#'):
                continue
            
            if line_stripped.startswith("Thing ") or line_stripped.startswith("Bridge "):
                if things_template != '':
                    things_template += '\n'
                things_template += line
                if line_stripped.endswith('{'):
                    things_nest_level += 1
                continue
            
            if things_nest_level > 0:
                things_template += line
                if line_stripped.startswith('}'):
                    things_nest_level -= 1
                continue

            items_template += line

    templates[template_name] = { 'things': things_template, 'items': items_template } 


def camel_case_split(str):
    return " ".join(re.findall(r'[A-Z0-9](?:[a-z0-9]+|[A-Z]*(?=[A-Z]|$))', str))

def get_template_name(thing):
    return thing.get('template', settings.get('template'))

def generate(name, thing):
    template_name = get_template_name(thing)
    if not template_name:
        warn("{} has no template, and no default template has been specified".format(name))
        return

    try:
        load_template(template_name)
    except FileNotFoundError as err:
        warn("Error loading the template for '{}', template: '{}' {}".format(name, template_name, err))
        return

    generated = {}
    for part in [ 'things', 'items' ]:
        try:
            generated[part] = Template(templates[template_name][part]).render(thing)
        except:
            warn("Template error. Thing: '{}' Template: '{}' Error: {}".format(thing['name'], template_name, sys.exc_info()[1]))
            return None

    return generated

def get_output_file(output_name, section):
    return settings.get('outputs', {}).get(output_name, {}).get(section)

def add_thing_to_buffer(thing, things_data, items_data):
    global output_buffer
    template_name = get_template_name(thing)
    if not template_name: 
        return

    try:
        output_name = thing['output']
    except:
        try: 
            output_name = settings['templates'][template_name]['output']
        except:
            try:
                output_name = settings['output']
            except:
                warn("{}: No output name".format(thing['name']))
                return

    things_file = get_output_file(output_name, 'things-file')
    items_file = get_output_file(output_name, 'items-file')

    if not things_file:
        warn("{}: missing things-file output setting".format(thing['name']))
        return
    if not items_file:
        warn("{}: missing items-file output setting".format(thing['name']))
        return

    if output_name not in output_buffer:
        output_buffer[output_name] = {}
    output_buffer[output_name].setdefault('things-file', []).append(things_data)
    output_buffer[output_name].setdefault('items-file', []).append(items_data)

def save_output_buffer():
    # write output
    for output_name in output_buffer:
        for part in output_buffer[output_name]:
            file_name = get_output_file(output_name, part)
            file_name = os.path.join(base_path, file_name)
            headers = part + "-header"            
            footers = part + "-footer"
            status = "updated" if os.path.isfile(file_name) else "created"
            with open(file_name, 'w') as file:
                # write global headers
                if 'header' in settings:
                    file.write(settings['header'])

                # write output specific headers
                if headers in settings['outputs'][output_name]:
                    file.write(settings['outputs'][output_name][headers])

                # write the generated content
                file.write("\n\n".join(output_buffer[output_name][part]))
                
                # write output specific footers
                if footers in settings['outputs'][output_name]:
                    file.write(settings['outputs'][output_name][footers])

                # write global footers
                if 'footer' in settings:
                    file.write(settings['footer'])

            print("{} - {}".format(file_name, status))

def main():
    global settings
    things_file_name = sys.argv[1] if len(sys.argv) > 1 else "devices.yaml"
    base_path = os.path.dirname(things_file_name)
    try:
        with open(things_file_name) as f:
            data = yaml.load(f.read(), Loader=yaml.BaseLoader)
    except:
        warn("{}".format(sys.exc_info()[1]))
        sys.exit()

    if not data:
        warn("No data found in {}".format(things_file_name))       
        sys.exit()

    settings = data.pop('settings', {})

    # load all the yaml data first and generate each thing
    for name, thing in data.items():
        thing.setdefault('name', name)
        # fill in some useful variables
        thing.setdefault('label', camel_case_split(name.replace("_", " ")))
        thing.setdefault('thingid', name.replace("_", "-").lower())
        thing.setdefault('name_parts', name.split("_"))
        thing.setdefault('room', camel_case_split(name.split("_")[0]))

        output = generate(name, thing)
        if output:
            add_thing_to_buffer(thing, output['things'], output['items'])

    save_output_buffer()

if __name__ == '__main__':
    main()