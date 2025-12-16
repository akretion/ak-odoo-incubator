By default, it calls pywebdriver on "https://localhost".

Actions may be triggered by a server action like in this example

.. code-block:: xml

  <record id="print_stock_location_act_server" model="ir.actions.server">
      <field name="name">🖨 barcode location</field>
      <field name="model_id" ref="model_stock_location"/>
      <field name="binding_model_id" ref="model_stock_location"/>
      <field name="state">code</field>
      <field name="binding_type">report</field>
      <field name="code">
        action = model._print_my_barcode()
      </field>
  </record>


Don't forget binding_type set to report to get it works
