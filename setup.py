"""Setup for paje-data package."""
import setuptools

import pjdata

NAME = "pjdata"

VERSION = pjdata.__version__

AUTHOR = 'Davi Pereira dos Santos and Edesio Alcobaça'


AUTHOR_EMAIL = ''


DESCRIPTION = 'Package for Data and related classes for data science (Pajé, Oka, ...)'


with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()


LICENSE = 'GPL3'


URL = 'https://github.com/automated-data-science/paje-data'


DOWNLOAD_URL = 'https://github.com/automated-data-science/paje-data/releases'


CLASSIFIERS = ['Intended Audience :: Science/Research',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
               'Natural Language :: English',
               'Programming Language :: Python',
               'Topic :: Software Development',
               'Topic :: Scientific/Engineering',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7']


INSTALL_REQUIRES = [
    'liac-arff', 'pandas', 'sklearn', 'pycryptodome', 'sortedcontainers',
    'compose', 'lz4', 'zstandard', "Pillow", 'numpy'  # needed by mypy
]


EXTRAS_REQUIRE = {
    'code-check': [
        'pylint',
        'mypy'
    ],
    'tests': [
        'pytest',
        'pytest-cov',
    ],
    'docs': [
        'sphinx',
        'sphinx-gallery',
        'sphinx_rtd_theme',
        'numpydoc'
    ]
}

SETUP_REQUIRES = ['flake8', 'autopep8', 'wheel', 'compose']

setuptools.setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    packages=setuptools.find_packages(),
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    setup_requires=SETUP_REQUIRES    
)

package_dir = {'': 'pjdata'}  # For IDEs like Intellij to recognize the package.

