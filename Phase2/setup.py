import setuptools

REQUIRED_PACKAGES = [
    'pandas==1.1.*',
    'python-dateutil==2.8.1',
    'flat-table==1.1.1'
]

PACKAGE_NAME = 'pubsub_to_bigquery'
PACKAGE_VERSION = '1.0.0'

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
)
