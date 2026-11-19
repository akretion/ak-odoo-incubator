To make it work, you will need to deactivate the cron once the database is not in production anymore.

For instance with a script that runs:

.. code:: sql

    UPDATE ir_cron SET active='f' WHERE cron_name = 'Database Age Cron';
