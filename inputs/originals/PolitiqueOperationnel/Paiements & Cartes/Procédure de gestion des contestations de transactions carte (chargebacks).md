# PROCÉDURE – gestion des contestations de transactions carte (chargebacks)

## 1. Objet et finalité

Cette procédure opérationnelle décrit de manière détaillée les étapes à suivre pour traiter les contestations de transactions carte (chargebacks) initiées par les clients de Neo Financia. Elle a pour objectif de garantir une gestion efficace, conforme aux exigences des réseaux internationaux (Visa, Mastercard), en assurant la protection des droits du client et la maîtrise des risques financiers et opérationnels.

## 2. Champ d’application / Paiements & Cartes

La procédure s’applique à :

* Toutes les transactions carte initiées via Visa ou Mastercard (paiements en ligne, en point de vente, retraits DAB).
* Tous les motifs de contestation couverts par les règles interbancaires (fraude, non-réception de bien, double débit, etc.).
* L’ensemble des collaborateurs impliqués dans la gestion des réclamations et litiges de paiements carte.

## 3. Références réglementaires et normatives (ACPR/EBA, RGPD, PSD2, ISO 9001/27001)

* **ACPR/EBA** : Lignes directrices EBA/GL/2022/06 sur les droits des utilisateurs de services de paiement.
* **PSD2** (Directive UE 2015/2366) : Droit au remboursement des opérations non autorisées.
* **RGPD** (Règlement UE 2016/679) : Confidentialité et sécurité des données du porteur.
* **ISO 9001** : Qualité du traitement client.
* **ISO 27001** : Sécurité des informations et traçabilité.

## 4. Définitions & acronymes

* **Chargeback** : procédure de rétrofacturation d'une transaction contestée.
* **Acquéreur** : établissement traitant le paiement pour le commerçant.
* **Émetteur** : établissement bancaire du porteur de carte (Neo Financia).
* **ARN** : Acquirer Reference Number (identifiant unique de transaction).
* **SCA** : Strong Customer Authentication (authentification forte – PSD2).

## 5. Rôles et responsabilités (RACI)

| Rôle                                 | Responsable (R) | Acteur (A) | Consulté (C) | Informé (I) |
| ------------------------------------ | --------------- | ---------- | ------------ | ----------- |
| Responsable Paiements                | R               |            |              |             |
| Analyste Réclamations Carte          |                 | A          |              |             |
| Responsable Conformité               |                 | C          |              | I           |
| Service Client                       |                 | A          |              | I           |
| Partenaires réseau (Visa/Mastercard) |                 |            | C            | I           |

## 6. Prérequis / Entrées nécessaires

* Déclaration de contestation client via l’application ou formulaire web.
* Informations sur la transaction : montant, date, commerçant, motif.
* Documents justificatifs (ex : accusé de non-livraison, ticket DAB, échanges avec commerçant).
* Historique de transaction carte (ARN, SCA, logs).

## 7. Étapes détaillées du workflow

### 7.1 Étape 1 : Réception et enregistrement de la contestation

* Le client initie une réclamation via l’espace personnel ou par contact service client.
* Vérification de la complétude des informations fournies.
* Attribution d’un numéro de dossier et enregistrement dans le système GRC.

### 7.2 Étape 2 : Analyse préliminaire et classification du litige

* Vérification de la transaction : authentification, autorisation, duplication, contexte du paiement.
* Classement dans la catégorie correspondante selon les règles réseau (fraude, non-livraison, etc.).
* Déclenchement de la procédure de chargeback si fondé, sinon notification de rejet au client avec justification.

### 7.3 Étape 3 : Initiation du chargeback (via réseau)

* Saisie du cas dans l’interface réseau (Visa Resolve Online, Mastercard Dispute Management).
* Transmission des pièces justificatives requises.
* Suivi du retour acquéreur (acceptation, rejet, representment).

### 7.4 Étape 4 : Clôture et notification client

* Clôture du dossier selon le statut final : remboursé, rejeté ou arbitrage.
* Notification au client via email ou messagerie sécurisée.
* Archivage du dossier avec toutes les preuves et communications.

### 7.5 Points de décision & contrôles qualité

* Vérification manuelle obligatoire avant lancement d’un chargeback.
* Contrôle automatique de respect des délais imposés (Visa : 120 jours max. selon motif).
* Validation finale de clôture du dossier par le Responsable Paiements.

## 8. Enregistrements produits / Evidences (logs, formulaires, rapports)

* Dossier client (formulaire, motif, documents justificatifs).
* Logs système (SCA, autorisation, consultation ARN).
* Suivi du litige dans l’interface réseau (statuts, décisions).
* Rapport interne mensuel (nombre, taux de succès, délais).

## 9. Indicateurs de performance & SLA (KPIs)

| Indicateur                                    | Fréquence     | SLA                    |
| --------------------------------------------- | ------------- | ---------------------- |
| Délai moyen de première réponse client        | Hebdomadaire  | ≤ 2 jours ouvrés       |
| Délai de traitement complet (hors arbitrage)  | Mensuelle     | ≤ 30 jours calendaires |
| Taux de contestations acceptées (chargebacks) | Mensuelle     | ≥ 75 %                 |
| Taux de dossiers clos dans les délais Visa/MC | Trimestrielle | 100 %                  |

## 10. Risques, points de vigilance & mesures de mitigation

| Risque identifié                                        | Mesure de mitigation                                 |
| ------------------------------------------------------- | ---------------------------------------------------- |
| Perte financière par retard de procédure                | Suivi automatisé des délais, alertes système         |
| Faux positifs (fraude non avérée)                       | Double vérification manuelle, scoring comportemental |
| Représentations non justifiées (representments abusifs) | Documentation rigoureuse et recours à l’arbitrage    |

## 11. Systèmes / outils support & interfaces

* Plateforme GRC interne (gestion des litiges)
* Interfaces réseau Visa / Mastercard (VROL, MDD)
* Base de données transactionnelles (ARN, logs SCA)
* Outil d’authentification (SCA, biométrie)
* Système de messagerie client sécurisée

## 12. Gestion des exceptions et escalade

* En cas de dossier complexe (cas multi-transactions, litige frontalier) : escalade au Responsable Paiements.
* En cas de rejet client sur décision finale : possibilité de recours via arbitrage réseau (Visa/Mastercard).
* Exception réglementaire ou fraude grave : signalement à la Conformité pour traitement spécifique.

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                      | Modification principale           |
| ------- | ---------- | --------------------------- | --------------------------------- |
| 1.0     | 28/05/2025 | Consultant Senior Paiements | Création initiale de la procédure |
| 1.1     |            |                             |                                   |
| 1.2     |            |                             |                                   |
