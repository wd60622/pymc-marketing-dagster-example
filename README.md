# PyMC-Marketing Dagster Example

This repository contains an example of how to use PyMC-Marketing and Dagster to
build a simple marketing attribution model.

![Backfill](./images/scheduled-backfill.png)

Kick off the dagster dev server with the following command:

```bash
export DAGSTER_HOME=$(pwd)/artifacts
mkdir $DAGSTER_HOME
dagster dev -m pymc_marketing_dagster_example.definitions
```

## Local Development

Install the environment with `conda`:

```bash
conda env create -f environment.yml
```

Activate the environment and install the package in editable mode:

```bash
conda activate pymc-marketing-dagster-example
pip install -e .
```