# Procédure « Mover » – Mobilité interne et changement de rôle

**Version :** 1.0
**Date d’application :** 1 juillet 2025
**Propriétaire du document :** Responsable IAM

---

## 1. Objectif

Standardiser et sécuriser le traitement des évolutions de poste, de service ou de localisation d’un **collaborateur existant** (Mover) chez Neo Financia : attribution des nouveaux droits requis, retrait des anciens, maintien de la séparation des tâches (SoD) et traçabilité réglementaire.

---

## 2. Périmètre

* Tous les collaborateurs internes dont la fiche RH change de **poste, entité légale, manager ou localisation**.
* Prestataires internes transférés sur un autre projet ou client.
* Systèmes cibles : Active Directory/Azure AD, O365, Core Banking, CRM Salesforce, GitLab, SAP FI, ServiceNow, VPN.
* Sites concernés : Paris, Lyon, Londres (y compris télétravail/transfert international temporaire < 6 mois).

---

## 3. Chronologie & points de passage clés

| Jours ouvrés relatifs | Étape clé                      | Responsable/Outil                 |
| --------------------- | ------------------------------ | --------------------------------- |
| **J‑7**               | Soumission demande de mobilité | **Manager sortant – Portail IAM** |
| **J‑6**               | Mise à jour fiche RH           | **RH – SuccessFactors**           |
| **J‑5**               | Validation SoD & approbations  | **IAM/CISO – SailPoint**          |
| **J‑4**               | Provisioning nouveaux droits   | **IAM – SailPoint**               |
| **J‑1**               | Déprovisioning anciens droits  | **IAM – SailPoint**               |
| **Jour T**            | Prise de poste & vérif. MFA    | **Collaborateur**                 |
| **T+15**              | Audit post‑mouvement & CMDB    | **Audit interne & IT SD**         |

> **SLA** : 100 % des nouveaux accès actifs le jour T ; 0 ancien privilège persistant > 24 h après T.

---

## 4. Procédure détaillée

### 4.1 Initiation (J‑7)

1. **Manager sortant** clique sur *Request ► Transfer* dans le Portail IAM, choisit le collaborateur concerné ; saisit :

   * **Date de transfert** (T) et nouvel intitulé de poste.
   * Liste **droits à retirer** (checkbox des rôles actuels).
2. Le formulaire est automatiquement **copié** au **Manager entrant** qui sélectionne le **pack rôle métier cible** et justifie les accès sensibles.

### 4.2 Validation RH (J‑6)

1. **RH** met à jour SuccessFactors : poste, département, location, manager.
2. L’ETL RH→SailPoint génère l’événement *UpdateIdentity* avec champ *changeType = Transfer*.

### 4.3 Contrôle SoD & approbations (J‑5)

1. **SailPoint** exécute les règles SoD combinant **anciens + nouveaux rôles**.
2. En cas de **conflit critique**, le workflow passe par le **CISO** pour arbitrage :

   * Option 1 : Refus du transfert.
   * Option 2 : Acceptation conditionnelle + implémentation contrôle compensatoire.
3. Après approbation, le workflow déclenche le **plan de provisioning**.

### 4.4 Provisioning nouveaux droits (J‑4)

1. **SailPoint** :

   * Ajoute le collaborateur aux nouveaux groupes AD/Azure AD.
   * Attribue licences O365/E5 ou E3 selon rôle.
   * Crée rôles applicatifs (ex. *Salesforce – Manager*).
   * Met à jour l’accès VPN (profil réseau, split‑tunnel).
2. **ServiceNow** génère un ticket *Hardware Move* si changement de site physique (desk swap, docking station, badge).
3. **Collaborateur** reçoit notification « Vos nouveaux droits sont prêts pour activation le T ».

### 4.5 Déprovisioning anciens droits (J‑1)

1. **SailPoint** compare la liste effective de droits avec la cible ; retire :

   * Groupes AD devenus obsolètes.
   * Accès Core Banking, SAP, GitLab hors périmètre.
2. Les **données personnelles** (home share, boîte mail) restent inchangées ; partages réseau spécifiques sont révoqués.

