from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements.txt
with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="crypto-wallet-finder",  # Changed to be more specific and avoid conflicts
    version="1.0.0",
    packages=find_packages(),
    install_requires=requirements,
    
    # Metadata
    author="Wallet Finder Contributors",
    author_email="your.email@example.com",  # Update this
    description="A tool for finding cryptocurrency wallet seeds using parallel processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wallet_finder",  # Update this
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/wallet_finder/issues",  # Update this
    },
    
    # Classifiers help users find your project
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    
    # Package requirements
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "wallet-finder=wallet_finder.gui:main",
        ],
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        "wallet_finder": ["*.txt", "*.json"],
    },
)
