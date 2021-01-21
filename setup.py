from setuptools import setup

with open("README.md", "r") as fp:
    long_description = fp.read()

setup(
    name="evalo",
    version="0.2.0",
    description="Reverse evaluate values to Python code using constraint solving",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alexander Grooff",
    author_email="alexandergrooff@gmail.com",
    url="https://github.com/AlexanderGrooff/python-code-synthesis",
    packages=["evalo"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
