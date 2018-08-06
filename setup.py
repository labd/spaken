from setuptools import find_packages, setup


with open('README.rst', 'r') as fh:
    description = '\n'.join(fh.readlines())


tests_require = [
    'moto==1.3.3',
    'pytest>=3.5.1',
    'pytest-cov>=2.5.1',
    'pytest-click',
]


setup(
    name='spaken',
    version='0.1.3',
    description=description,
    url='https://github.com/labd/spaken',
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    install_requires=[
        'boto3',
        'click>=6.7',
        'pip>=10.0',
        'packaging>=17.0',
    ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    package_dir={'': 'src'},
    packages=find_packages('src'),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': {
            'spaken = spaken.cmd:main'
        }
    },
    zip_safe=False,
)
