# Manual User
First of all, when you run the client it appears and input where you must put the proxy of the main. If the proxy is correct it will appear the Iceflix interface where you can login as user, login as administrator and you can do an anonimous search. If you do a login as user it will request your username and the password and if it is correct it will show the user interface where you can do a search by name, search by tag, download a file. If you do a login as administrator and the admin token is correct it will show you the Administrator interface where you can add and remove user, rename media, remove and upload file. If you select anonimous search it will request the media name and it will show you the search if it exists with all the media id's. 
There are explanations that if you dont understand anything you can put help or ? to show information about the command. The option exit allows you to exit the application. 

# Template project for ssdd-lab

This repository is a Python project template.
It contains the following files and directories:

- `configs` has several configuration files examples.
- `iceflix` is the main Python package.
  You should rename it to something meaninful for your project.
- `iceflix/__init__.py` is an empty file needed by Python to
  recognise the `iceflix` directory as a Python module.
- `iceflix/cli.py` contains several functions to handle the basic console entry points
  defined in `python.cfg`.
  The name of the submodule and the functions can be modified if you need.
- `iceflix/iceflix.ice` contains the Slice interface definition for the lab.
- `iceflix/main.py` has a minimal implementation of a service,
  without the service servant itself.
  Can be used as template for main or the other services.
- `pyproject.toml` defines the build system used in the project.
- `run_client` should be a script that can be run directly from the
  repository root directory. It should be able to run the IceFlix
  client.
- `setup.cfg` is a Python distribution configuration file for Setuptools.
  It needs to be modified in order to adeccuate to the package name and
  console handler functions.
 
