from gettext import find
import setuptools

def read_requirements():
    with open("requirements.txt") as req:
        content = req.read()
        requirements = content.split("\n")
    return requirements

setuptools.setup(
    name = "looknice",
    version = "0.1",
    packages =  setuptools.find_packages(),
    include_package_data = True,
    install_requires = read_requirements(),
    entry_points = """
        [console_scripts]
        my_test = looknice.cli:my_test
        looknice = looknice.cli:cli
    """
)