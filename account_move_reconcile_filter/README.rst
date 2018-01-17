Account Move Reconcile Filter
===============================

This module add a computed field on reconciliation object and a filter on the account_move_line
You are not able to filter your account move line based on a reconciliation date (max date of all move reconciled)


Fast installation
-------------------


ALTER TABLE account_move_reconcile ADD reconcile_date date;


UPDATE account_move_reconcile
    SET reconcile_date = TMP.rec_date
FROM (
    SELECT max(date) as rec_date, reconcile_id
    FROM account_move_line
    GROUP BY reconcile_id
    ) AS TMP
WHERE TMP.reconcile_id = account_move_reconcile.id;
