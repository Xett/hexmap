import setuptools

with open("README.md", "r") as fh:
    long_description=fh.read()

setuptools.setup(
    name='hexmap',
    version='0.1',
    scripts=['bin/hexmap'],
    author='Xet',
    author_email='ethan.jones@my.jcu.edu.au',
    description='Hexmap storage and coordinate system',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xett/Hexmap",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
        "Operating System :: OS Independent",
    ]
)
