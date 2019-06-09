import json
import logging
import os
from pathlib import Path
import typing

import inflection


log_level = getattr(logging, os.environ.get('LOG_LEVEL', 'info').upper())
logging.basicConfig(level=log_level)
logger = logging.getLogger('generate')

init_header = '''\'\'\'
DO NOT EDIT THIS FILE

This file is generated from the CDP definitions. If you need to make changes,
edit the generator and regenerate all of the modules.
\'\'\'
'''

module_header = '''\'\'\'
DO NOT EDIT THIS FILE

This file is generated from the CDP definitions. If you need to make changes,
edit the generator and regenerate all of the modules.

Domain: {}
Experimental: {}
\'\'\'

from dataclasses import dataclass, field
import typing

'''


def parse(json_path, output_path):
    '''
    Parse JSON protocol description and generate module files.

    :param Path json_path: path to a JSON CDP schema
    :param Path output_path: a directory path to create the modules in
    :returns: a list of 2-tuples containing (module name, list of exported
        symbols)
    '''
    with json_path.open() as json_file:
        schema = json.load(json_file)
    version = schema['version']
    assert (version['major'], version['minor']) == ('1', '3')
    modules = list()
    for domain in schema['domains']:
        modules.append(
            generate_domain_module(domain, output_path))
    return modules


def generate_domain_module(domain, output_path):
    '''
    Generate a Python module for a given CDP domain.

    :param dict domain: domain schema
    :param Path output_path: a directory path to create the module in
    :returns: module name and a list of exported names
    '''
    name = domain['domain']
    module_name = inflection.underscore(name)
    logger.info('Generating module: %s → %s.py', name, module_name)
    experimental = domain.get('experimental', False)

    # The dependencies listed in the JSON don't match the actual dependencies
    # encountered when building the types. So we ignore the declared
    # dependencies and compute it ourself.
    type_dependencies = set()
    domain_types = domain.get('types', list())
    for type_ in domain_types:
        for prop in type_.get('properties', list()):
            dependency = get_dependency(prop)
            if dependency:
                type_dependencies.add(dependency)
    if type_dependencies:
        logger.debug('Computed type_dependencies: %s', ','.join(
            type_dependencies))

    event_dependencies = set()
    domain_events = domain.get('events', list())
    for event in domain_events:
        for param in event.get('parameters', list()):
            dependency = get_dependency(param)
            if dependency:
                event_dependencies.add(dependency)
    if event_dependencies:
        logger.debug('Computed event_dependencies: %s', ','.join(
            event_dependencies))

    command_dependencies = set()
    domain_commands = domain.get('commands', list())
    for command in domain_commands:
        for param in command.get('parameters', list()):
            dependency = get_dependency(param)
            if dependency:
                command_dependencies.add(dependency)
        for return_ in command.get('returns', list()):
            dependency = get_dependency(return_)
            if dependency:
                command_dependencies.add(dependency)
    if command_dependencies:
        logger.debug('Computed command_dependencies: %s', ','.join(
            command_dependencies))

    # Generate code for this module.
    module_path = output_path / module_name
    module_path.mkdir(parents=True, exist_ok=True)
    init_path = module_path / '__init__.py'
    init_path.touch()

    types_path = module_path / 'types.py'
    with types_path.open('w') as types_file:
        types_file.write(module_header.format(module_name, experimental))
        for dependency in sorted(type_dependencies):
            types_file.write(import_dependency(dependency))
        if type_dependencies:
            types_file.write('\n')
        type_exports, type_code = generate_types(domain_types)
        types_file.write(type_code)

    events_path = module_path / 'events.py'
    with events_path.open('w') as events_file:
        events_file.write(module_header.format(module_name, experimental))
        events_file.write('from .types import *\n')
        for dependency in sorted(event_dependencies):
            events_file.write(import_dependency(dependency))
        if event_dependencies:
            events_file.write('\n')
        event_exports, event_code = generate_events(domain_events)
        events_file.write(event_code)

    commands_path = module_path / 'commands.py'
    with commands_path.open('w') as commands_file:
        commands_file.write(module_header.format(module_name, experimental))
        commands_file.write('from .types import *\n')
        for dependency in sorted(command_dependencies):
            commands_file.write(import_dependency(dependency))
        if command_dependencies:
            commands_file.write('\n')
        command_exports, command_code = generate_commands(name, domain_commands)
        commands_file.write(command_code)

    return module_name, type_exports, event_exports, command_exports


