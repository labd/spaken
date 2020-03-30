import re
from setuptools import find_packages, setup


with open("README.md") as fh:
    long_description = re.sub(
        "<!-- start-no-pypi -->.*<!-- end-no-pypi -->\n",
        "",
        fh.read(),
        flags=re.M | re.S,
    )


tests_require = [
    "coverage[toml]",
    "moto>=1.3.4",
    "pretend",
    "pytest>=3.5.1",
    "pytest-cov>=2.5.1",
    "pytest-click",
]


setup(
    name="spaken",
    version="0.2.1",
    description="Optimize Pip installs for CI/CD pipelines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/labd/spaken",
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    install_requires=["boto3>=1.7.84", "click>=6.7", "pip>=10.0", "packaging>=17.0",],
    tests_require=tests_require,
    extras_require={"test": tests_require},
    package_dir={"": "src"},
    packages=find_packages("src"),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"console_scripts": {"spaken = spaken.cmd:main"}},
    zip_safe=False,
)
