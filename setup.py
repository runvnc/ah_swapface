from setuptools import setup, find_packages

setup(
    name="ah_swapface",
    version="1.0.3",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    include_package_data=True,
    install_requires=[
        "onnxruntime",
        "torch==0.4.1",
        "opencv-python",
        "pillow", 
        "numpy==1.26.3",
        "nanoid",
        "scipy",
        "scikit-learn"
    ],
    dependency_links=[
        "git+https://github.com/deepinsight/insightface.git#egg=insightface&subdirectory=python-package"
    ]
)
