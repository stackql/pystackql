Getting Started
===============

``pystackql`` allows you to run StackQL queries against cloud and SaaS providers within a native Python environment.
The ``pystackql.StackQL`` class can be used with Pandas, Matplotlib, Jupyter and more. 

.. contents:: Contents
   :local:
   :depth: 2

Installation
************ 

`pystackql` can be installed from PyPI using pip:

.. code-block:: sh

    $ pip install pystackql

or you can use the ``setup.py`` script:

.. code-block:: sh

    $ git clone https://github.com/stackql/pystackql && cd pystackql
    $ python setup.py install

to confirm that the installation was successful, you can run the following command:

.. code-block:: python

    from pystackql import StackQL
    iql= StackQL()

    print(iql.version)
 
you should see a result like:

.. code-block:: sh

    v0.3.265

Authentication Overview
***********************

StackQL providers will have different authentication methods. To see the available authentication methods for a provider consult the `StackQL provider docs <https://registry.stackql.io/>`_.
In general most providers will use API keys or service account files which can be generated and revoked from the provider's console.

StackQL provider authentication is setup with the ``pystackql.StackQL`` class constructor using the `auth` keyword/named argument.  
The `auth` argument can be set to a dictionary or a string.  If a dictionary is used, the keys should be the provider name and the values should be the authentication method.  
If a string is supplied it needs to be a stringified JSON object with the same structure as the dictionary.

.. If a string is used, it should be the provider name.  
.. The authentication method will be read from the environment variable ``STACKQL_AUTH_<provider_name>``.  
.. For example, if you are using the Google provider, you can set the environment variable ``STACKQL_AUTH_GOOGLE`` to the path of your service account file.  
.. If you are using the AWS provider, you can set the environment variable ``STACKQL_AUTH_AWS`` to your API key.

.. note:: 

   Keyword arguments to the `StackQL` class constructor are simply command line arguments to the `stackql exec command <https://stackql.io/docs/command-line-usage/exec>`_.

Authentication Example
**********************

The following example demonstrates how to instantiate a `StackQL` session with authentication to the `aws`, `google` and `okta` providers.

.. code-block:: python

    from pyspark import SparkContext, SparkConf
    import sagemaker_pyspark

    conf = (SparkConf()
            .set("spark.driver.extraClassPath", ":".join(sagemaker_pyspark.classpath_jars())))
    SparkContext(conf=conf)


As a newbie experimenter/hobbyist in the field of IoT using BLE communications, I found it pretty hard to identify a Python package which would enable one to use a Raspberry Pi (Zero W inthis case) to swiftly scan, connect to and read/write from/to a nearby BLE device (GATT server). 

This package is intended to provide a quick, as well as (hopefully) easy to undestand, way of getting a simple BLE GATT client up and running, for all those out there, who, like myself, are hands-on learners and are eager to get their hands dirty from early on. 

For more installation options see the `StackQL docs <https://stackql.io/docs/installing-stackql>`_.


- As my main use-case scenario was to simply connect two devices, the current version of :class:`simpleble.SimpleBleClient` has been designed and implemented with this use-case in mind. As such, if you are looking for a package to allow you to connect to multiple devices, then know that off-the-self this package DOES NOT allow you to do so. However, implementing such a feature is an easily achievable task, which has been planned for sometime in the near future and if there proves to be interest on the project, I would be happy to speed up the process.

- Only Read and Write operations are currently supported, but I am planning on adding Notifications soon.

- Although the interfacing operations of the :class:`bluepy.btle.Service` and :class:`bluepy.btle.Peripheral` classes have been brought forward to the :class:`simpleble.SimpleBleClient` class, the same has not been done for the :class:`bluepy.btle.Descriptor`, meaning that the :class:`simpleble.SimpleBleClient` cannot be used to directly access the Descriptors. This can however be done easily by obtaining a handle of a :class:`simpleble.SimpleBleDevice` object and calling the superclass :meth:`bluepy.btle.Peripheral.getDescriptors` method. 

Running Queries
***************

- As my main use-case scenario was to simply connect two devices, the current version of :class:`simpleble.SimpleBleClient` has been designed and implemented with this use-case in mind. As such, if you are looking for a package to allow you to connect to multiple devices, then know that off-the-self this package DOES NOT allow you to do so. However, implementing such a feature is an easily achievable task, which has been planned for sometime in the near future and if there proves to be interest on the project, I would be happy to speed up the process.

