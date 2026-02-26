# PROCÉDURE – analyse de solvabilité et de scoring interne

## 1. Objet et finalité

Cette procédure décrit précisément les étapes opérationnelles pour mener l'analyse de solvabilité et le scoring interne des clients sollicitant un crédit auprès de Neo Financia. Son objectif est de garantir une évaluation rigoureuse des risques de crédit, d’assurer la conformité réglementaire et de minimiser les pertes potentielles dues au défaut des emprunteurs.

## 2. Champ d’application / Opérations de Crédit

Cette procédure s’applique à :

* Tous les crédits à la consommation et immobiliers proposés par Neo Financia.
* L’ensemble des demandes initiées par des particuliers et des professionnels.
* Toutes les unités impliquées dans l’évaluation crédit à Paris, Lyon et Londres.

## 3. Références réglementaires et normatives (ACPR/EBA, RGPD, PSD2, ISO 9001/27001)

* ACPR/EBA : EBA/GL/2020/06 – Lignes directrices relatives à l'octroi et au suivi des prêts.
* RGPD (UE 2016/679) – Protection des données personnelles.
* PSD2 (UE 2015/2366) – Sécurité des paiements et authentification forte.
* ISO 9001 – Management de la qualité.
* ISO 27001 – Sécurité des systèmes d’information.

## 4. Définitions & acronymes

* **Solvabilité** : capacité d'un client à honorer ses engagements financiers.
* **Scoring interne** : méthode quantitative interne d’évaluation des risques de crédit.
* **KYC/KYB** : Connaissance du client particulier/professionnel.
* **ACPR/EBA** : Autorité de Contrôle Prudentiel et de Résolution/European Banking Authority.
* **RGPD** : Règlement Général sur la Protection des Données.
* **PSD2** : Directive sur les services de paiement.
* **CISO** : Chief Information Security Officer.

## 5. Rôles et responsabilités (RACI)

| Rôle                   | Responsable (R) | Acteur (A) | Consulté (C) | Informé (I) |
| ---------------------- | --------------- | ---------- | ------------ | ----------- |
| Responsable Crédit     | R               |            |              |             |
| Analyste Crédit        |                 | A          |              | I           |
| Responsable Conformité |                 |            | C            | I           |
| Responsable Risques    |                 | C          |              | I           |
| CISO                   |                 |            | C            | I           |

## 6. Prérequis / Entrées nécessaires

* Formulaire de demande de crédit complet (données financières et personnelles).
* Pièces justificatives (revenus, situation financière, pièces d'identité).
* Accès aux données externes (bases crédit externes, KYC).
* Système automatisé interne de scoring crédit.

## 7. Étapes détaillées du workflow

### 7.1 Étape 1 : Réception et vérification initiale des demandes

* Réception de la demande via plateforme digitale.
* Vérification automatique de la complétude et de la cohérence des données.
* Validation de la conformité RGPD/KYC.

### 7.2 Étape 2 : Scoring interne automatisé initial

* Lancement du scoring automatique :

  * Évaluation quantitative basée sur historique crédit.
  * Vérification du revenu et du taux d’endettement.
  * Attribution d'un score initial de solvabilité.

### 7.3 Étape 3 : Analyse approfondie manuelle (si nécessaire)

* Déclenchement si :

  * Score automatique inférieur au seuil requis.
  * Dossier identifié à risque élevé.
* Analyse complémentaire par Analyste Crédit :

  * Vérification manuelle des pièces justificatives.
  * Contact client éventuel pour clarifications.

### 7.4 Étape 4 : Décision finale et validation

* Validation automatique si critères remplis.
* Décision manuelle (Analyste Crédit ou Responsable Crédit) pour dossiers complexes.
* Documentation formelle de la décision dans le système GRC.

### 7.5 Étape 5 : Notification client et archivage

* Communication immédiate de la décision (digitale).
* Archivage sécurisé du dossier crédit et des preuves de décision.

### 7.3 Points de décision & contrôles qualité

* Validation automatique du scoring interne initial (système).
* Validation manuelle obligatoire des dossiers complexes par Responsable Crédit.
* Vérification trimestrielle de la conformité du scoring par Responsable Conformité.

## 8. Enregistrements produits / Évidences (logs, formulaires, rapports)

* Rapports automatisés de scoring initial.
* Formulaires d’analyse approfondie et décisions manuelles.
* Preuves d’archivage sécurisé des données client (GRC sécurisé).

## 9. Indicateurs de performance & SLA (KPIs)

| Indicateur                                 | Fréquence   | SLA         |
| ------------------------------------------ | ----------- | ----------- |
| Temps de traitement du scoring automatique | Mensuel     | ≤ 2 minutes |
| Temps de décision manuelle                 | Mensuel     | ≤ 48 heures |
| Taux de conformité des dossiers validés    | Trimestriel | 100 %       |
| Taux d’erreur dans les analyses manuelles  | Trimestriel | ≤ 2 %       |

## 10. Risques, points de vigilance & mesures de mitigation

| Risque/vigilance                    | Mesure de mitigation                       |
| ----------------------------------- | ------------------------------------------ |
| Risque de scoring erroné            | Vérification périodique et audits internes |
| Dépassement délai décision manuelle | Rappels automatisés et suivi quotidien     |
| Non-conformité réglementaire        | Formation continue, audits réguliers       |

## 11. Systèmes / outils support & interfaces

* Outil interne de scoring automatisé (modèle prédictif).
* Plateforme digitale d’onboarding crédit.
* Système GRC pour archivage sécurisé des dossiers.
* Bases externes (bureaux de crédit, bases KYC externes).

## 12. Gestion des exceptions et escalade

* Toute anomalie dans le scoring automatisé doit être immédiatement signalée au Responsable Crédit.
* En cas d’incapacité à prendre une décision dans les délais impartis, escalade obligatoire au Directeur des Risques.

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                   | Modification principale           |
| ------- | ---------- | ------------------------ | --------------------------------- |
| 1.0     | 28/05/2025 | Consultant Senior Crédit | Création initiale de la procédure |
| 1.1     |            |                          |                                   |
| 1.2     |            |                          |                                   |
