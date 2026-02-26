# Procédure « Joiner » – Intégration d’un nouveau collaborateur

**Version :** 1.0
**Date d’application :** 1 juillet 2025
**Propriétaire du document :** Responsable IAM

---

## 1. Objectif

Établir l’ensemble des étapes opérationnelles, responsabilités et contrôles nécessaires pour créer, configurer et valider les comptes et accès d’un **nouveau collaborateur** (Joiner) chez Neo Financia, tout en respectant les exigences de sécurité, de conformité réglementaire (PSD2, GDPR) et de service.

---

## 2. Périmètre

* Collaborateurs internes : CDI, CDD, alternants, stagiaires.
* Prestataires externes disposant d’un compte nominatif.
* Entités couvertes : Siège Paris, bureaux de Lyon et Londres.
* Systèmes cibles : Active Directory/Azure AD, O365, Core Banking, CRM Salesforce, VPN Palo Alto, GitLab, ServiceNow.

---

## 3. Chronologie & points de passage clés

| Jours ouvrés relatifs | Étape clé                                        | Outil/Responsable                |
| --------------------- | ------------------------------------------------ | -------------------------------- |
| **J‑5**               | Création du collaborateur dans SIRH              | **RH – SuccessFactors**          |
| **J‑4**               | Sélection des rôles métier et validation manager | **Portail IAM – Manager**        |
| **J‑3**               | Provisioning automatique des comptes             | **SailPoint IAM**                |
| **J‑2**               | Préparation & étiquetage du matériel             | **IT Service Desk – ServiceNow** |
| **Jour J**            | Activation MFA + prise de poste                  | **Joiner**                       |
| **J+30**              | Revue conformité des accès                       | **Manager – Portail IAM**        |

> **SLA** : 100 % des comptes actifs 24 h avant arrivée ; 0 % de droits non justifiés lors de la revue J+30.

---

## 4. Procédure détaillée

### 4.1 Pré‑embarquement (J‑5 à J‑4)

1. **Signature du contrat** – RH dépose le PDF signé dans DocuSign.
2. **Création fiche collaborateur** – RH remplit les champs obligatoires dans SuccessFactors : *Nom, Prénom, Date d’entrée, Type de contrat, Manager.*
3. **Sync automatique** – L’ETL SuccessFactors→SailPoint pousse l’événement *NewHire* ; un identifiant **EmployeeID** unique est généré.
4. **Notification** – Portail IAM notifie le manager par e‑mail « Action requise – Sélectionner rôle métier ».

### 4.2 Sélection du rôle métier (J‑4)

1. **Manager** se connecte au Portail IAM (SSO) et :

   * Choisit le **pack applicatif** approprié (ex. *Analyste Crédit Retail*).
   * Indique besoins spécifiques (ex. accès GitLab, environnement UAT).
   * Saisit la **date d’accès anticipé** si nécessaire (testing, formation).
2. **Validation SoD** – Le moteur SailPoint exécute la règle *Access Risk Policy* ; en cas de conflit SoD, le workflow passe en *Révision CISO*.
3. **Approbation** – Le CISO (ou délégué) approuve/refuse ; le workflow reprend.

### 4.3 Provisioning (J‑3)

1. **SailPoint** déclenche les connecteurs API :

   * Active Directory/Azure AD ⇢ création compte, appartenance groupes, attribution licence O365 E5.
   * Core Banking REST ⇢ création utilisateur, profil *read‑only* par défaut.
   * Salesforce ⇢ rôle *Standard User* + partage selon BU.
2. **Génération mot de passe initial** : stocké dans coffre‑fort CyberArk, valable 24 h.
3. **Création tickets ServiceNow** :

   * *New Laptop + Smartphone* (assigné IT SD).
   * *YubiKey Provisioning*.

### 4.4 Préparation matériel (J‑2)

1. **IT SD** récupère liste équipements, étiquette actifs CMDB.
2. Configure :

   * BitLocker + Intune sur laptop.
   * eSIM/Carte SIM + MDM sur smartphone.
3. Dépose le kit « Welcome Pack » à l’accueil ou l’expédie (télétravail).

### 4.5 Arrivée (Jour J)

1. **Onboarding Welcome Call** – RH + Manager (Teams, 30 min).
2. **Prise en main IT** :

   * Joiner récupère mot de passe dans CyberArk ; se connecte O365.
   * Active **MFA** (application Authenticator + YubiKey).
   * Change mot de passe initial.
3. **Checklist sécurité** – pop‑up portail O365 « Premiers pas sécurité » :

   * L’installation des correctifs Windows / MacOS est confirmée.
   * Politique mot de passe acceptée.
   * Chartes IT & sécurité signées électroniquement (DocuSign).

