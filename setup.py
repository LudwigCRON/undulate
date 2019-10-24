from setuptools import setup, find_packages

project_url = 'https://github.com/LudwigCRON/pywave'

requires = ['pycairo >= "1.18.1"',
            'PyYAML >= "5.1.2"',
            'python_version>="3.5"']

setup(
    name='pywaveform',
    use_scm_version={
        "relative_to": __file__,
        "write_to": "pywave/version.py",
    },
    url=project_url,
    license='MIT license',
    author='Ludwig CRON',
    author_email='ludwig.cron@gmail.com',
    description='pywave diagrams based on their textual representation',
    long_description=open("README.md").read(),
    zip_safe=False,
    classifiers=[],
    platforms='any',
    packages=["pywave"],
    include_package_data=True,
    install_requires=requires,
    setup_requires=[
        'setuptools_scm',
    ],
    entry_points={
        'console_scripts': [
            'pywave = pywave:main',
        ],
    },
    keywords=['pywave'],
)
