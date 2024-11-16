from setuptools import setup, find_packages

setup(
    name="CopyCutFolders",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PySide6>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "copycutfolders=CopyCutFolders.main:main",
        ],
    },
    author="あなたの名前",
    author_email="あなたのメール",
    description="アニメーション制作用のカットフォルダコピーツール",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/あなたのユーザー名/CopyCutFolders",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 