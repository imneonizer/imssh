from setuptools import setup, Extension
from setuptools import find_packages

with open("Readme.md") as f:
    long_description = f.read()

if __name__ == "__main__":
    setup(
        name="imssh",
        scripts=["scripts/imssh"],
        version="0.0.1",
        description="A paramiko based, ssh automation tool.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Nitin Rai",
        author_email="mneonizer@gmail.com",
        url="https://github.com/imneonizer/imssh",
        license="MIT License",
        packages=find_packages(),
        include_package_data=True,
        install_requires=["paramiko>=2.7.2"],
        platforms=["linux", "unix"],
        python_requires=">3.5.2",
    )