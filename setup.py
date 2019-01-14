# encoding: UTF-8
from setuptools import setup


setup(
    name="inapppy",
    version="2.2",
    packages=["inapppy", "inapppy.asyncio"],
    install_requires=[
        "aiohttp",
        "rsa",
        "requests",
        "google-api-python-client",
        "oauth2client==3.0.0",
    ],
    description="In-app purchase validation library for Apple AppStore and GooglePlay.",
    keywords="in-app store purchase googleplay appstore validation",
    author="Lukas Šalkauskas",
    author_email="halfas.online@gmail.com",
    url="https://github.com/dotpot/InAppPy",
    long_description=open("README.rst").read(),
    license="MIT",
)
