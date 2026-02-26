# Procédure Opérationnelle – Notification des Violations de Données à Caractère Personnel

**Version :** 1.0
**Date d’application :** 1 août 2025
**Propriétaire :** Data Protection Officer (DPO)

---

## 1. Objectif

Définir les étapes précises permettant de :

* détecter, qualifier et documenter toute **violation de données** (Art. 4‑12 RGPD) ;
* notifier l’autorité de contrôle (CNIL) **dans les 72 heures** (Art. 33) ;
* informer les personnes concernées **sans délai excessif** lorsque le risque est élevé (Art. 34) ;
* garantir la traçabilité et l’amélioration continue de la sécurité des traitements.

---

## 2. Portée

* Tous traitements et systèmes contenant des données à caractère personnel exploités par Neo Financia (on‑prem, Cloud, SaaS).
* Incidents internes, externes, malveillants ou accidentels, incluant : divulgation, destruction, perte, altération, accès non autorisé.

---

## 3. Gouvernance & rôles clés

| Rôle                                              | Responsabilités                                                                                   |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Détecteur initial** (SOC, Employé, Fournisseur) | Signale immédiatement via le portail Incident Jira – catégorie **P1‑Security**.                   |
| **SOC**                                           | Analyse, classe la gravité (S0‑S3), collecte journaux.                                            |
| **Incident Manager (IM)**                         | Coordonne la réponse, convoque la cellule de crise.                                               |
| **DPO**                                           | Évalue l’impact RGPD, décide notification CNIL & personnes, rédige le formulaire **CNIL‑Breach**. |
| **CISO**                                          | Définit mesures correctives techniques, valide le rapport post‑mortem.                            |
| **Com Dir**                                       | Prépare messages externes/interne si notification publique.                                       |
| **Juriste**                                       | Vérifie obligations contractuelles (clients, assureur).                                           |

---

## 4. Classification des incidents

| Niveau | Définition                                                  | Délai interne max pour escalade DPO |
| ------ | ----------------------------------------------------------- | ----------------------------------- |
| **S0** | Violation confirmée, données sensibles ou >10 000 personnes | 1 h                                 |
| **S1** | Violation confirmée, impact limité (<10 000 pers.)          | 2 h                                 |
| **S2** | Suspicion raisonnable, investigation en cours               | 4 h                                 |
| **S3** | Fausse alerte ou aucun DP détecté                           | Clôture sans notification           |

---

## 5. Chronologie cible (S0/S1)

| T0               | Détection / signalement (portail Jira, hotline SOC)                    |
| ---------------- | ---------------------------------------------------------------------- |
| **T0 + 30 min**  | SOC qualifie l’incident, informe Incident Manager                      |
| **T0 + 1 h**     | IM déclenche **Cellule de crise privacy** (DPO, CISO, Juriste, ComDir) |
| **T0 + 4 h**     | Décision : obligation de notification ?  🔄 Oui / Non                  |
| **T0 + 48 h**    | Collecte faits, preuves, mesures ; brouillon formulaire CNIL           |
| **T0 + 72 h**    | Soumission notification CNIL (portail CNIL)                            |
| **T0 + 72‑96 h** | Notification personnes concernées (si risque élevé)                    |
| **T0 + 14 j**    | Rapport post‑mortem & plan d’actions préventives                       |

---

## 6. Étapes opérationnelles

### 6.1 Détection & consignation

1. **Portail Jira** : création ticket *SEC‑Breach* avec champ obligatoire *type de données*.
2. SOC annexe logs Splunk, captures, horodatage UTC et fuseau Europe/Paris.

### 6.2 Containment & analyse

1. IM ordonne `isolate_system` (firewall, disable account, revoke token).
2. SOC effectue **triage** : vecteur, étendue, catégorie DP (art. 9, art. 10).
3. **Evidence Locker** : fichiers `.pcap`, dumps, journaux chiffrés, hashés SHA‑256.

