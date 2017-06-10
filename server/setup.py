"A server that performs SPAKE2 operations, for interoperability testing."

# Install this, then run "twist spake2_interop" and hit http://HOST:8705/

from setuptools import setup
import versioneer

setup(
    name="spake2-interop-server",
    version=versioneer.get_version(),
    author="Brian Warner",
    author_email="warner@lothar.com",
    url="https://github.com/warner/spake2-interop",
    package_dir={"": "src"},
    packages=["spake2_interop_server",
              "twisted.plugins",
              ],
    license="MIT",
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        "twisted",
        ],
    )