def get_dependency(cdp_meta):
    if 'type' in cdp_meta and cdp_meta['type'] != 'array':
        return None

    if 'items' in cdp_meta and 'type' in cdp_meta['items']:
        return None

    if '$ref' in cdp_meta:
        type_ = cdp_meta['$ref']
    elif 'items' in cdp_meta and '$ref' in cdp_meta['items']:
        type_ = cdp_meta['items']['$ref']
    else:
        raise Exception('Cannot get dependency: {!r}'.format(cdp_meta))

    try:
        dependency, _ = type_.split('.')
        return dependency
    except ValueError:
        # Not a dependency on another module.
        return None


def import_dependency(dependency):
    module_name = inflection.underscore(dependency)
    return 'from ..{} import types as {}\n'.format(module_name, module_name)


def generate_types(types):
    '''
    Generate type definitions as Python code.

    :param list types: a list of CDP type definitions
    :returns: a tuple (list of types, code as string)
    '''
    code = '\n'
    exports = list()
    classes = list()
    emitted_types = set()
    for type_ in types:
        cdp_type = type_['type']
        type_name = type_['id']
        exports.append(type_name)
        description = type_.get('description')
        logger.debug('Generating type %s: %s', type_name, cdp_type)
        if 'enum' in type_:
            code += generate_enum_type(type_)
            emitted_types.add(type_name)
        elif cdp_type == 'object':
            classes.append(generate_class_type(type_))
        else:
            code += generate_basic_type(type_)
            emitted_types.add(type_name)

    # The classes have dependencies on each other, so we have to emit them in
    # a specific order. If we can't resolve these dependencies after a certain
    # number of iterations, it suggests a cyclical dependency that this code
    # cannot handle.
    tries_remaining = 1000
    while classes:
        class_ = classes.pop(0)
        if not class_['children']:
            code += class_['code']
            emitted_types.add(class_['name'])
            continue
        if all(child in emitted_types for child in class_['children']):
            code += class_['code']
            emitted_types.add(class_['name'])
            continue
        classes.append(class_)
        tries_remaining -= 1
        if not tries_remaining:
            logger.error('Class resolution failed. Emitted these types: %s',
                emitted_types)
            logger.error('Class resolution failed. Cannot emit these types: %s',
                json.dumps(classes, indent=2))
            raise Exception('Failed to resolve class dependencies.'
                ' See output above.')

    return exports, code


def inline_doc(description, indent=0):
    '''
    Generate an inline doc, e.g. ``#: This type is a ...``

    :param str description:
    :returns: a string
    '''
    if not description:
        return ''

    i = ' ' * indent
    lines = ['{}#: {}\n'.format(i, l) for l in description.split('\n')]
    return ''.join(lines)


def docstring(description, indent=4):
    '''
    Generate a docstring from a description.

    :param str description:
    :param int indent: the number of spaces to indent the docstring
    '''
    if not description:
        return ''

    i = ' ' * indent
    start_stop = "{}'''".format(i)
    lines = [start_stop]
    for line in description.split('\n'):
        lines.append('{}{}'.format(i, line))
    lines.append(start_stop)
    return '\n'.join(lines) + '\n'


def generate_enum_type(type_):
    '''
    Generate an "enum" type.

    Enums are handled by making a python class that contains only class members.
    Each class member is upper snaked case, e.g. ``MyTypeClass.MY_ENUM_VALUE``
    and is assigned a string value from the CDP metadata.

    :param dict type_: CDP type metadata
    '''
    code = ''
    if type_['type'] != 'string':
        raise Exception('Unexpected enum type: {!r}'.format(type_))
    code += '\nclass {}:\n'.format(type_['id'])
    description = type_.get('description')
    code += docstring(description)
    for enum_member in type_['enum']:
        snake_case = inflection.underscore(enum_member).upper()
        code += '    {} = "{}"\n'.format(snake_case, enum_member)
    code += '\n'
    return code


def get_python_type(cdp_meta):
    '''
    Generate a name for the Python type that corresponds to the the given CDP
    type.

    :param dict cdp_meta: CDP metadata for a type or property
    :returns: Python type as a string
    '''
    if 'type' in cdp_meta:
        cdp_type = cdp_meta['type']
        if cdp_type == 'array':
            py_type = 'typing.List'
            try:
                cdp_nested_type = cdp_meta['items']['$ref']
                py_type += "['{}']".format(cdp_nested_type)
            except KeyError:
                # No nested type: ignore.
                pass
        else:
            py_type = {
                'any': 'typing.Any',
                'boolean': 'bool',
                'integer': 'int',
                'object': 'dict',
                'number': 'float',
                'string': 'str',
            }[cdp_type]
        return py_type

    if '$ref' in cdp_meta:
        prop_type = cdp_meta['$ref']
        if '.' in prop_type:
            # If the type lives in another module, then we need to
            # snake_case the module name and it should *not* be added to the
            # list of child classes that is used for dependency resolution.
            other_module, other_type = prop_type.split('.')
            prop_type = '{}.{}'.format(inflection.underscore(other_module),
                other_type)
        return prop_type

    raise Exception('Cannot get python type from CDP metadata: {!r}'.format(
        cdp_meta))



