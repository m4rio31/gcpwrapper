import setuptools

REQUIRED_PACKAGES = [
    "google-cloud-logging==3.2.4"
]

setuptools.setup(name='gcpwrapper',
                 version='1.0.0.dev1',
                 install_requires=REQUIRED_PACKAGES,
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "Operating System :: OS Independent"
                     ]
)