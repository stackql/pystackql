Getting Started
===============

:mod:`pystackql` allows you to run StackQL queries against cloud and SaaS providers within a native Python environment.
The :class:`pystackql.StackQL` class can be used with Pandas, Matplotlib, Jupyter and more. 

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

    # see registry.stackql.io for provider auth block descriptions
    provider_auth =  { 
        "aws": { 
            "credentialsenvvar": "AWS_SECRET_ACCESS_KEY", 
            "keyIDenvvar": "AWS_ACCESS_KEY_ID", 
            "type": "aws_signing_v4" 
        },
        "google": { 
            "type": "service_account",  
            "credentialsfilepath": "creds/sa-key.json" 
        },
        "okta": { 
            "type": "api_key",
            "credentialsenvvar": "OKTA_SECRET_KEY", 
            "valuePrefix": "SSWS " 
        }
    }
    stackql = StackQL(auth=provider_auth)
    query = "SELECT ..."
    res = stackql.execute(query)


In the above example you will need environment variables set for the `aws` and `okta` providers.  The `google` provider will use the service account file located at `creds/sa-key.json`.

Running Queries
***************

The :class:`pystackql.StackQL` class has a single method, :meth:`pystackql.StackQL.execute`, which can be used to run StackQL queries and return results in `json`, `csv`, `text` or `table` format.
