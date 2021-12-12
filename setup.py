from setuptools import find_packages, setup

setup(
    name='zdspy',
    version='0.0.1',
    description='',
    long_description='',
    long_description_content_type='',
    license='',
    author='',
    author_email='',
    keywords='',
    classifiers=[],
    python_requires='>=3.9',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ndspy',
    ],
    extras_require={
        'test': [
            'tox',
        ]
    },
)
