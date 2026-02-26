# Processus Opérationnel JML (Joiners ▸ Movers ▸ Leavers)

**Version :** 1.0
**Date d’entrée en vigueur :** 1 juillet 2025
**Propriétaire du document :** Responsable IAM

---

## 1. Objectif

Décrire pas‐à‐pas les activités, responsabilités, points de contrôle et enchaînements outillés permettant d’exécuter la Politique JML de Neo Financia. Le présent processus vise la reproductibilité, la traçabilité et l’automatisation maximale afin de :

* Réduire les délais d’activation ➜ < 3 jours ouvrés pour les Joiners ;
* Garantir la désactivation complète ➜ < 4 h pour les Leavers ;
* Permettre un suivi auditable et un reporting continu.

---

## 2. Références

* **Politique JML – Neo Financia** (cf. document de référence)
* Catalogue de rôles & matrice SoD v2.3
* Guide d’administration IAM SailPoint IdentityNow v2025

---

## 3. Aperçu du flux global

```
RH (SIRH) ──▶  Portail IAM  ──▶  SailPoint  ──▶  ServiceNow  ──▶  Systèmes cibles
      ⬑────────────────────────── Logs (Splunk) ────────────────────────────────⬏
```

* **RH** : point d’entrée unique (SIRH SuccessFactors)
* **Portail IAM** : formulaires dynamiques J/M/L + workflow BPMN
* **SailPoint IdentityNow** : gouvernance, provisioning API, recertifications
* **ServiceNow** : tickets matériels & tâches IT
* **Splunk** : journalisation centralisée, dashboards KPI

---

## 4. Processus détaillé

### 4.1 Joiners

| # | Responsable         | Système     | Délai SLA  | Description                                                                     |
| - | ------------------- | ----------- | ---------- | ------------------------------------------------------------------------------- |
| 1 | **RH**              | SIRH        | J‑5        | Création du collaborateur & date d’entrée.                                      |
| 2 | **Workflow IAM**    | SailPoint   | Instantané | Génère l’« EmployeeID » & déclenche le process « New Hire ».                    |
| 3 | **Manager**         | Portail IAM | J‑4        | Sélectionne le rôle métier (pack applicatif prédéfini) + fournit date de début. |
| 4 | **IAM**             | SailPoint   | J‑3        | Provisionne comptes AD, O365, VPN, CRM, Core Banking via connecteurs API.       |
| 5 | **IT Service Desk** | ServiceNow  | J‑2        | Prépare poste de travail, smartphone, YubiKey ; associe au collaborateur.       |
| 6 | **Collaborateur**   | O365        | Jour J     | Active MFA, change mot de passe initial.                                        |
| 7 | **Manager**         | Portail IAM | J+30       | Revues de conformité : validation ou retrait des droits dormants (>30 jours).   |

**Points de contrôle automatiques**

* Validation SoD en temps réel via règle « Access Risk » (SailPoint).
* Échec MFA ⇒ blocage de compte et alerte SOC.

---

### 4.2 Movers

| # | Responsable         | Système     | Délai SLA | Description                                                                      |
| - | ------------------- | ----------- | --------- | -------------------------------------------------------------------------------- |
| 1 | **Manager sortant** | Portail IAM | J‑7       | Initie workflow « Transfer » : sélection du collaborateur + date de bascule.     |
| 2 | **RH**              | SIRH        | J‑6       | Met à jour l’intitulé de poste et le service.                                    |
| 3 | **IAM**             | SailPoint   | J‑5       | Évaluation SoD ; provisioning automatique des nouveaux rôles.                    |
| 4 | **IAM**             | SailPoint   | J‑1       | Déprovisionne les rôles obsolètes ; maintient e‑mail et AD.                      |
| 5 | **Audit interne**   | Splunk      | J+15      | Vérifie qu’aucune transaction Core Banking n’a été réalisée avec anciens droits. |

---

### 4.3 Leavers

