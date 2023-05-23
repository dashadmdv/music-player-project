from setuptools import find_packages, setup
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='dashadmdv_music_player_sync',
    packages=find_packages(include=['dashadmdv_music_player_sync']),
    version='0.1.0',
    description='Custom sync for my music player',
    author='dashadmdv',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
