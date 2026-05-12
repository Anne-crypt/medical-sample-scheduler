# Laboratoire - Système de Planification

## Description

operate a medical scheduling app based on specific constraints

## Installation

clone possible
branch main --> version simple
branch intermediate-version --> version intermédiaire

## Utilisation

- execute tests : PYTHONPATH=. pytest
- one function : PYTHONPATH=. pytest -q tests/test_planner_intermediate.py -k lunch
- PYTHONPATH=. pytest -q tests/test_planner_intermediate.py (-k 20_samples)
- to execute main : python3 main.py 

## Évolution depuis version SIMPLE

tools
- ruff
- pylance
files
- add files for each classes
- add separate function in utils.py
- call those functions in main function planifyLab to fill the constraints

## Rendu en retard : exercice difficile

These tests passed in local
- Happy path : cas nominal qui fonctionne
- Priorités : STAT > URGENT > ROUTINE respecté
- Spécialisations : technicien compatible assigné
- Contraintes : au moins pauses déjeuner testées
- Efficacité : coefficient technicien appliqué
- metrics : ❌