def generate_class_type(type_):
    '''
    Generate a class type.

    Top-level types that are defined as a CDP ``object`` are turned into Python
    dataclasses.

    :param dict type_: CDP type metadata
    '''
    description = type_.get('description')
    type_name = type_['id']
    children = set()
    class_code = '\n@dataclass\n'
    class_code += 'class {}:\n'.format(type_name)
    class_code += docstring(description)
    constructor = list()
    for prop in type_.get('properties', []):
        prop_name = prop['name']
        snake_name = inflection.underscore(prop_name)
        if snake_name == 'type':
            snake_name = 'type_'
        prop_description = prop.get('description')
        if prop_description:
            class_code += inline_doc(prop_description, indent=4)
        prop_type = get_python_type(prop)
        if prop_type == type_name:
            # If a type refers to itself, e.g. StackTrace has a member
            # called ``parent`` that is itself a StackTrace, then the type
            # name must be quoted or else Python will not be able to compile
            # the module.
            prop_type = "'{}'".format(prop_type)
        elif '$ref' in prop and '.' not in prop_type:
            # If the type lives in this module and is not a type that refers
            # to itself, then add it to the set of children so that
            # inter-class dependencies can be resolved later on.
            children.add(prop_type)
        class_code += '    {}: {}\n\n'.format(snake_name, prop_type)
        if 'type' in prop:
            if prop['type'] != 'array':
                constructor.append("{}={}(response.get('{}'))".format(snake_name,
                    prop_type, prop_name))
            elif '$ref' in prop['items']:
                subtype = get_python_type(prop['items'])
                constructor.append("{}=[{}.from_response(i) for i in response.get('{}')]".format(
                    snake_name, subtype, prop_name))
            elif 'type' in prop['items']:
                subtype = get_python_type(prop['items'])
                constructor.append("{}=[{}(i) for i in response.get('{}')]".format(
                    snake_name, subtype, prop_name))
        else:
            constructor.append("{}={}.from_response(response.get('{}'))".format(
                snake_name, prop_type, prop_name))

    class_code += '    @classmethod\n'
    class_code += '    def from_response(cls, response):\n'
    class_code += '        return cls(\n'
    class_code += ''.join('            {},\n'.format(l) for l in constructor)
    class_code += '        )\n'
    class_code += '\n'

    return {
        'name': type_name,
        'code': class_code,
        # Don't emit children that live in a different module. We assume that
        # modules do not have cyclical dependencies on each other.
        'children': [c for c in children if '.' not in c],
    }


def generate_basic_type(type_):
    '''
    Generate one of the "basic" types, i.e. type aliases for Python built-ins.

    :param dict type_: CDP type metadata
    '''
    code = ''
    cdp_type = type_['id']
    py_type = get_python_type(type_)
    description = type_.get('description')
    code += 'class {}({}):\n'.format(cdp_type, py_type)
    code += docstring(description)
    code += '    @classmethod\n'
    code += '    def from_response(cls, response):\n'
    code += '        return cls(response)\n'
    code += '\n'
    code += '    def __repr__(self):\n'
    code += "        return '{}({{}})'.format({}.__repr__(self))\n".format(
        cdp_type, py_type)
    code += '\n\n'
    return code


def generate_events(events):
    exports = list()
    code = '\n'
    for event in events:
        event_name = inflection.camelize(event['name'],
            uppercase_first_letter=True)
        parameters = event.get('parameters', list())
        code += '\n@dataclass\n'
        code += 'class {}:\n'.format(event_name)
        description = event.get('description')
        code += docstring(description)
        if parameters:
            for parameter in parameters:
                param_name = inflection.underscore(parameter['name'])
                param_description = parameter.get('description')
                code += inline_doc(description, indent=4)
                if 'type' in parameter:
                    param_type = get_python_type(parameter)
                elif '$ref' in parameter:
                    param_type = parameter['$ref']
                    if '.' in param_type:
                        # If the type lives in another module, then we need to
                        # snake_case the module name and it should *not* be
                        # added to the list of child classes that is used for
                        # dependency resolution.
                        other_module, other_type = param_type.split('.')
                        param_type = '{}.{}'.format(
                            inflection.underscore(other_module), other_type)
                else:
                    raise Exception('Cannot determing event parameter type:'
                        ' {!r}'.format(parameter))
                code += '    {}: {}\n\n'.format(param_name, param_type)
        else:
            code += '    pass\n\n'
        exports.append(event_name)
    return exports, code


