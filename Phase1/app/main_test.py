import pytest
import yaml
import subprocess
import tempfile
import os

command_template = "{} --schema {} --ymlfile {}"
scrip_name = "python3 main.py"
valid_schema_path = 'configschema.json'
yml_test_file = 'config{}config.yml'.format(os.path.sep)
default_timeout=10
with open(yml_test_file, 'r') as fp:
    yml_fileE_example = yaml.safe_load(fp)

def test_not_required_args_provided(tests_setup_and_teardown):
    command = scrip_name
    exitcode = subprocess.run(list(command.split(" ")), timeout=default_timeout)
    assert exitcode.returncode == 2


def test_env_variable_not_set():
    command = command_template.format(scrip_name, valid_schema_path, yml_test_file)
    exitcode = subprocess.run(list(command.split(" ")), timeout=default_timeout)
    assert exitcode.returncode == 3


def test_input_file_path_invalid(tests_setup_and_teardown):
    command = command_template.format(scrip_name, valid_schema_path, "PathNotFound")
    exitcode = subprocess.run(list(command.split(" ")), timeout=default_timeout)
    assert exitcode.returncode == 4


def test_invalid_input_file_missing_archive_dir(tests_setup_and_teardown):
    wong_file_content = yml_fileE_example.copy()
    del wong_file_content['archive_files_dir']
    with tempfile.NamedTemporaryFile(mode='w') as tmp:
        yaml.dump(wong_file_content, tmp)
        command = command_template.format(scrip_name, valid_schema_path, tmp.name)
        exitcode = subprocess.run(list(command.split(" ")), timeout=default_timeout)
        assert exitcode.returncode == 5


def test_invalid_input_file_missing_raw_dir(tests_setup_and_teardown):
    wong_file_content = yml_fileE_example.copy()
    del wong_file_content['raw_files_dir']
    with tempfile.NamedTemporaryFile(mode='w') as tmp:
        yaml.dump(wong_file_content, tmp)
        command = command_template.format(scrip_name, valid_schema_path, tmp.name)
        exitcode = subprocess.run(list(command.split(" ")), timeout=default_timeout)
        assert exitcode.returncode == 5


def test_valid_input_file_with_unfound_pathes(tests_setup_and_teardown):
    wong_file_content = yml_fileE_example.copy()
    wong_file_content['raw_files_dir'] = "/hello"
    with tempfile.NamedTemporaryFile(mode='w') as tmp:
        yaml.dump(wong_file_content, tmp)
        command = command_template.format(scrip_name, valid_schema_path, tmp.name)
        exitcode = subprocess.run(list(command.split(" ")), timeout=default_timeout)
        assert exitcode.returncode == 6


def test_valid_input_file_with_valid_config(tests_setup_and_teardown):
    valid_yml_file = yml_fileE_example.copy()
    with tempfile.NamedTemporaryFile(mode='w') as tmp:
        yaml.dump(valid_yml_file, tmp)
        with pytest.raises(subprocess.TimeoutExpired):
            command = command_template.format(scrip_name, valid_schema_path, tmp.name)
            subprocess.run(list(command.split(" ")), timeout=default_timeout)
