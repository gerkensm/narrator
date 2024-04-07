from setuptools import setup, find_packages

setup(
    name='narrator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'openai',
        'pygame',
        'pydub',
        'mutagen',
        'aiohttp',
        'click',
        'pillow',
        'opencv-python',
        'python-magic',
        'pydantic>=2.6.4',
        'pydantic-settings>=2.2.1',
    ],
    entry_points={
        'console_scripts': [
            'narrator = narrator.main:main',
        ],
    },
)