### 4.6 Post‑intégration (J+1 à J+30)

1. **RH** confirme présence effective dans SuccessFactors (statut *Active*).
2. **Manager** suit un rapport automatique « Access Review – New Hire » à J+7 pour vérifier les accès non utilisés.
3. **IAM** exécute une règle : si un compte applicatif n’a pas de connexion > 14 jours, il est mis en **quarantaine** et notifié.
4. **Revue finale J+30** : le manager valide que :

   * Les accès sont toujours nécessaires (sinon, bouton *Remove*).
   * Aucun privilège non documenté.
     Le rapport signé est archivé dans Confluence.

---

## 5. Checklists par acteur

### 5.1 Ressources Humaines

* [ ] Vérifier l’éligibilité (pièce d’identité, permis de travail).
* [ ] Créer le dossier collaborateur dans SuccessFactors et générer l’**EmployeeID**.
* [ ] Télécharger le contrat signé (SuccessFactors & DocuSign).
* [ ] Renseigner la date d’entrée définitive et notifier le manager & IT SD.
* [ ] Envoyer l’e‑mail de bienvenue + guide d’onboarding RH.
* [ ] Planifier la session d’intégration RH (présentiel ou Teams).
* [ ] Créer la demande de badge d’accès physique.
* [ ] Vérifier l’inscription aux formations obligatoires (LMS).

### 5.2 Manager

* [ ] Sélectionner le **pack rôle métier** dans le Portail IAM.
* [ ] Justifier les accès spécifiques (GitLab, UAT, données sensibles).
* [ ] Examiner les alertes SoD et résoudre les conflits éventuels.
* [ ] Préparer le plan d’intégration 30‑60‑90 jours et nommer un mentor.
* [ ] Participer au **Welcome Call** (Jour J).
* [ ] Valider la disponibilité du poste de travail et des logiciels.
* [ ] Confirmer la présence effective dans SuccessFactors (Jour J).
* [ ] Réaliser la revue d’accès **J+30** et retirer ceux inutilisés.

### 5.3 IT Service Desk

* [ ] Créer le ticket ServiceNow « New Hire » lié à l’EmployeeID.
* [ ] Imager le laptop (build standard) et activer BitLocker + Intune.
* [ ] Configurer le smartphone, activer eSIM/MDM, vérifier patch OS.
* [ ] Programmer la YubiKey et l’associer à l’identité Azure AD.
* [ ] Tester la connexion VPN et l’accès réseau interne.
* [ ] Préparer le *Welcome Pack* et l’étiqueter (CMDB).
* [ ] Livrer ou expédier le kit avant **J‑1**.
* [ ] Clore le ticket ServiceNow, joindre la fiche de contrôle matériel.

### 5.4 Collaborateur

* [ ] Récupérer le mot de passe initial dans CyberArk.
* [ ] Se connecter à O365 et changer le mot de passe lors de la première connexion.
* [ ] Activer la YubiKey + application Authenticator pour MFA.
* [ ] Lire et signer la charte IT & sécurité (DocuSign).
* [ ] Vérifier l’accès Teams, Intranet, Core Banking (si applicable).
* [ ] Confirmer la réception du matériel dans ServiceNow.
* [ ] Compléter le module e‑learning *Sécurité* (LMS) avant **J+3**.
* [ ] Participer aux sessions d’accueil RH/IT.

## 6. Contrôles & KPI Contrôles & KPI

| Contrôle automatisé      | Outil            | Fréquence  | Seuil d’alerte          |
| ------------------------ | ---------------- | ---------- | ----------------------- |
| Validation SoD           | SailPoint        | Temps réel | Blocage workflow        |
| Inactivité comptes >14 j | SailPoint        | Quotidien  | Quarantaine automatique |
| KPI *Joiner TTA*         | Splunk Dashboard | Quotidien  | > 3 jours = Rouge       |

---

## 7. Escalade

* SLA provisioning non respecté ➜ Slack #jml-escalation puis e‑mail CISO.
* Conflit SoD non résolu >48 h ➜ escalade Directeur Risques Opérationnels.

---

## 8. Références & modèles

* Template *New Hire* (Portail IAM) – dernière version \[Confluence ▶ IAM ▶ Templates].
* Politique JML v1.0.
* Guide Utilisateur SailPoint – chapitre *Create Identity*.

---

## 9. Historique des versions

| Version | Date       | Auteur    | Commentaire        |
| ------- | ---------- | --------- | ------------------ |
| 1.0     | 01/06/2025 | Resp. IAM | Création initiale. |
