import setuptools
from setuptools.command.develop import develop
from setuptools.command.install import install
#from install_tkdnd              import dnd_installed, dnd_install
from pathlib import Path

min_version = "2.9.2"

#def run_install():
#  version = dnd_installed()
#  if not version or version < min_version:
#    dnd_install()

class PreInstallCommand(install):
  """Post-installation for installation mode."""

  def run(self):
#    run_install()
    install.run(self) 

class PreDevelopCommand(develop):
  """Post-installation for development mode."""

  def run(self):
#    run_install()
    develop.run(self) 

with open("Readme.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  cmdclass={
    'install': PreInstallCommand,
    'develop': PreDevelopCommand
  },
  name='layoutx',
  entry_points={
    'console_scripts': [
      'lxdesigner = layoutx.tools.designer:main'
    ]
  },
  version='1.2',
  author='Pascal Maximilian Bremer',
  description="Declarative tkinter layout engine with reactive data binding",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/Bomberus/LayoutX",
  packages=setuptools.find_packages(include=['layoutx', 'layoutx.*']),
  include_package_data=True,
  test_suite="tests",
  install_requires=[
    "pypugjs",
    "rx"
  ],
  extras_require = {
    "more_widgets":  ["ttkwidgets", "pygments"],
    "styles": ["ttkthemes"]
  },
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development'
  ]
)