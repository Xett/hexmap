import setuptools
with open("README.md","r") as fh:
	long_description=fh.read()
setuptools.setup(
	name='hexmap',
	version='0.1',
	scripts=['bin/hexmap'],
	author='Xett',
	author_email='3954937+Xett@users.noreply.github.com',
	description='Hexmap storage and coordinates',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://github.com/Xett/hexmap.git',
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	]
)