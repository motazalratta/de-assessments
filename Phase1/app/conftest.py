import pytest
import os

TEMP_ENV_VARS = {
    'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/your/key/file',
    'GOOGLE_CLOUD_PROJECT': '<project_id>',
}

@pytest.fixture(scope="function")
def tests_setup_and_teardown():
    # Will be executed function
    old_environ = dict(os.environ)
    os.environ.update(TEMP_ENV_VARS)

    yield
    # Will be executed after function
    os.environ.clear()
    os.environ.update(old_environ)