### 6.3 Évaluation du risque (DPO)

* Utilise matrice **Impact × Probabilité** :
  \| Impact | Exemples |
  \|--------|----------|
  \| Élevé | Données bancaires + identité, biométrie |
  \| Moyen | Nom + email |
  \| Faible | Données pseudonymisées |
* Critères CNIL : nature, volume, facilité d’identification, gravité conséquences.

### 6.4 Décision de notification

* **Notification CNIL obligatoire** si atteinte à la confidentialité/intégrité/ disponib. impactant DP **et** risque pour droits/libertés.
* **Notification personnes** si risque **élevé** ; peut être différée si crypto parfaite ou mesures ultérieures suffisent.

### 6.5 Préparation dossier CNIL

1. DPO remplit template **CNIL‑Breach‑V3** (titre, DPO, catégorie données, nb enregistrements, mesures correctives, point de contact).
2. Validation juridique (relecture) + approbation CISO.
3. Dépôt via portail CNIL ; réception **ID‑Breach #** archivée.

### 6.6 Notification des personnes

1. Com Dir prépare message clair : nature de la violation, conseils (ex. changer mdp), contact hotline.
2. Moyen utilisé : e‑mail individuel + bannière in‑app ; logs SendGrid conservés.

### 6.7 Post‑incident & leçons apprises

1. **Post‑mortem RCFA** (Root Cause & Follow‑up Analysis) sous 14 j.
2. Actions correctives entrées dans **Jira – Project SEC‑IMPR** ; propriétaire et échéance.
3. Audit interne vérifie clôture actions ≤ 90 j.

---

## 7. Journalisation & preuve

| Artefact                       | Emplacement            | Rétention |
| ------------------------------ | ---------------------- | --------- |
| Ticket Jira SEC‑Breach         | Jira Cloud             | 10 ans    |
| Formulaire CNIL                | SharePoint Compliance  | 10 ans    |
| Evidence Locker                | S3 IronMountain (WORM) | 10 ans    |
| Logs Splunk index `incident_*` | Splunk                 | 5 ans     |

---

## 8. RACI

| Activité                   | Détecteur | SOC | IM | DPO     | CISO | Juriste | ComDir |
| -------------------------- | --------- | --- | -- | ------- | ---- | ------- | ------ |
| Création ticket            | R         | I   | I  | I       | I    | I       | I      |
| Qualification              | I         | R   | C  | C       | C    | I       | I      |
| Décision notification CNIL | I         | C   | C  | **A/R** | C    | C       | I      |
| Notification CNIL          | I         | I   | C  | **R**   | C    | A       | I      |
| Notification personnes     | I         | I   | C  | **A**   | C    | C       | **R**  |
| Rapport post‑mortem        | I         | C   | R  | A       | A    | I       | I      |

---

## 9. KPI & monitoring

| KPI                           | Cible  | Source                |
| ----------------------------- | ------ | --------------------- |
| **Time‑to‑Detect** (avg)      | <2 h   | Splunk MTTD dashboard |
| **Time‑to‑Notify CNIL**       | ≤ 72 h | Jira SLA tracker      |
| **P0 Breaches/an**            | 0      | Incident registry     |
| **Actions correctives <90 j** | 100 %  | Jira follow‑up        |

---

## 10. Formation & tests

* **Table‑top exercise** « GDPR Breach » organisé 2×/an (sec‑ops, DPO, Com).
* Formation « RGPD Incident Response » obligatoire pour SOC et IM (LMS).
* Test d’alerte PagerDuty simulé chaque trimestre.

---

## 11. Procédure de changement

Toute mise à jour de la procédure ou du template CNIL doit être approuvée par le DPO et le CISO et publiée sur Confluence (E‑signature).

---

## 12. Historique des versions

| Version | Date       | Auteur     | Commentaire        |
| ------- | ---------- | ---------- | ------------------ |
| 1.0     | 01/06/2025 | DPO & CISO | Création initiale. |