| # | Responsable            | Système    | SLA          | Description                                                                          |
| - | ---------------------- | ---------- | ------------ | ------------------------------------------------------------------------------------ |
| 1 | **RH**                 | SIRH       | Dès info     | Renseigne date de sortie.                                                            |
| 2 | **Interface SIRH→IAM** | SailPoint  | < 5 min      | Crée événement « Departure » et bascule statut à *Pré‑leaver*.                       |
| 3 | **IAM**                | SailPoint  | − J‑1 minuit | Planifie désactivation automatique des comptes à 00:00 (fusion fuseau Europe/Paris). |
| 4 | **IT Service Desk**    | ServiceNow | Jour J       | Collecte badge, laptop, mobile ; change statut CMDB en *Returned*.                   |
| 5 | **IAM**                | SailPoint  | < 4 h        | Désactivation effective : AD disabled, O365 blocked, tokens révoqués.                |
| 6 | **Backup Ops**         | Veeam      | J+7          | Archive home drive & boîte mail 6 ans (règlement ACPR).                              |
| 7 | **Audit interne**      | Splunk     | Trimestriel  | Revue échantillonnée des comptes désactivés ; traçage dans registre.                 |

---

## 5. Outils & intégrations

| Domaine | Outil                     | Nature de l’intégration                                              |
| ------- | ------------------------- | -------------------------------------------------------------------- |
| SIRH    | **SAP SuccessFactors**    | API OData ↔ SailPoint (EmployeeID, dates, manager)                   |
| IAM     | **SailPoint IdentityNow** | Connecteurs : AD, Azure AD, CoreBanking REST, Salesforce, ServiceNow |
| ITSM    | **ServiceNow**            | Tickets matériels & tâches IT auto‑créées par webhook SailPoint      |
| MFA     | **Azure MFA + YubiKey**   | Enforcement sur AD/AzureAD, Radius VPN, SAML SSO                     |
| SIEM    | **Splunk Enterprise**     | Collecte logs IAM, AD, VPN ; dashboards JML, alerting SOC            |

---

## 6. Matrice RACI (extraits clés)

| Activité               | RH | Manager | IAM | IT SD | CISO | Audit |
| ---------------------- | -- | ------- | --- | ----- | ---- | ----- |
| Créer profil Joiner    | R  | A       | I   | I     | I    | I     |
| Attribuer rôle métier  | I  | R/A     | C   | I     | I    | I     |
| Provisionner comptes   | I  | C       | R   | A     | I    | I     |
| Revue J+30             | I  | R/A     | C   | I     | I    | C     |
| Suspendre accès Leaver | I  | C       | R   | A     | I    | C     |
| Vérif. trimestrielle   | I  | I       | C   | I     | R    | A     |

Légende : **R** = Responsable (realise), **A** = Autorité (approuve), **C** = Consulté, **I** = Informé

---

## 7. KPI & Reporting

| Indicateur                     | Cible     | Calcul                                    | Tableau Splunk       |
| ------------------------------ | --------- | ----------------------------------------- | -------------------- |
| *Joiner TTA* (Time‑To‑Access)  | ≤ 3 jours | Date début ‑ Date création dernier compte | `joiner_tta`         |
| *Leaver TTD* (Time‑To‑Disable) | ≤ 4 h     | Date sortie RH ‑ Horodatage disable AD    | `leaver_ttd`         |
| % Comptes orphelins            | 0 %       | Comptes sans owner                        | `orphan_accounts`    |
| Taux revue d’accès             | ≥ 95 %    | utilisateurs validés / total              | `certification_rate` |

Dashboard Splunk actualisé **quotidiennement** et présenté au Comité Sécurité & Conformité chaque trimestre.

---

## 8. Templates & formulaires

* **Formulaire « New Hire »** (Portail IAM) – champs dynamiques basés sur rôle ; validation SoD en ligne.
* **Formulaire « Transfer »** – inclut ancienne et nouvelle unité, droits à retirer.
* **Formulaire « Off‑boarding »** – checklist matérielle, date fin d’accès, champ motif de départ.

Tous les templates sont stockés dans **Confluence ▸ Space « IAM » ▸ Templates**.

---

## 9. Exceptions & escalade

* Échec SLA désactivation : alerting mail + Slack #security‑alerts ; escalade T+30 min au CISO.
* Cas critique (risque fraude) : désactivation immédiate via script `emergency_disable.py`, *post‑mortem* dans 24 h.

---

## 10. Amélioration continue

* **Kaizen mensuel** : revue des incidents JML, actions d’amélioration automatisées (RPA, connectors).
* **Revue annuelle de capacité** : mise à l’échelle connecteurs, licences IdentityNow.

---

## 11. Historique

| Version | Date       | Auteur    | Modifications      |
| ------- | ---------- | --------- | ------------------ |
| 1.0     | 01/06/2025 | Resp. IAM | Création initiale. |