### 4.6 Transition jour T

1. **Collaborateur** se connecte via MFA et vérifie l’accès aux nouveaux systèmes.
2. **Manager entrant** valide dans le Portail IAM « Accès opérationnels ».
3. **IT SD** clôt tout ticket matériel et confirme mise à jour CMDB (nouvelle localisation asset).

### 4.7 Post‑mouvement (T+1 à T+15)

1. **IAM** exécute un rapport « Dormant Old Privileges » : toute utilisation d’un ancien droit ⇒ alerte SOC.
2. **Audit interne** échantillonne 10 % des Movers pour vérifier :

   * Absence d’anciens droits critiques.
   * Conformité SoD rôle cible.
3. **Managers** réalisent une mini‑revue « Access Review – Mover » à T+15 via SailPoint ; tout écart ➜ correction immédiate.

---

## 5. Checklists par acteur

### 5.1 Manager sortant

* [ ] Soumettre la demande *Transfer* dans le Portail IAM (J‑7).
* [ ] Sélectionner et retirer tous droits non nécessaires après T.
* [ ] Organiser une **passation de connaissances**.
* [ ] Mettre à jour les feuilles de temps/projets pour clôture.

### 5.2 Manager entrant

* [ ] Choisir le **pack rôle métier cible** et accès spécifiques.
* [ ] Vérifier alertes SoD et ajuster si nécessaire.
* [ ] Planifier l’accueil d’équipe (jour T).
* [ ] Confirmer l’activation MFA du collaborateur.
* [ ] Exécuter la revue d’accès **T+15**.

### 5.3 Ressources Humaines

* [ ] Mettre à jour fiche SuccessFactors : poste, manager, BU, site.
* [ ] Émettre avenant contractuel si changement de classification.
* [ ] Notifier Paye & Avantages sociaux.
* [ ] Mettre à jour badge accès physique si changement site.

### 5.4 Équipe IAM

* [ ] Vérifier la bonne réception événement *UpdateIdentity*.
* [ ] Analyser conflits SoD et escalader si critique.
* [ ] Lancer plan provisioning/déprovisioning.
* [ ] Générer rapport *Mover Completion* (Journaux SailPoint).

### 5.5 IT Service Desk

* [ ] Créer ticket *Hardware Move* si besoin.
* [ ] Réassigner poste de travail dans CMDB (site, bureau).
* [ ] Mettre à jour profils d’impression et Wi‑Fi.
* [ ] Clore tickets et notifier manager entrant.

### 5.6 Collaborateur

* [ ] Lire l’e‑mail de notification de mobilité.
* [ ] Tester tous nouveaux accès le jour T.
* [ ] Signaler tout accès manquant via ServiceNow.
* [ ] Mettre à jour signature e‑mail (intitulé, BU, numéro téléphone).

---

## 6. Contrôles & KPI

| Contrôle automatisé              | Outil            | Fréquence  | Seuil d’alerte         |
| -------------------------------- | ---------------- | ---------- | ---------------------- |
| Contrôle SoD post‑mouvement      | SailPoint        | Temps réel | Blocage si *High* risk |
| Ancien droit actif >24 h         | SailPoint        | Horaire    | Alerte SOC             |
| KPI *Mover TTL* (Time‑To‑Lift)   | Splunk Dashboard | Quotidien  | > 2 j = Rouge          |
| KPI *Mover TTR* (Time‑To‑Remove) | Splunk           | Quotidien  | > 24 h = Rouge         |

---

## 7. Escalade

* Temps‑To‑Remove >24 h ➜ canal Slack #jml‑escalation + e‑mail CISO.
* Conflit SoD non résolu >48 h ➜ Directeur Risques Opérationnels.

---

## 8. Références & modèles

* Template *Transfer* (Portail IAM) – Confluence ▶ IAM ▶ Templates.
* Politique JML v1.0.
* Guide SailPoint – chapitre *Modify Identity*.

---

## 9. Historique des versions

| Version | Date       | Auteur    | Commentaire        |
| ------- | ---------- | --------- | ------------------ |
| 1.0     | 01/06/2025 | Resp. IAM | Création initiale. |
