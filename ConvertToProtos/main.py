import json
import os
from google.protobuf.json_format import MessageToDict
from descriptor_pb2 import FileDescriptorProto

gamepath = r'C:\Users\hiro\Documents\Grasscutter\proto_descriptors'

def fieldtype_to_protofieldtype(fieldtype):
    fieldtype_map = {
        "TYPE_DOUBLE": "double",
        "TYPE_FLOAT": "float",
        "TYPE_INT64": "int64",
        "TYPE_UINT64": "uint64",
        "TYPE_INT32": "int32",
        "TYPE_FIXED64": "fixed64",
        "TYPE_FIXED32": "fixed32",
        "TYPE_BOOL": "bool",
        "TYPE_STRING": "string",
        "TYPE_GROUP": "group",
        "TYPE_MESSAGE": "message",
        "TYPE_BYTES": "bytes",
        "TYPE_UINT32": "uint32",
        "TYPE_ENUM": "enum",
        "TYPE_SFIXED32": "sfixed32",
        "TYPE_SFIXED64": "sfixed64",
        "TYPE_SINT32": "sint32",
        "TYPE_SINT64": "sint64",
    }
    
    fieldtype = fieldtype.replace(".proto.", "")
    if (fieldtype.startswith(".")):
        fieldtype = fieldtype[1:]
    return fieldtype_map.get(fieldtype, fieldtype)

def do_message(messagetype, writer, indent=0):
    name = messagetype['name']
    writer.write(f'{"    " * indent}message {name} {{\n')
    
    oneof_groups = {}
    regular_fields = []

    if 'field' in messagetype:
        for field in messagetype['field']:
            oneof_index = field.get('oneofIndex')
            if oneof_index is not None:
                if oneof_index not in oneof_groups:
                    oneof_groups[oneof_index] = []
                oneof_groups[oneof_index].append(field)
            else:
                regular_fields.append(field)

    if 'enumType' in messagetype:
        for field in messagetype['enumType']:
            name = field['name']
            writer.write(f'{"    " * (indent + 1)}enum {name} {{\n')
            for value in field['value']:
                writer.write(f'{"    " * (indent + 2)}{value["name"]} = {value["number"]};\n')
            writer.write(f'{"    " * (indent + 1)}}}\n')

    for field in regular_fields:
        map_entry = False
        if 'typeName' in field and 'nestedType' in messagetype:
            for nested in messagetype['nestedType']:
                if nested.get('name') == field['typeName'].split('.')[-1] and nested.get('options', {}).get('mapEntry', False):
                    key_field = next((f for f in nested['field'] if f['name'] == 'key'), None)
                    value_field = next((f for f in nested['field'] if f['name'] == 'value'), None)
                    
                    if key_field and value_field:
                        key_type = fieldtype_to_protofieldtype(key_field['type'])
                        value_type = fieldtype_to_protofieldtype(value_field['type'])
                        writer.write(f'{"    " * (indent + 1)}map<{key_type}, {value_type}> {field["name"]} = {field["number"]};\n')
                        map_entry = True
                    break
        
        if map_entry:
            continue
        
        fieldtype = field['type']
        if fieldtype == 'TYPE_MESSAGE' and 'typeName' in field:
            fieldtype = field['typeName']
        if fieldtype == 'TYPE_ENUM' and 'typeName' in field:
            fieldtype = field['typeName']
        label = field['label']
        if label == 'LABEL_REPEATED':
            writer.write(f'{"    " * (indent + 1)}repeated {fieldtype_to_protofieldtype(fieldtype)} {field["name"]} = {field["number"]};\n')
        else:
            writer.write(f'{"    " * (indent + 1)}{fieldtype_to_protofieldtype(fieldtype)} {field["name"]} = {field["number"]};\n')

    for index, fields in oneof_groups.items():
        oneof_name = messagetype['oneofDecl'][index]['name']
        writer.write(f'{"    " * (indent + 1)}oneof {oneof_name} {{\n')
        for field in fields:
            map_entry = False
            if 'typeName' in field and 'nestedType' in messagetype:
                for nested in messagetype['nestedType']:
                    if nested.get('name') == field['typeName'].split('.')[-1] and nested.get('options', {}).get('mapEntry', False):
                        key_field = next((f for f in nested['field'] if f['name'] == 'key'), None)
                        value_field = next((f for f in nested['field'] if f['name'] == 'value'), None)
                        
                        if key_field and value_field:
                            key_type = fieldtype_to_protofieldtype(key_field['type'])
                            value_type = fieldtype_to_protofieldtype(value_field['type'])
                            writer.write(f'{"    " * (indent + 2)}map<{key_type}, {value_type}> {field["name"]} = {field["number"]};\n')
                            map_entry = True
                        break
            
            if map_entry:
                continue
            
            fieldtype = field['type']
            if fieldtype == 'TYPE_MESSAGE' and 'typeName' in field:
                fieldtype = field['typeName']
            if fieldtype == 'TYPE_ENUM' and 'typeName' in field:
                fieldtype = field['typeName']
            label = field['label']
            if label == 'LABEL_REPEATED':
                writer.write(f'{"    " * (indent + 2)}repeated {fieldtype_to_protofieldtype(fieldtype)} {field["name"]} = {field["number"]};\n')
            else:
                writer.write(f'{"    " * (indent + 2)}{fieldtype_to_protofieldtype(fieldtype)} {field["name"]} = {field["number"]};\n')
        writer.write(f'{"    " * (indent + 1)}}}\n')

    if 'nestedType' in messagetype:
        for nested in messagetype['nestedType']:
            if not nested.get('options', {}).get('mapEntry', False):
                do_message(nested, writer, indent + 1)
    
    writer.write(f'{"    " * indent}}}\n\n')

for file in os.listdir(gamepath):
    with open(os.path.join(gamepath, file), 'rb') as f:
        data = f.read()
        proto = FileDescriptorProto()
        proto.ParseFromString(data)
        proto_dict = MessageToDict(proto)
        defs = json.loads(json.dumps(proto_dict, indent=2))

        filename = defs['name']
        if not os.path.exists("output"):
            os.makedirs("output")
        writer = open(os.path.join("output", filename), 'w')
        syntax = defs['syntax']
        package = defs['package'] if 'package' in defs else ''
        dependencies = defs.get('dependency', [])
        writer.write(f'syntax = "{syntax}";\n\n')
        options = defs.get('options', {})
        if options.get('javaPackage', '') != '':
            writer.write(f'option java_package = "{options["javaPackage"]}";\n\n')
        if package != '':
            writer.write(f'package {package};\n\n')


        dependencies = defs.get('dependency', [])
        if dependencies.__len__() > 0:
            for dependency in dependencies:
                filepath_parts = filename.split('.')
                dependency = dependency.replace('.', '/', dependency.count('.') - 1)
                writer.write(f'import "{dependency}";\n')
            writer.write('\n')

        filename = defs['name']
        if 'messageType' in defs:
            messagetypes = defs['messageType']
            for messagetype in messagetypes:
                do_message(messagetype, writer)

        if 'enumType' in defs:
            for enumtype in defs['enumType']:
                name = enumtype['name']
                writer.write(f'enum {name} {{\n')
                for value in enumtype['value']:
                    writer.write(f'    {value["name"]} = {value["number"]};\n')
                writer.write('}\n\n')

        writer.close()