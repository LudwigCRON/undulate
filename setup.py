from setuptools import setup

PROJECT_URL = "https://github.com/LudwigCRON/undulate"
REQUIRES = [
    "cairocffi>=1.4.0",
    "pangocffi>=0.11.0",
    "pangocairocffi>=0.7.0",
    'PyYAML >= "5.1.2"',
    'python_version>="3.5"',
]

setup(
    name="undulate",
    use_scm_version={"relative_to": __file__, "write_to": "undulate/version.py"},
    url=PROJECT_URL,
    license="MIT license",
    author="Ludwig CRON",
    author_email="ludwig.cron@gmail.com",
    description="generate waveform diagrams of signals based on their textual representation",
    long_description=open("README.md").read(),
    zip_safe=False,
    classifiers=[],
    platforms="any",
    packages=["undulate"],
    include_package_data=True,
    install_requires=REQUIRES,
    setup_requires=["setuptools_scm"],
    entry_points={"console_scripts": ["undulate = undulate.cli:main"]},
    keywords=["undulate"],
)
