import chuckjokes

from setuptools import setup

packages = ["chuckjokes"]

install_requires = [
        "appdirs",
        "click",
        "prettytable",
        "requests"
        ]

setup(
        name="chuckjokes",
        version=chuckjokes.__version__,
        packages=packages,
        include_package_data=True,
        intall_requires=install_requires,
        entry_points="""
            [console_scripts]
            chuckjokes=chuckjokes.cli:cli
        """
        )
