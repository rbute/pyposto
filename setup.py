from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps: [] = [
    'pytest',
]

setup(
    name="pyposto",
    version="0.0.2",
    author="Rakesh Bute",
    author_email="rakeshbute@gmail.com",
    description="Write Python functions as build steps ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rbute/pyposto",
    project_urls={
        "Code": "https://github.com/rbute/pyposto",
        # "Issue tracker": "https://github.com/rbute/pyposto/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.6',
    tests_require=test_deps,
    install_requires=
    [
        'click',
        'pyunpack',
        'urllib3',
        'wget',
        'pyyaml',
        'urllib3',
        'wget',
        'patool',
        'reentry',
        'click_plugins',
    ] + test_deps,
    entry_points={
        'console_scripts': [
            'pyposto=pyposto:step'
        ]
    }
)
