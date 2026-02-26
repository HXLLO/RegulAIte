# Procédure Opérationnelle – Traitement des Demandes d’Exercice de Droits (DSAR)

**Version :** 1.0
**Date d’application :** 1 août 2025
**Propriétaire :** Data Protection Officer (DPO)

---

## 1. Objectif

Assurer un traitement **rapide, cohérent et conforme** des demandes d’exercice de droits prévues par les articles 12 à 22 du RGPD :

* Droit d’accès, de rectification, d’effacement, de limitation, d’opposition, de portabilité et décision automatisée ;
* Respect des délais (≤ 1 mois, extensible de 2 mois) ;
* Documentation probante pour démontrer la conformité (Accountability).

---

## 2. Portée

* Toutes les demandes émanant de : clients, prospects, employés, ex‑employés et partenaires de Neo Financia ;
* Tous canaux : portail « **Mon Espace Données** », e‑mail [dpo@neofinancia.com](mailto:dpo@neofinancia.com), courrier postal, réseaux sociaux ;
* Tous environnements contenant des données personnelles (Core Banking, CRM, HRIS, logs web, data lake…).

---

## 3. Gouvernance & rôles

| Rôle                     | Responsabilités                                                              |
| ------------------------ | ---------------------------------------------------------------------------- |
| **DPO (Owner)**          | Qualifie la demande, suit le SLA, valide la réponse finale.                  |
| **ServiceNow RGPD Desk** | Point d’entrée, enregistre la demande, accuse réception.                     |
| **Identity Owner**       | Fournit les données pour un système donné (ex. Responsable CRM).             |
| **Legal**                | Revue juridique, exemptions (art. 23), clause bancaire secret professionnel. |
| **CISO**                 | Vérifie redaction / pseudonymisation, supervise sécurisation transfert.      |
| **IT Ops (Data Export)** | Extrait données structurées (SQL, API) selon format JSON/CSV.                |
| **Com Dir**              | Communication avec personne concernée si vocabulaire sensible.               |

---

## 4. Canaux et authentification

| Canal                              | Mode d’authentification requis                                          |
| ---------------------------------- | ----------------------------------------------------------------------- |
| Portail web « Mon Espace Données » | Connexion SCA mobile + OTP SMS                                          |
| E‑mail                             | Copie pièce d’identité + selfie + dernière transaction de référence     |
| Courrier postal                    | Copie ID certifiée conforme ou accusé AR à adresse du contrat           |
| Téléphone / réseaux sociaux        | Redirection vers portail / e‑mail (pas de données divulguées oralement) |

---

## 5. Typologie des demandes & SLA internes

| Type droit                   | Délai légal | SLA Neo Financia |
| ---------------------------- | ----------- | ---------------- |
| Accès                        | 1 mois      | 25 jours         |
| Rectification                | 1 mois      | 20 jours         |
| Effacement (droit à l’oubli) | 1 mois      | 25 jours         |
| Portabilité                  | 1 mois      | 20 jours         |
| Opposition marketing         | Immédiat    | 24 h             |
| Limitation                   | 1 mois      | 15 jours         |

Extension possible **+ 2 mois** justifiée (complexité / nombre de demandes) — notification avant jour 30.

---

## 6. Flux opérationnel détaillé

