[![Build Status](https://travis-ci.org/akretion/ak-odoo-incubator.svg?branch=10.0)](https://travis-ci.org/akretion/ak-odoo-incubator)
[![Coverage Status](https://coveralls.io/repos/github/akretion/ak-odoo-incubator/badge.svg?branch=10.0)](https://coveralls.io/github/akretion/ak-odoo-incubator?branch=10.0)
[![Code Climate](https://codeclimate.com/github/akretion/ak-odoo-incubator/badges/gpa.svg)](https://codeclimate.com/github/akretion/ak-odoo-incubator)


## Branch management from v10 version

In this repo we have one branch per module.

Example for v10:

- no 10.0 branch

- branch name convention :
  - 10-my-module : permanent stable branch
  - 10-my-module-david-...-wip : working branch

 - PR are done : 10-my-module-david-...-wip -> 10-my-module
 - When PR is done, 10-my-module-david-...-wip is removed
 - PR are done : 10-my-module...-wip -> 10.0
