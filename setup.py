import os

from setuptools import setup, find_packages

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('data')

setup(
    name='ADR_Tagger',
    version='0.1',
    description='Estracción de relaciones de RAM en textos biomédicos con Spacy y SKLearn.',
    packages=find_packages(),
    package_data={'': extra_files},
    include_package_data=True,
    install_requires=['jpype1==1.2.1',
                      'nltk==3.6.2',
                      'scikit-learn==0.24.2',
                      'simstring-pure==1.0.0',
                      'six==1.16.0',
                      'spacy>=3.1.1',
                      'tqdm==4.62.0'],
)

