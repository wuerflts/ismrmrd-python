import os
from setuptools import setup, find_packages
from distutils.command.build import build
from distutils.command.build_py import build_py

import logging
import shutil
from pathlib import Path
import re 

logging.basicConfig()
log_ = logging.getLogger(__name__)

schema_file = os.path.join('schema','ismrmrd.xsd')
config_file = os.path.join('schema','.xsdata.xml')

class my_build_py(build_py):
    def run(self):
        # honor the --dry-run flag
        if not self.dry_run:
            outloc = self.build_lib
            outloc = os.path.join(outloc,'ismrmrd/xsd/ismrmrdschema')

            
            generate_schema(schema_file, config_file, outloc)
                    # distutils uses old-style classes, so no super()
        build_py.run(self)


def fix_init_file(package_name,filepath):

    with open(filepath,'r+') as f:
        text = f.read()
        text = re.sub(f'from {package_name}.ismrmrd', 'from .ismrmrd',text)
        f.seek(0)
        f.write(text)
        f.truncate()




def generate_schema(schema_filename, config_filename, outloc  ):

    from xsdata.codegen.transformer import SchemaTransformer
    from xsdata.exceptions import CodeGenerationError
    from xsdata.logger import logger
    from xsdata.models.config import GeneratorConfig
    from xsdata.models.config import OutputFormat
    from xsdata.models.config import  OutputStructure

    def to_uri(filename):
        return Path(filename).absolute().as_uri()

    subpackage_name = 'ismrmrdschema'
    logger.setLevel(logging.INFO)
    config = GeneratorConfig.read(Path(config_filename))
    config.output.format = OutputFormat("pydata")
    config.output.package = subpackage_name 
    transformer = SchemaTransformer(config=config,print=False)
    transformer.process_schemas([to_uri(schema_filename)])
    fix_init_file(subpackage_name,f"{subpackage_name}/__init__.py")
    shutil.rmtree(os.path.join(outloc,subpackage_name),ignore_errors=True)
    shutil.move(subpackage_name,outloc)

setup(
    name='ismrmrd',
    version='1.7.1',
    author='ISMRMRD Developers',
    author_email='ismrmrd@googlegroups.com',
    description='Python implementation of the ISMRMRD',
    license='Public Domain',
    keywords='ismrmrd',
    url='https://ismrmrd.github.io',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ],
    install_requires=['xsdata>=21', 'numpy', 'h5py>=2.3'],
    setup_requires=['nose>=1.0', 'xsdata>=21'],
    test_suite='nose.collector',
    cmdclass={'build_py':my_build_py}
)
