import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ilinfo-ajbmachon",
    version="0.2.0",
    author="Andre Machon",
    author_email="ajbmachon2@gmail.com",
    license='GNU GPLv3',
    description="Package for analyzing ILIAS installations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ajbmachon/ilinfo",
    packages=setuptools.find_packages(exclude=['tests*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['click', 'scandir', 'mysql-connector-python'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
)
