import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()

setuptools.setup(
    name="django-eb-sqs-worker", # Replace with your own username
    version="0.4.0",
    author="Alexey Strelkov",
    author_email="datagreed@gmail.com",
    description="Django Background Tasks for Amazon Elastic Beanstalk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DataGreed/django-eb-sqs-worker/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
)