.. image:: https://stackql.io/img/stackql-logo-bold.png
    :alt: "stackql logo"
    :target: https://github.com/stackql/stackql
    :align: center

======================================
PyStackQL - Python Wrapper for StackQL
======================================

.. image:: https://readthedocs.org/projects/pystackql/badge/?version=latest
   :target: https://pystackql.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/pystackql
   :target: https://pypi.org/project/pystackql/
   :alt: PyPI

StackQL is an open source developer tool which allows you to query and interact with cloud and SaaS provider APIs using SQL grammar.
StackQL can be used for cloud inventory analysis, cloud cost optimization, cloud security and compliance, provisioning/IaC, assurance, XOps, and more.

PyStackQL is a Python wrapper for StackQL which allows you to use StackQL within Python applications and to use the power of Python to extend StackQL.
PyStackQL can be used with ``pandas``, ``matplotlib``, ``plotly``, ``jupyter`` and other Python libraries to create powerful data analysis and visualization applications.

For detailed documentation, including the API reference, see `Read the Docs <https://pystackql.readthedocs.io>`_.

Installing PyStackQL
-----------------------------------

PyStackQL can be installed with pip as follows:

::

    pip install pystackql

You can install from source by cloning this repository and running a pip install command in the root directory of the repository:

::

    git clone https://github.com/stackql/pystackql
    cd pystackql
    pip install .

Using PyStackQL
-----------------------------------

The following example demonstrates how to run a query and return the results as a ``pandas.DataFrame``:

::

    from pystackql import StackQL
    import pandas as pd
    region = "ap-southeast-2"
    stackql = StackQL()
    
    query = """
    SELECT instanceType, COUNT(*) as num_instances
    FROM aws.ec2.instances
    WHERE region = '%s'
    GROUP BY instanceType
    """ % (region)   
    
    res = stackql.execute(query)
    df = pd.read_json(res)
    print(df)

You can find more examples in the `stackql docs <https://stackql.io/docs>`_ or the examples in `readthedocs <https://pystackql.readthedocs.io/en/latest/examples.html>`_.

Supported Operating Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyStackQL (and StackQL) are supported on:

- MacOS (arm and amd)
- Linux
- Windows

Supported Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~~

PyStackQL has been tested on:

- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11

Licensing
~~~~~~~~~
PyStackQL is licensed under the MIT License. The license is available `here <https://github.com/stackql/pystackql/blob/main/LICENSE>`_


Building the docs
~~~~~~~~~~~~~~~~~

To build the docs, you will need to install the following packages:

::

    pip install sphinx sphinx_rtd_theme sphinx-autodoc-typehints

Then, from the root directory of the repository, run:

::

    cd docs
    make html

The docs will be built in the ``docs/build/html`` directory.

Building the package
~~~~~~~~~~~~~~~~~~~~

To build the package, you will need to install the following packages:

::

    pip install setuptools wheel twine

Then, from the root directory of the repository, run:

::

    python3 setup.py sdist

The package will be built in the ``dist`` directory.

Publishing the package
~~~~~~~~~~~~~~~~~~~~~~

To publish the package to PyPI, run the following command:

::

    twine upload dist/pystackql-2.0.0.tar.gz
