import setuptools

with open("README.md", "r") as nerd:
    long_description = nerd.read()

setuptools.setup(
        name="sableye",
        version="1.0.0",
        author="nubby",
        author_email="nubby@mail.com",
        description="the tiny radish-rover",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/itsnubby/sableye.git",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",      # 2 has limited funkitude.
            "License :: OSI Approved :: Apache License 2.0",
            "Operating System :: Linux",
            ],
        python_requires='>=3.6',
        )
