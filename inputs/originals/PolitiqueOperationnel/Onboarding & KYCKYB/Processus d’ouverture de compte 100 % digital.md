# PROCESSUS – ouverture de compte 100 % digital

## 1. Objet et finalité

Ce processus détaille les étapes d’ouverture de compte bancaire entièrement digital chez Neo Financia, intégrant les contrôles réglementaires obligatoires (KYC/KYB). Il garantit une expérience fluide et sécurisée, conforme aux réglementations ACPR/EBA, RGPD et PSD2, tout en optimisant l’efficacité opérationnelle grâce à une approche Lean.

## 2. Champ d’application / Onboarding & KYC/KYB

Le processus couvre :

* Ouverture de comptes pour particuliers (KYC)
* Ouverture de comptes pour professionnels (KYB)
* Toutes les étapes depuis la demande initiale jusqu’à l’activation du compte.

## 3. Parties prenantes & RACI (rôles)

| Rôle                   | Responsable (R) | Acteur (A) | Consulté (C) | Informé (I) |
| ---------------------- | --------------- | ---------- | ------------ | ----------- |
| Responsable Onboarding | R               |            |              |             |
| Analyste KYC/KYB       |                 | A          |              |             |
| Responsable Conformité |                 | C          |              | I           |
| Équipe Support client  |                 | A          |              | I           |
| Responsable IT         |                 | A          | C            | I           |
| Directeur Général      |                 |            |              | I           |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

| Entrées                          | Déclencheurs                     | Fournisseurs      |
| -------------------------------- | -------------------------------- | ----------------- |
| Demande client en ligne          | Soumission du formulaire web/app | Client            |
| Pièces justificatives numériques | Envoi des documents via app/web  | Client            |
| Données de validation KYC/KYB    | Demande initiale du client       | Bases externes    |
| Vérification automatisée         | Réception pièces justificatives  | Systèmes internes |

## 5. Macro-workflow BPMN / chaîne de valeur

### 5.1 Vue d’ensemble (diagramme texte + numérotation)

``
[1] Réception demande → [2] Vérification automatisée des données → [3] Analyse KYC/KYB → [4] Décision d’ouverture → [5] Création compte digital → [6] Notification client → [7] Activation du compte par le client → [8] Archivage électronique des pièces et données → [9] Suivi post-ouverture
``

### 5.2 Sous-processus clés

* **2.1 Vérification automatisée** : Validation initiale de cohérence des données client (identité, adresse, statut pro).
* **3.1 Analyse approfondie KYC/KYB** : Contrôles complémentaires manuels (si nécessaire) par analyste conformité.
* **4.1 Décision automatisée** : Validation automatisée (scoring risque) avec intervention humaine si exceptions.
* **5.1 Création technique du compte** : Ouverture effective dans le système bancaire digital.

### 5.3 Points de contrôle & jalons

* Vérification automatique des documents (étape 2)
* Validation KYC/KYB par analyste conformité (étape 3)
* Décision finale avant création du compte (étape 4)
* Confirmation activation compte client (étape 7)

## 6. Sorties et clients internes/externes (SIPOC – O/C)

| Sorties                        | Clients internes/externes |
| ------------------------------ | ------------------------- |
| Compte bancaire digital ouvert | Client (externe)          |
| Rapport conformité KYC/KYB     | Compliance (interne)      |
| Données d’ouverture archivées  | Audit interne (interne)   |

## 7. Ressources & systèmes support (IT, data, fournisseurs)

* Plateforme d’onboarding digital (web et mobile)
* Logiciel automatisé de vérification documentaire (IA)
* Solution de scoring et gestion des risques (GRC)
* Système bancaire central pour gestion des comptes
* Archivage sécurisé numérique (SharePoint sécurisé)

## 8. Exigences de conformité (ACPR/EBA, RGPD, PSD2, ISO 9001/27001)

* **ACPR/EBA** : Respect strict des exigences d’identification client, vérification des documents, lutte contre la fraude.
* **RGPD** : Protection rigoureuse des données personnelles collectées et traitées.
* **PSD2** : Sécurisation renforcée du processus d’ouverture et d’authentification des clients.
* **ISO 9001/27001** : Qualité de service et sécurité des systèmes d’information garantissant confidentialité et intégrité des données.

## 9. Indicateurs de performance (KPIs) & seuils SLA

| Indicateur                               | Fréquence   | SLA                                 |
| ---------------------------------------- | ----------- | ----------------------------------- |
| Durée totale ouverture compte            | Mensuel     | ≤ 10 minutes (auto), ≤ 24h (manuel) |
| Taux de comptes validés automatiquement  | Mensuel     | ≥ 85 %                              |
| Taux d’erreurs/demandes incomplètes      | Mensuel     | ≤ 5 %                               |
| Taux de satisfaction client (onboarding) | Trimestriel | ≥ 90 %                              |

## 10. Risques, gaspillages (Lean) et actions de mitigation

| Risque/gaspillage               | Actions de mitigation                                            |
| ------------------------------- | ---------------------------------------------------------------- |
| Documents incomplets/illisibles | Clarification proactive dans l’application, contrôle automatique |
| Reprises manuelles excessives   | Amélioration continue de l’automatisation (IA)                   |
| Non-conformité réglementaire    | Audits réguliers et contrôles renforcés                          |

## 11. Interfaces & dépendances croisées (processus amont/aval)

| Processus amont                 | Processus aval                    |
| ------------------------------- | --------------------------------- |
| Marketing & Acquisition client  | Activation des services bancaires |
| Veille réglementaire compliance | Suivi continu conformité          |
| Développement IT                | Support client post-ouverture     |

## 12. Plans d’amélioration continue (PDCA)

* **Plan** : Analyse régulière des retours client et des incidents compliance.
* **Do** : Mise en œuvre d’optimisations digitales et d’automatisation.
* **Check** : Validation trimestrielle des résultats KPI.
* **Act** : Ajustements permanents et intégration des meilleures pratiques observées.

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                 | Modification principale        |
| ------- | ---------- | ---------------------- | ------------------------------ |
| 1.0     | 28/05/2025 | Consultant Senior BPMN | Création initiale du processus |
| 1.1     |            |                        |                                |
| 1.2     |            |                        |                                |
