from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="aak_agency",
    version="0.1.0",
    description="AAK Agency — CBL Chocolate Distribution ERP Customisation",
    author="lakal96",
    author_email="kapila@aakagency.lk",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
