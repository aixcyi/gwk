from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='gwk',
    description='Genshin Wish Kit',
    version='1.0.0',
    license='MIT',
    author='aixcyi',
    author_email='aixcyi@simple.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    packages=["gwk"],
    python_requires=">=3.6.2",
    install_requires=[
        "requests~=2.12.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
