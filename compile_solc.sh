#!/bin/bash
solc --combined-json abi,bin contracts/*.sol -o . --overwrite