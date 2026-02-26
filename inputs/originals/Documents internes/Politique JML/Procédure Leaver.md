# Procédure « Leaver » – Départ d’un collaborateur

**Version :** 1.0
**Date d’application :** 1 juillet 2025
**Propriétaire du document :** Responsable IAM

---

## 1. Objectif

Garantir la désactivation rapide des accès, la restitution complète des actifs et l’archivage réglementaire lors du **départ** (volontaire ou involontaire) d’un collaborateur ou prestataire, afin de minimiser les risques de sécurité et de se conformer aux exigences ACPR, PSD2 et GDPR.

---

## 2. Périmètre

* Tous les employés, stagiaires, alternants et prestataires quittant Neo Financia.
* Départs planifiés (préavis) ou immédiats (licenciement, prestation terminée).
* Sites : Paris, Lyon, Londres, télétravail.
* Systèmes : Active Directory/Azure AD, O365, Core Banking, SAP FI, Salesforce, GitLab, VPN, ServiceNow, badge physique.

---

## 3. Chronologie & SLA

### 3.1 Départ planifié

| Jours ouvrés relatifs   | Étape clé                                         | Responsable/Outil       |
| ----------------------- | ------------------------------------------------- | ----------------------- |
| **T‑5**                 | Notification de départ dans SIRH                  | **RH – SuccessFactors** |
| **T‑4**                 | Validation date et type de départ                 | **Manager + RH**        |
| **T‑3**                 | Plan Off‑boarding + transfert connaissances       | **Manager**             |
| **T‑1 minuit**          | Planification désactivation comptes               | **IAM – SailPoint**     |
| **Jour T (avant 12 h)** | Restitution matériel + disable comptes            | **IAM + ITSD**          |
| **T+7**                 | Archivage données, suppression définitive comptes | **IAM + Backup**        |
| **T+30**                | Audit post‑départ                                 | **Audit interne**       |

### 3.2 Départ immédiat (urgence)

* **H0** – RH ou Manager déclenche « Emergency Leaver » dans Portail IAM.
* **< 15 min** – IAM exécute script *emergency\_disable.py* : blocage AD, O365, VPN, tokens.
* **< 1 h** – ITSD récupère badge, laptop, mobile (accompagné Sûreté).
* Suite du processus comme départ planifié (archivage, audit).

> **SLA clé** : **Time‑To‑Disable ≤ 4 h** après heure officielle de sortie.

---

## 4. Procédure détaillée (départ planifié)

### 4.1 Notification & préparation (T‑5 à T‑3)

1. **RH** saisit la **Date Fin Contrat** dans SuccessFactors, champ *terminationType* (Resignation, End of Contract, Termination).
2. L’ETL RH→SailPoint crée statut **Pre‑Leaver** et envoie e‑mail au Manager et IAM.
3. **Manager** complète dans Portail IAM :

   * Checklist connaissances à transférer.
   * Liste applications critiques à **désactiver** ou **déléguer**.
4. **ServiceNow** crée tickets : *Asset Return*, *Badge Deactivation*, *Mail Forwarding* (optionnel).

### 4.2 Désactivation (T‑1 minuit)

1. **SailPoint** programme événement *DisableAccounts* pour 00 h 00 fuseau Europe/Paris le jour T.
2. Connecteurs appliquent :

   * AD/Azure AD : `userAccountControl=514`, licence O365 retirée.
   * Core Banking : `status=locked`.
   * GitLab : `external=false`, `state=blocked`.
   * VPN : certificat révoqué via Radius.
3. **SOC (Splunk)** reçoit alerte de confirmation désactivation.

### 4.3 Restitution des actifs (Jour T)

1. **Collaborateur** remet laptop, smartphone, YubiKey, badge à **ITSD** (ou livraison DHL si télétravail).
2. **ITSD** vérifie état matériel, met à jour CMDB ≥ *Returned/To Wipe*.
3. **Sûreté** désactive badge physique (Contrôle d’accès).

### 4.4 Archivage & suppression (T+7)

