# PROCESSUS – gouvernance des données et du catalogue de données

## 1. Objet et finalité

Ce processus définit les modalités opérationnelles de gouvernance des données au sein de Neo Financia, y compris la gestion du catalogue de données. Il vise à garantir la qualité, l’intégrité, la sécurité et la traçabilité des données critiques, dans une logique de conformité réglementaire et d’efficience opérationnelle.

## 2. Champ d’application / Data Governance & Confidentialité (RGPD)

Le processus s’applique à l’ensemble des domaines métiers, directions et systèmes impliqués dans la création, l’usage, le traitement ou la gouvernance des données de référence, transactionnelles, analytiques ou personnelles.

## 3. Parties prenantes & RACI (rôles)

| Rôle                     | Responsable | Autorité | Consulté | Informé |
| ------------------------ | ----------- | -------- | -------- | ------- |
| Chief Data Officer (CDO) | X           | X        | -        | X       |
| Data Stewards            |             |          | X        | X       |
| Responsables métiers     |             | X        | X        | X       |
| RSSI / DPO               |             | X        | X        | X       |
| IT / Data Engineering    |             | X        | X        | X       |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

* **Fournisseurs** : métiers, DSI, conformité, partenaires technologiques
* **Déclencheurs** : mise en production d’un nouveau système, création de données sensibles, incident RGPD, audit, projet réglementaire
* **Entrées** : dictionnaires métiers, référentiels de données, audits, incidents, normes ISO/BCBS

## 5. Macro-workflow BPMN / chaîne de valeur

### 5.1 Vue d’ensemble (diagramme texte + numérotation)

1. Identification des actifs de données critiques
2. Nomination d’un Data Owner et d’un Data Steward
3. Cartographie et classification des données (sensibilité, usage, cycle de vie)
4. Enregistrement dans le catalogue de données (Data Catalog)
5. Définition des règles de gestion, qualité et conformité
6. Mise en place des contrôles automatisés et manuels
7. Revue périodique et gouvernance continue

### 5.2 Sous-processus clés

* Gestion du dictionnaire de données
* Publication et maintien du catalogue de données
* Validation des règles de qualité et d’usage
* Notification des modifications aux parties prenantes

### 5.3 Points de contrôle & jalons

* Revue mensuelle du catalogue
* Approbation des règles de gouvernance par le CDO
* Intégration dans les comités Data & IT

## 6. Sorties et clients internes/externes (SIPOC – O/C)

* **Sorties** : catalogue de données à jour, fiches de gouvernance, plans d’action correctifs
* **Clients internes** : data analysts, métiers, DSI, conformité, audit interne
* **Clients externes** : autorités (ACPR, CNIL), auditeurs tiers

## 7. Ressources & systèmes support (IT, data, fournisseurs)

* Plateforme de Data Cataloging (ex. Collibra, Alation)
* Systèmes de gestion de la qualité de données (DQ tool)
* CRM, ERP, Core Banking System
* Référentiels internes (glossaire métier, GED)

## 8. Exigences de conformité ({{REGS}})

* RGPD (Règlement Général sur la Protection des Données)
* ISO/IEC 27001 & 27701
* Règlementations ACPR & lignes directrices EBA
* BCBS 239 sur la gestion des risques liés aux données

## 9. Indicateurs de performance (KPIs) & seuils SLA

* % de données critiques enregistrées dans le catalogue (>95 %)
* Délai de mise à jour des métadonnées (< 5 jours ouvrés)
* Taux de conformité des règles de qualité (> 98 %)

## 10. Risques, gaspillages (Lean) et actions de mitigation

* Risque : données non cataloguées → mitigation : contrôle d’exhaustivité mensuel
* Risque : mauvaise qualité des métadonnées → mitigation : automatisation des règles de qualité
* Gaspillages : doublons d’entrée → mitigation : déduplication automatisée

## 11. Interfaces & dépendances croisées (processus amont/aval)

* Processus amont : acquisition de données, création de produits/services
* Processus aval : analyse BI, reporting réglementaire, gestion des incidents

## 12. Plans d’amélioration continue (PDCA)

* P : audit du cycle de vie des données & identification des écarts
* D : mise en œuvre de règles de gouvernance cibles
* C : reporting régulier au comité de gouvernance des données
* A : adaptation des règles selon retours et évolutions réglementaires

## 13. Historique des versions (tableau)

| Version | Date       | Auteur        | Modifications principales      |
| ------- | ---------- | ------------- | ------------------------------ |
| 1.0     | 2025-05-28 | D. Consultant | Création initiale du processus |