def generate_commands(domain_name, commands):
    '''
    Generate command definitions as Python code.

    :param str domain_name: the CDP domain name
    :param list commands: a list of CDP command definitions
    :returns: a tuple (list of exported types, code as string)
    '''
    code = '\n\n'
    code += 'class {}:\n'.format(domain_name)
    for command in commands:
        command_name = command['name']
        method_name = inflection.underscore(command_name)
        description = command.get('description', '')
        code += '    @staticmethod\n'
        arg_list = list()
        dict_items = list()
        params = command.get('parameters', list())
        if params:
            description += '\n'
        for param in params:
            param_name = param['name']
            snake_name = inflection.underscore(param_name)
            param_type = get_python_type(param)
            arg_list.append('{}: {}'.format(snake_name, param_type))
            description += '\n:param {}: {}'.format(snake_name,
                param.get('description', ''))
            dict_items.append((snake_name, param_name))
        returns = command.get('returns', list())
        if len(returns) == 0:
            return_type = 'None'
        elif len(returns) == 1:
            return_type = get_python_type(returns[0])
            description += '\n:returns: {}'.format(
                returns[0].get('description', ''))
        else:
            return_type = 'dict'
            description += '\n:returns: a dict with the following keys:'
            for return_ in returns:
                description += '\n    * {}: {}'.format(return_['name'],
                    return_.get('description', ''))
        code += '    def {}({}) -> {}:\n'.format(method_name,
            ', '.join(arg_list), return_type)
        code += docstring(description, indent=8)
        code += '\n'
        code += '        cmd_dict = {\n'
        code += "            'method': '{}.{}',\n".format(domain_name,
            command_name)
        if dict_items:
            code += "            'params': {\n"
            for snake_name, param_name in dict_items:
                code += "                '{}': {},\n".format(param_name,
                    snake_name)
            code += '            }\n'
        code += '        }\n'
        code += '        response = yield cmd_dict\n'
        if len(returns) == 1:
            return_ = returns[0]
            return_type = get_python_type(return_)
            code += '        return {}\n'.format(make_return_code(return_))
        elif len(returns) > 1:
            # we should be able to refactor the first part of this if block to have something
            # reusable, then we call that new thing inside of a loop in this elif block
            # the only difference here is printing key names and dict syntax
            code += '        return {\n'
            for return_ in returns:
                return_type = get_python_type(return_)
                return_name = return_['name']
                code += "                '{}': {},\n".format(return_name,
                    make_return_code(return_))
            code += '            }\n'
        code += '\n'
    return [domain_name], code


def make_return_code(return_):
    '''
    Make a snippet of code that retuns a value inside of a ``def parse_response()``.

    :param dict return_: the CDP metadata for the item to return
    :returns: a string
    '''
    return_name = return_['name']
    return_type = get_python_type(return_)
    if 'typing.List' in return_type:
        subtype = get_python_type(return_['items'])
        if 'type' in return_['items']:
            code = "[{}(i) for i in response['{}']]".format(subtype, return_name)
        else:
            code = "[{}.from_response(i) for i in response['{}']]".format(subtype, return_name)
    else:
        code = "{}.from_response(response['{}'])".format(return_type, return_name)
    return code


def generate_init(init_path, modules):
    '''
    Generate an ``__init__.py`` that exports the specified modules.

    :param Path init_path: a file path to create the init file in
    :param list[tuple] modules: a list of modules each represented as tuples
        of (name, list_of_exported_symbols)
    '''
    modules.sort()
    with init_path.open('w') as init_file:
        init_file.write(init_header)
        for module, type_exports, _, _ in modules:
            if type_exports:
                init_file.write('from .{}.types import (\n'.format(module))
                for export in type_exports:
                    init_file.write('    {},\n'.format(export))
                init_file.write(')\n')
        for module, _, event_exports, _ in modules:
            if event_exports:
                init_file.write('from .{}.events import (\n'.format(module))
                for export in event_exports:
                    init_file.write('    {},\n'.format(export))
                init_file.write(')\n')
        for module, _, _, command_exports in modules:
            if command_exports:
                init_file.write('from .{}.commands import (\n'.format(module))
                for export in command_exports:
                    init_file.write('    {},\n'.format(export))
                init_file.write(')\n')

def main():
    ''' Main entry point. '''
    here = Path(__file__).parent.resolve()
    json_paths = [
        here / 'browser_protocol.json',
        here / 'js_protocol.json',
    ]
    output_path = here.parent / 'cdp'
    init_path = output_path / '__init__.py'

    modules = list()
    for json_path in json_paths:
        logger.info('Parsing JSON file %s', json_path)
        modules.extend(parse(json_path, output_path))

    generate_init(init_path, modules)


if __name__ == '__main__':
    main()
