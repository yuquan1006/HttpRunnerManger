
from setuptools import setup,find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='httprunner',
    version='2.5.1',
    packages=find_packages(),
    url='git@git.ihr360.com:qa/HttpRunnerManger.git',
    license='MIT',
    author='york.yu',
    author_email='york.yu@ihr360.com',
    description='based on httprunner-version(2.5.1) for ihr360',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['requests','sentry-sdk', 'colorama', 'jsonschema', 'jinja2', 'har2case', 'filetype', 'pyyaml', 'requests', 'colorlog', 'requests-toolbelt', 'jsonpath','pytz'],
    package_data={'httprunner':['report/html/*.html'],'httprunner':['loader/schemas/*.json']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

