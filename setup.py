from setuptools import setup, find_packages

setup(
    name="ah_swapface",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "insightface",
        "onnxruntime",
        "torch",
        "opencv-python",
        "pillow", 
        "numpy",
        "nanoid"
    ],
)
