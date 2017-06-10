"A server that performs SPAKE2 operations, for interoperability testing."

# Install this, then run "twist spake2_interop" and hit http://HOST:8705/

from setuptools import setup
import versioneer

setup(
    name="spake2-interop-python-spake2-0.7",
    version=versioneer.get_version(),
    author="Brian Warner",
    author_email="warner@lothar.com",
    package_dir={"": "src"},
    # this must be installed into its own virtualenv (e.g. it can't share a
    # venv with spake2-0.3), so we don't need a version-specific package
    # name, and keeping it neutral will minimize the diff
    packages=["spake2_interop_python"],
    license="MIT",
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        "spake2==0.7",
        ],
      entry_points={
          "console_scripts":
          [
              "spake2_interop_python_0_7 = spake2_interop_python:run",
          ]
      },
    )
