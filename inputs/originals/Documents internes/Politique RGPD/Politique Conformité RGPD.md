# Politique Conformité RGPD – Neo Financia

**Version :** 1.0
**Date d’entrée en vigueur :** 1 août 2025
**Propriétaire du document :** Data Protection Officer (DPO)
**Périmètre :** Ensemble des sites et applications web/mobile exploités par Neo Financia, y compris les environnements de test et de pré‑production.

---

## 1. Objectif

Assurer la conformité de Neo Financia au **Règlement (UE) 2016/679 (RGPD)** et aux lignes directrices de la CNIL, en définissant les principes, rôles et procédures applicables :

* à la **conservation et la suppression** des données à caractère personnel ;
* aux **conditions de recueil, gestion et retrait du consentement** ;
* plus largement, à la mise en œuvre des droits des personnes concernées et aux obligations de documentation.

---

## 2. Gouvernance & responsabilités

| Rôle                         | Responsabilités clés                                                                      |
| ---------------------------- | ----------------------------------------------------------------------------------------- |
| **Conseil d’administration** | Supervise la stratégie de conformité et approuve la présente politique.                   |
| **DPO**                      | Pilote la conformité RGPD, tient le registre des traitements, instruit les demandes RGPD. |
| **CISO**                     | Met en œuvre les mesures de sécurité techniques & organisationnelles.                     |
| **Service Juridique**        | Revue contractuelle, clauses de protection des données, transfert hors UE.                |
| **Marketing Digital**        | Configure les outils de suivi, gère la plate‑forme de consentement (CMP).                 |
| **Départements IT & Dev**    | Implémentent privacy‑by‑design, effacement logique/physique et logs.                      |
| **Support Client**           | Traite les demandes d’exercice de droits via ServiceNow RGPD.                             |

---

## 3. Principes généraux (Art. 5 RGPD)

1. **Licéité, loyauté, transparence**
2. **Limitation des finalités**
3. **Minimisation des données**
4. **Exactitude**
5. **Limitation de la conservation**
6. **Intégrité et confidentialité**
7. **Responsabilité (Accountability)**

Ces principes sont inscrits dans le cycle de vie de tout nouveau projet via le **processus Privacy by Design** (formulaire PIA‑001).

---

## 4. Politique de conservation & suppression des données

### 4.1 Tableau des durées de conservation

| Catégorie de données    | Finalité                     | Base légale            | Durée active                | Durée d’archivage    | Référence réglementaire  |
| ----------------------- | ---------------------------- | ---------------------- | --------------------------- | -------------------- | ------------------------ |
| KYC & pièces d’identité | Lutte anti‑blanchiment (AML) | Obligation légale      | Relation + 5 ans            | +5 ans (coffre‑fort) | Art. L561‑12 CMF         |
| Transactions bancaires  | Exécution du contrat         | Exécution d’un contrat | Relation + 10 ans           | —                    | Art. L123‑22 CCom        |
| Logs d’accès web        | Sécurité, détection fraude   | Intérêt légitime       | 12 mois                     | —                    | Recommandation CNIL 2021 |
| Cookies analytiques     | Mesure d’audience            | Consentement           | 13 mois max                 | —                    | Délib. CNIL 2020‑092     |
| Prospection e‑mail      | Marketing                    | Consentement           | 3 ans après dernier contact | —                    | Recommandation CNIL 2016 |
| Tickets support         | Service clientèle            | Intérêt légitime       | 5 ans                       | —                    | Prescription civile      |
| Enregistrements chat    | Amélioration qualité         | Intérêt légitime       | 24 mois                     | —                    | Recommandation CNIL 2022 |

### 4.2 Règles d’effacement automatisé

* Une **tâche quotidienne** (job `gdpr_purge.py`) exécute la suppression logique des enregistrements dont la date d’échéance est atteinte.
* Les sauvegardes chiffrées sont conservées 30 jours ; l’effacement définitif intervient lors de la rotation.

### 4.3 Conservation différenciée pour litiges ou obligations légales

* En cas de contentieux, la mise en **hold légal** est ordonnée par le Juridique via ticket *LegalHold* ; l’effacement est suspendu jusqu’à levée.

---

## 5. Politique de consentement (Art. 4‑11 & 7 RGPD)

### 5.1 Conditions de validité du consentement

