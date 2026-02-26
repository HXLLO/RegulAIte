# PROCÉDURE – gestion de la liquidité intrajournalière

## 1. Objet et finalité

Cette procédure vise à garantir la gestion efficace, sécurisée et en temps réel de la liquidité intrajournalière de Neo Financia, permettant d'assurer la disponibilité des fonds nécessaires aux opérations de paiement, de compensation, de règlement de titres et d’autres transactions critiques. Elle s'inscrit dans la gestion active des risques de liquidité en conformité avec les exigences de la BCE et de l’ACPR.

## 2. Champ d’application / Finance, Trésorerie & Reporting

Cette procédure couvre :

- Le suivi en temps réel des positions de trésorerie par compte de règlement
- La prévision et l’ajustement des flux de trésorerie dans la journée
- Les arbitrages de liquidité intrajournaliers entre comptes et devises
- La gestion des incidents de liquidité ou de blocage des flux
- L’interface avec les systèmes de paiement (TARGET2, SWIFT, SEPA, etc.)

## 3. Références réglementaires et normatives (REGS)

- EBA Guidelines on Internal Governance (EBA/GL/2021/05)
- LCR (Liquidity Coverage Ratio) et NSFR (Net Stable Funding Ratio) – CRR II
- Règlement UE n° 575/2013 – Bâle III
- ISO 20022 – format de messages de paiement
- Circulaire ACPR sur la gestion du risque de liquidité (2012-R-03)

## 4. Définitions & acronymes

- **LCR** : Liquidity Coverage Ratio  
- **NSFR** : Net Stable Funding Ratio  
- **BIC** : Bank Identifier Code  
- **CLS** : Continuous Linked Settlement  
- **Target2** : système de règlement brut en temps réel de la zone euro  
- **CUT-OFF** : heure limite de traitement d’un flux bancaire

## 5. Rôles et responsabilités (RACI)

| Activité                            | R (Responsable) | A (Accountable)         | C (Consulté)         | I (Informé)          |
|------------------------------------|------------------|--------------------------|----------------------|----------------------|
| Suivi intrajournalier des soldes   | Trésorier Front  | Responsable Trésorerie   | Risques, IT Paiements| Direction Financière |
| Arbitrage entre comptes devises    | Trésorier Front  | Responsable Trésorerie   | Back-Office Paiements| Contrôle Interne     |
| Escalade en cas de blocage         | Responsable Trésorerie | CFO                | Direction Générale   | Audit Interne        |

## 6. Prérequis / Entrées nécessaires

- Accès aux systèmes de paiements et outils de cash management
- Planning des flux sortants journaliers (salaires, virements clients, remboursements crédits…)
- Positions de trésorerie consolidées début de journée
- Calendrier des cut-offs réglementaires par devise/système

## 7. Étapes détaillées du workflow

### 7.1 Étape 1 : Pré-ouverture

- Collecte des soldes d’ouverture et des flux planifiés
- Revue des reports d’opérations de la veille (pending)
- Mise à jour du dashboard de suivi de liquidité

### 7.2 Étape 2 : Monitoring en journée

- Suivi intrajournalier toutes les 30 min via outils TMS
- Ajustement des positions par virements internes
- Réaffectation de liquidité entre comptes selon priorité (cut-off, taux…)

### 7.3 Étape 3 : Clôture de journée

- Vérification des soldes en fin de journée
- Traitement des écarts et des incidents
- Génération du rapport journalier de liquidité

### 7.4 Points de décision & contrôles qualité

- Point de décision : seuil minimal de liquidité atteint → arbitrage ou escalade
- Contrôles :
  - Matching flux prévus / réalisés
  - Contrôle post-journée sur mouvements non autorisés
  - Validation par second niveau (Contrôle Trésorerie)

## 8. Enregistrements produits / Evidences (logs, formulaires, rapports)

- Rapport de trésorerie intrajournalière (PDF journalier)
- Journal des virements internes de rééquilibrage
- Logs des actions de transfert manuels ou automatiques
- Alertes et notifications systèmes (email, SWIFT MT)

## 9. Indicateurs de performance & SLA (KPIs)

| Indicateur                                 | Objectif           |
|--------------------------------------------|--------------------|
| Respect des cut-offs règlementaires        | 100 %              |
| Taux de liquidité disponible à J           | ≥ 105 % des besoins|
| Nombre d’incidents de blocage flux         | 0 / mois           |
| Réactivité aux alertes système             | ≤ 15 min           |

## 10. Risques, points de vigilance & mesures de mitigation

- **Risque de rupture de liquidité**  
  *Mesure* : seuils d’alerte dynamique & automatisation des virements  
- **Risque d’erreur manuelle de transfert**  
  *Mesure* : double validation systématique  
- **Risque de dépassement de cut-off**  
  *Mesure* : cartographie et suivi proactif des heures limites

## 11. Systèmes / outils support & interfaces

- Outils de trésorerie (ex. Kyriba, Diapason, Sage XRT)
- Interfaces SWIFT MT & ISO 20022
- Tableau de bord intrajournalier (Power BI / Excel automatisé)
- Core Banking System (flux clients)
- Interface Target2 / SEPA / RTGS / CLS

## 12. Gestion des exceptions et escalade

- Escalade immédiate vers CFO si liquidité < seuil critique
- Notification au Risk Officer en cas de dépassement de seuil
- Procédure de back-up : intervention manuelle par le BO (avec signature)

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                  | Modifications clés                          |
|---------|------------|-------------------------|----------------------------------------------|
| 1.0     | 2025-05-28 | Trésorerie Groupe       | Création initiale de la procédure            |
| 1.1     | 2025-06-15 | Contrôle Interne        | Ajout du contrôle post-journée et audit logs |
