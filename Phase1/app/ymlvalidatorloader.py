import jsonschema
import yaml


class DictAsMember(dict):
    def __getattr__(self, name):
        value = self[name]
        if isinstance(value, dict):
            value = DictAsMember(value)
        if isinstance(value, list):
            newlist = []
            for i in value:
                if isinstance(i, dict):
                    newlist.append(DictAsMember(i))
                else:
                    newlist.append(i)
            return newlist
        return value

class YmlValidatorLoader(object):
    def __init__(self, schema_path, yml_file_path):
        with open(schema_path, 'r') as fp:
            self.__schema_object_raw = yaml.safe_load(fp)
            self.schema_object = DictAsMember(self.__schema_object_raw)
        with open(yml_file_path, 'r') as fp:
            self.__yml_file_object_raw = yaml.safe_load(fp)
            self.yml_file_object = DictAsMember(self.__yml_file_object_raw)

    def validate(self):
        jsonschema.validate(self.__yml_file_object_raw, self.__schema_object_raw)
