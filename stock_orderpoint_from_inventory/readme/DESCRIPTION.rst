This module allows you to create Reordering Rules in one go through the Inventory screen.

The excel file is created according to the following logic:

- If there is a Reordering Rule that can be matched with the Inventory Line, it is placed along with its external id
  (external ID is generated if it didn't exist)

- If there is none, create a Reordering Rule according to some baseline logic that can be customized with
  "orderpoint_initialize_from_inventory_ratio_min" and "orderpoint_initialize_from_inventory_ratio_max" config params,
  which will take the current inventory and multiply it to obtain respectively the min and max for the Reordering Rules

- The Reordering Rule / Inventory Line is matched according to the product ID, and the warehouse (through the Inventory's Stock Location)

