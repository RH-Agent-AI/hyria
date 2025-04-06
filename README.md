# Hyria

Hyria est une application web basée sur **FastAPI** destinée à gérer l'accès à une base de données dans le cadre du projet RH-Agent-AI. Ce projet a été développé dans le contexte d'un hackathon et intègre des déploiements automatisés via GitHub et AWS CodeDeploy.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Déploiement](#déploiement)
- [Configuration](#configuration)
- [Contribuer](#contribuer)
- [Licence](#licence)
- [Contact](#contact)

## Fonctionnalités

- **API REST** : Développée avec FastAPI pour une gestion efficace des requêtes.
- **Déploiement automatisé** : Intégration avec GitHub et AWS CodeDeploy pour des mises à jour continues.
- **Sécurité** : Gestion des accès et déploiement sécurisé.
- **Base de données** : Connexion à une base hébergée (actuellement sur Render).

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip
- (Optionnel) Virtualenv
- Git

### Étapes d'installation

1. **Cloner le dépôt**

   Ouvrez un terminal et clonez le dépôt dans le dossier de votre choix :
   ```bash
   git clone https://gitingest.com/RH-Agent-AI/hyria.git
   cd hyria