1. **Backup Ops (Veeam)** archive home drive & mailbox **6 ans** (exigence ACPR).
2. **IAM** exécute job *DeleteDisabledAccountsOlderThan30Days*.
3. Logs SailPoint/Splunk conservés **5 ans**.

### 4.5 Audit post‑départ (T+30)

1. **Audit interne** prélève échantillon (≥ 10 %) des leavers du mois ; vérifie :

   * Tous comptes désactivés.
   * Restitution 100 % actifs.
   * Aucun accès initié après date départ.
2. Non‑conformité ➜ plan d’action et rapport au Comité Sécurité & Conformité.

---

## 5. Checklists par acteur

### 5.1 Ressources Humaines

* [ ] Saisir date et type de départ dans SuccessFactors.
* [ ] Créer notification Portail IAM *Leaver*.
* [ ] Organiser entretien de départ & questionnaire.
* [ ] Informer Paie, Avantages sociaux, Mutuelle.
* [ ] Générer certificat de travail et reçu solde de tout compte.

### 5.2 Manager

* [ ] Valider date de sortie & last working day.
* [ ] Identifier données à transférer (projets, dossiers).
* [ ] Nommer repreneur (delegate) dans systèmes (SharePoint, Jira).
* [ ] Confirmer restitution des actifs auprès ITSD.
* [ ] Supprimer délégations mail/calendrier.

### 5.3 Équipe IAM

* [ ] Vérifier réception événement Pre‑Leaver.
* [ ] Planifier disable comptes à 00 h 00 jour T.
* [ ] Exécuter script *emergency\_disable* si demande urgente.
* [ ] Lancer suppression définitive à T+30.
* [ ] Générer rapport *Leaver Completion*.

### 5.4 IT Service Desk

* [ ] Générer ticket *Asset Return* lié EmployeeID.
* [ ] Collecter laptop, smartphone, YubiKey, badge.
* [ ] Mettre à jour statut CMDB.
* [ ] Wipe sécurisé des appareils (Intune, Mobile Iron) avant réaffectation.
* [ ] Archiver fiche de contrôle matériel signée.

### 5.5 Sécurité Opérationnelle (SOC)

* [ ] Surveiller toute tentative de connexion après désactivation.
* [ ] En cas d’alerte, escalader au CISO.

### 5.6 Collaborateur (si départ volontaire)

* [ ] Finaliser tâches en cours, documenter projets.
* [ ] Sauvegarder documents personnels depuis O365.
* [ ] Restituer tout matériel avant 12 h Jour T.
* [ ] Signer accusé de réception solde de tout compte.

---

## 6. Contrôles & KPI

| Contrôle automatisé                         | Outil       | Fréquence  | Seuil d’alerte       |
| ------------------------------------------- | ----------- | ---------- | -------------------- |
| Désactivation comptes à H+4                 | Splunk      | Temps réel | >4 h = Rouge         |
| Comptes désactivés mais non supprimés >30 j | SailPoint   | Quotidien  | Alerte SOC           |
| % Restitution actifs                        | ServiceNow  | Hebdo      | <100 % = Alerte ITSD |
| KPI *Leaver TTD* (Time‑To‑Disable)          | Splunk Dash | Quotidien  | >4 h = Rouge         |

---

## 7. Escalade

* **SLA TTD** non respecté ➜ Slack #jml‑escalation + e‑mail CISO.
* Actif non restitué >48 h ➜ Responsable Sécurité Physique.
* Tentative connexion après disable ➜ Incident sécurité, procédure IR‑001.

---

## 8. Références & modèles

* Template *Off‑boarding* (Portail IAM) – Confluence ▶ IAM ▶ Templates.
* Politique JML v1.0.
* Procédure Incident Response IR‑001 (tentative connexion).
* Guide SailPoint – chapitre *Disable Identity*.

---

## 9. Historique des versions

| Version | Date       | Auteur    | Commentaire        |
| ------- | ---------- | --------- | ------------------ |
| 1.0     | 01/06/2025 | Resp. IAM | Création initiale. |
