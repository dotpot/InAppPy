# encoding: UTF-8
from setuptools import setup


def get_description():
    with open("README.rst") as info:
        return info.read()


setup(
    name="inapppy",
    version="2.5.2",
    packages=["inapppy", "inapppy.asyncio"],
    install_requires=["aiohttp", "rsa", "requests", "google-api-python-client", "oauth2client"],
    description="In-app purchase validation library for Apple AppStore and GooglePlay.",
    keywords="in-app store purchase googleplay appstore validation",
    author="Lukas Šalkauskas",
    author_email="halfas.online@gmail.com",
    url="https://github.com/dotpot/InAppPy",
    long_description=get_description(),
    license="MIT",
)
