# PROCESSUS – clôture comptable mensuelle et consolidation

## 1. Objet et finalité

Ce processus a pour objectif de définir les étapes, rôles, contrôles et livrables liés à la clôture comptable mensuelle de Neo Financia, ainsi qu’à la consolidation des résultats des entités juridiques du groupe. Il vise à garantir la fiabilité des comptes, le respect des délais de clôture (J+6), la conformité réglementaire et la production d’états financiers consolidés permettant une communication financière fiable.

## 2. Champ d’application / Finance, Trésorerie & Reporting

Ce processus s’applique à :

- toutes les entités juridiques de Neo Financia (France, Royaume-Uni, etc.),
- l’ensemble des activités comptables : saisie, justification, rapprochements, provisions, réconciliations intra-groupe, clôtures analytiques,
- le processus de consolidation dans l’outil groupe.

## 3. Parties prenantes & RACI (rôles)

| Activité                             | R (Responsable)   | A (Accountable) | C (Consulté)            | I (Informé)           |
|-------------------------------------|--------------------|------------------|--------------------------|------------------------|
| Préparation du calendrier de clôture| Comptabilité       | Directeur Financier | Consolidation | Contrôle de gestion |
| Comptabilisation des écritures      | Comptabilité       | Responsable Comptable | Contrôle Interne | Audit interne |
| Réconciliations intra-groupes       | Consolidation      | Responsable Consolidation | Trésorerie | Direction Générale |
| Revue des provisions et cut-offs    | Contrôle de gestion| Directeur Financier | Juridique, Fiscalité | Audit externe |
| Chargement dans outil de consolidation | Consolidation | Responsable Consolidation | IT Finance | Audit interne |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

- Déclencheur : fin de période (dernier jour ouvré du mois)
- Fournisseurs :
  - ERP comptable (journaux, balances)
  - Systèmes métiers (core banking, CRM, RH)
  - Services opérationnels (factures, immobilisations, contrats)
  - Trésorerie (écritures bancaires, flux financiers)
  - Fiscalité / Juridique (provisions, litiges)

## 5. Macro-workflow BPMN / chaîne de valeur

### 5.1 Vue d’ensemble (diagramme texte + numérotation)

1. Lancement du calendrier de clôture (J-1)
2. Extraction et saisie des écritures de fin de mois (J+1)
3. Rapprochements bancaires et intercos (J+2)
4. Justification des comptes (J+3)
5. Contrôles, revue analytique, provisions (J+4)
6. Chargement consolidation groupe (J+5)
7. Rapport de clôture et validation finale (J+6)

### 5.2 Sous-processus clés

- Gestion des provisions mensuelles (charges à payer, produits constatés d’avance, risques, etc.)
- Réconciliation intra-groupe et ajustements IFRS
- Reporting flash à la direction financière
- Consolidation multi-entités (filiales, succursales)

### 5.3 Points de contrôle & jalons

- Cut-off factures fournisseurs validé (J+2)
- Justification des comptes sensibles (trésorerie, clients, fournisseurs) achevée (J+3)
- Check-list clôture validée par l’équipe finance (J+5)
- Rapport de clôture signé électroniquement (J+6)

## 6. Sorties et clients internes/externes (SIPOC – O/C)

- Sorties :
  - Balance de vérification mensuelle
  - Rapport de clôture synthétique
  - Dossier de justification des comptes
  - Données chargées dans outil de consolidation
- Clients :
  - Direction Financière
  - Direction Générale
  - Auditeurs internes et externes
  - Supervision réglementaire (ACPR, EBA)

## 7. Ressources & systèmes support (IT, data, fournisseurs)

- ERP Comptable (ex. Sage X3, Oracle, SAP)
- Outil de consolidation (ex. SAP BFC, LucaNet)
- Référentiels tiers (clients/fournisseurs)
- Intranet Finance (calendrier, modèles de provision, checklist)
- Plateformes intercos (reconciliations groupe)

## 8. Exigences de conformité ({{REGS}})

- Règlement ANC 2022-06 (comptabilité bancaire)
- Normes IFRS 10/11/12 et IAS 27-28
- ISO 9001 : processus qualité, documentation, traçabilité
- ISO 27001 : sécurité des données financières
- Règlementations ACPR/EBA sur les reportings financiers

## 9. Indicateurs de performance (KPIs) & seuils SLA

| Indicateur                             | Objectif             |
|----------------------------------------|----------------------|
| Taux de clôture dans les délais (J+6)  | ≥ 98 %               |
| Taux d’écarts intercos résolus         | ≥ 95 %               |
| Taux de comptes justifiés              | 100 % (comptes clés) |
| Nombre de corrections post-clôture     | ≤ 2 / mois           |

## 10. Risques, gaspillages (Lean) et actions de mitigation

- **Risque** : Retard sur saisie ou réconciliation
  - *Action* : automatisation des écritures récurrentes
- **Risque** : Données incomplètes / erreurs de reporting
  - *Action* : checklists et contrôles croisés
- **Gaspillage Lean** : double saisie, ressaisie manuelle
  - *Action* : interfaces automatisées entre ERP et consolidation

## 11. Interfaces & dépendances croisées (processus amont/aval)

- Amont :
  - Processus achat/facturation
  - Processus trésorerie
  - Processus paie & RH
- Aval :
  - Reporting réglementaire et comptable
  - Présentations au comité de direction
  - Reporting groupe consolidé

## 12. Plans d’amélioration continue (PDCA)

- **Plan** : cartographie des écarts post-clôture (retours d’expérience)
- **Do** : automatisation des écritures récurrentes, macros de contrôle
- **Check** : audits internes trimestriels
- **Act** : mise à jour du manuel de clôture et formation continue

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                  | Modifications apportées             |
|---------|------------|-------------------------|-------------------------------------|
| 1.0     | 2025-05-28 | Département Finance     | Création initiale du processus      |
| 1.1     | 2025-06-10 | Contrôle Interne        | Ajout des contrôles post-J+3        |
