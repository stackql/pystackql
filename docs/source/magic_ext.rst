StackqlMagic Extension for Jupyter
==================================

The ``StackqlMagic`` extension for Jupyter notebooks provides a convenient interface to run StackQL queries against cloud or SaaS providers directly from within the notebook environment. Results can be visualized in a tabular format using Pandas DataFrames.

Setup
-----

To enable the `StackqlMagic` extension in your Jupyter notebook, use the following command:

.. code-block:: python

    %load_ext pystackql.magic

To use the `StackqlMagic` extension in your Jupyter notebook to run queries against a StackQL server, use the following command:

.. code-block:: python

    %load_ext pystackql.magics

Usage
-----

The extension provides both line and cell magic functionalities:

1. **Line Magic**:
    
   You can run StackQL queries directly from a single line:

   .. code-block:: python

       %stackql DESCRIBE aws.ec2.instances

2. **Cell Magic**:
   
   For multi-line queries or when you need to use specific options:

   .. code-block:: python

        %%stackql
        SELECT instanceType, COUNT(*) as num_instances
        FROM aws.ec2.instances 
        WHERE region = '$region' GROUP BY instanceType       

Options
-------

When using `StackqlMagic` as cell magic, you can pass in the following options:

- ``--no-display`` : Suppresses the display of the results. Even when this option is enabled, the results are still saved in the `stackql_df` Pandas DataFrame.

Example:

.. code-block:: python

    project = 'stackql-demo'
    zone = 'australia-southeast1-a'
    region = 'australia-southeast1'

.. code-block:: python

    %%stackql --no-display
    SELECT SPLIT_PART(machineType, '/', -1) as machine_type, count(*) as num_instances 
    FROM google.compute.instances 
    WHERE project = '$project' AND zone = '$zone'
    GROUP BY machine_type

This will run the query but won't display the results in the notebook. Instead, you can later access the results via the `stackql_df` variable.

.. note::

    The results of the queries are always saved in a Pandas DataFrame named `stackql_df` in the notebook's current namespace. This allows you to further process or visualize the data as needed.

An example of visualizing the results using Pandas is shown below:

.. code-block:: python

    stackql_df.plot(kind='pie', y='num_instances', labels=_['machine_type'], title='Instances by Type', autopct='%1.1f%%')

--------

This documentation provides a basic overview and usage guide for the `StackqlMagic` extension. For advanced usage or any additional features provided by the extension, refer to the source code or any other accompanying documentation.
