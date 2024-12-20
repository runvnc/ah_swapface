from setuptools import setup, find_packages

setup(
    name="ah_swapface",
    version="1.0.1",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    include_package_data=True,
    install_requires=[
        "onnxruntime",
        "torch",
        "opencv-python",
        "pillow", 
        "numpy",
        "nanoid"
    ],
    dependency_links=[
        "git+https://github.com/deepinsight/insightface.git#egg=insightface&subdirectory=python-package"
    ]
)
