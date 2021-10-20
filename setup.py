from setuptools import setup
import sdist_upip

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("VERSION", encoding="utf-8") as f:
    version = f.read()


setup(
    cmdclass={"sdist": sdist_upip.sdist},
    name="micropython-uAPI",
    packages=["uAPI"],
    version=version,
    description="A very lightweight API framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheGarkine/uAPI",
    author="Raphael Krauthann",
    author_email="krauthann1@googlemail.com",
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        #'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="micropython api web embedded",
)
