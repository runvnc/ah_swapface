from setuptools import setup, find_packages

setup(
    name="ah_swapface",
    version="1.0.3",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    include_package_data=True,
    install_requires=[
        "onnxruntime",
        "torch",
        "opencv-python",
        "pillow", 
        "numpy~=2.0.0",
        "nanoid",
        "scipy",
        "scikit-learn"
    ],
    dependency_links=[
        "git+https://github.com/deepinsight/insightface.git#egg=insightface&subdirectory=python-package"
    ]
)