1. **Libre :** aucun service essentiel n’est conditionné à l’acceptation des cookies non nécessaires.
2. **Spécifique :** granularité par finalité (analytics, pub personnalisée, réseaux sociaux).
3. **Éclairé :** bandeau CMP affiche description claire, lien vers Politique Cookies.
4. **Univoque :** case à cocher vierge ou action positive (cliquer « Accepter »).
5. **Rétractable :** possibilité de retirer le consentement **aussi facilement** que de le donner via centre de préférences.

### 5.2 Plate‑forme de gestion du consentement (CMP)

| Exigence               | Implémentation                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------- |
| IAB TCF v2.2           | CMP certifiée (Didomi) configurée en mode « opt‑in explicite ».                    |
| Preuve du consentement | Hash unique stocké (TTL 3 ans) dans table `consent_log`, horodatage + version CMP. |
| Synchronisation        | ConsentString transmise dans Google Tag Manager, Facebook CAPI, etc.               |
| Auditabilité           | Exports mensuels CSV des consentements conservés 6 ans.                            |

### 5.3 Double opt‑in marketing

* Toute inscription à la newsletter déclenche un e‑mail de confirmation ; l’adresse n’est activée qu’après clic sur le lien (preuve d’opt‑in conservée dans table `newsletter_consent`).

---

## 6. Gestion des droits des personnes (Art. 12‑22)

| Droit                          | Délai réponse | Processus                                                                  |
| ------------------------------ | ------------- | -------------------------------------------------------------------------- |
| Accès (Art. 15)                | ≤ 1 mois      | Portail web « Mes Données » ou ticket ServiceNow catégorie *RGPD*.         |
| Rectification (Art. 16)        | ≤ 1 mois      | Formulaire *Update Personal Data*.                                         |
| Effacement (Art. 17)           | ≤ 1 mois      | Fonction « Supprimer mon compte » (API `delete_account`) + pipeline purge. |
| Opposition marketing (Art. 21) | Immédiat      | Lien désabonnement en pied de chaque e‑mail, flag DB `opt_out=1`.          |
| Portabilité (Art. 20)          | ≤ 1 mois      | Export JSON téléchargeable en self‑service.                                |
| Limitation (Art. 18)           | ≤ 1 mois      | Flag `processing_limited=1`, lock du compte.                               |

Le **Workflow DSAR** (Data Subject Access Request) est piloté dans ServiceNow avec **SLA tiers** de 25 jours pour marge juridique.

---

## 7. Registre des traitements (Art. 30)

* Maintenu dans l’outil Saas **OneTrust RoPA**.
* Révision **trimestrielle** par le DPO ; export PDF signé déposé dans SharePoint *Compliance*.

---

## 8. Analyse d’impact relative à la protection des données (DPIA – Art. 35)

* DPIA obligatoire pour tout nouveau traitement financier, scoring automatisé ou traitement à grande échelle.
* Modèle **DPIA‑NF‑2025** disponible dans Confluence.
* Score de risque ≥ 2 déclenche revue du DPO + CISO + CNIL si risque élevé non atténué.

---

## 9. Notification des violations de données (Art. 33‑34)

* Tout incident classé **P1‑Security** dans Jira déclenche l’**IRP** et une évaluation DPO/CISO sous 4 h.
* Notification CNIL ≤ 72 h (template *CNIL‑Breach*).
* Notification des personnes concernées si risque élevé ; modèle d’e‑mail stocké dans Eloqua.

---

## 10. Mesures de sécurité & chiffrement

| Donnée                 | Repos                | Transit       |
| ---------------------- | -------------------- | ------------- |
| DB client (PostgreSQL) | TDE AES‑256          | TLS 1.3 ECDHE |
| Fichiers KYC S3        | S3‑SSE‑KMS (AES‑256) | HTTPS         |
| Logs d’accès           | Syslog TLS           | VPN IPSec     |

Accès administrateurs protégés par **MFA + bastion**, journalisation dans Splunk, rotation clés AWS KMS 365 j.

---

## 11. Sensibilisation & formation

* Formation **« Basics of GDPR »** (LMS) obligatoire à l’embauche puis tous les 2 ans.
* Quiz de contrôle (> 85 % réussite) conditionne accès aux environnements de prod.

---

## 12. Revue & amélioration continue

* **Audit interne RGPD** annuel + audits externes CNIL mock.
* Tableau de bord *GDPR COMPLY* sous PowerBI présenté au Comité Conformité tous les trimestres.
* Mécanisme de **leçons apprises** post‑incident sécurité → backlog Privacy by Design.

---

## 13. Historique des versions

| Version | Date       | Auteur | Commentaire        |
| ------- | ---------- | ------ | ------------------ |
| 1.0     | 01/06/2025 | DPO    | Création initiale. |