| #  | Étape                                                                     | Responsable          | Délai  |
| -- | ------------------------------------------------------------------------- | -------------------- | ------ |
| 1  | Réception & enregistrement (ticket **DSAR‑###** dans ServiceNow)          | RGPD Desk            | < 4 h  |
| 2  | Accusé de réception à la personne                                         | RGPD Desk            | 24 h   |
| 3  | Vérification identité (KYC light)                                         | DPO                  | 3 j    |
| 4  | Qualification droit + périmètre                                           | DPO                  | 3 j    |
| 5  | Sous‑tâches « Data Collection » créées par système                        | DPO                  | 4 j    |
| 6  | Extraction & dépôt dans dossier SharePoint / Sec. Files                   | Identity Owners / IT | 14 j   |
| 7  | Redaction / pseudonymisation (si tiers)                                   | CISO + Legal         | 18 j   |
| 8  | Compilation réponses + export machine‑lisible (JSON/CSV) et lisible (PDF) | RGPD Desk            | 22 j   |
| 9  | Validation finale DPO                                                     | DPO                  | 24 j   |
| 10 | Envoi sécurisé (S/MIME mail ou portail)                                   | RGPD Desk            | ≤ 25 j |
| 11 | Clôture ticket & archivage                                                | RGPD Desk            | ≤ 30 j |

### Extension > 30 jours

* DPO met à jour ticket, envoie notification à la personne (motif + nouvelle échéance) avant **Jour 28**.

---

## 7. Extraction & format des données

* **Structurées** : exports CSV/JSON, séparateur ; ; charset UTF‑8.
* **Non structurées** : recherche mot‑clé dans SharePoint/Azure Blob via Azure Cognitive Search.
* **E‑mails** : export PST filtré ID collaborateur.
* **Fichiers volumineux** > 200 Mo : lien de téléchargement sécurisé (OneDrive — expiration 30 j).

---

## 8. Redaction & sécurité

* Champs à masquer : secrets commerciaux, données tierces, notes internes subjectives.
* Outil **Axiomatics PDF Redactor** — script batch `redact-dsar.ps1`.
* Fichier final chiffré AES‑256, transmis via portail web (TLS 1.3) ou e‑mail S/MIME.

---

## 9. Journalisation & conservation

| Enregistrement                | Durée   | Emplacement                        |
| ----------------------------- | ------- | ---------------------------------- |
| Tickets ServiceNow DSAR       | 6 ans   | ServiceNow EU DC                   |
| Preuve identité               | 15 mois | Dossier crypté SharePoint « DSAR » |
| Exports fournis               | 6 ans   | Azure Blob WORM                    |
| Log actions (who, when, what) | 6 ans   | Splunk index `dsar_audit`          |

---

## 10. Supervision & KPI

| KPI                        | Cible  | Source               |
| -------------------------- | ------ | -------------------- |
| DSAR on‑time delivery      | ≥ 95 % | ServiceNow reports   |
| Time‑to‑Ack                | ≤ 24 h | Splunk SLA dashboard |
| Requests needing extension | < 10 % | ServiceNow           |
| DSAR backlog > 30 d        | 0      | ServiceNow           |

Tableau de bord **PowerBI DSAR** présenté trimestriellement au Comité Conformité.

---

## 11. RACI

| Activité           | DPO | RGPD Desk | Identity Owner | IT Ops | Legal | CISO |
| ------------------ | --- | --------- | -------------- | ------ | ----- | ---- |
| Enregistrement     | A   | R         | I              | I      | I     | I    |
| Vérif. identité    | R   | C         | I              | I      | C     | I    |
| Extraction données | C   | I         | R              | R      | I     | I    |
| Redaction          | C   | I         | I              | I      | R     | R    |
| Validation & envoi | R   | C         | I              | I      | C     | C    |
| Archivage          | A   | R         | I              | I      | I     | I    |

---

## 12. Formation & tests

* Formation « DSAR handling » obligatoire pour RGPD Desk & Identity Owners (LMS) chaque année.
* **Test de demande mystère** trimestriel (simulation) — score de conformité > 90 %.
* Retex partagé lors du **Privacy Stand‑Up** mensuel.

---

## 13. Procédure de changement

Toute mise à jour (outil, délai, format) soumise à :

1. PR dans GitLab ;
2. Revue DPO + CISO ;
3. Publication Confluence, notification Slack #privacy‑news.

---

## 14. Historique des versions

| Version | Date       | Auteur | Commentaire        |
| ------- | ---------- | ------ | ------------------ |
| 1.0     | 01/06/2025 | DPO    | Création initiale. |
