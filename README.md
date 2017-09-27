[![Build Status](https://travis-ci.org/akretion/ak-odoo-incubator.svg?branch=10.0)](https://travis-ci.org/akretion/ak-odoo-incubator)
[![Coverage Status](https://coveralls.io/repos/github/akretion/ak-odoo-incubator/badge.svg?branch=10.0)](https://coveralls.io/github/akretion/ak-odoo-incubator?branch=10.0)
[![Code Climate](https://codeclimate.com/github/akretion/ak-odoo-incubator/badges/gpa.svg)](https://codeclimate.com/github/akretion/ak-odoo-incubator)


# Akretion Incubator
## Branch management from v10 version

This repository is used by Akretion for sharing R&D module.
Most of module are used in production so you can use it, but be carreful that we can make breaking change between version
When module will be enought generic and stabilized we will propose them to the OCA

# Dev tips

This project use black and pre-commit.
Please install precommit if you want to contribute

- no 10.0 branch
- branch name convention :
  - 10-my-module : permanent stable branch
  - 10-my-module-david-...-wip : working branch

 - PR are done : 10-my-module-david-...-wip -> 10-my-module
 - When PR is done, 10-my-module-david-...-wip is removed
 - PR are done : 10-my-module...-wip -> 10.0

After cloning just run
```
pre-commit install
```

So the git hook will be installed and every check can be perform automatically

