# Politique de Gestion des Joiners, Movers & Leavers (JML)

**Version :** 1.0
**Date d’entrée en vigueur :** 1 juillet 2025
**Propriétaire du document :** Chief Information Security Officer (CISO)
**Périmètre :** Neo Financia – siège de Paris et bureaux de Lyon et Londres

---

## 1. Objet

Cette politique définit les principes, responsabilités et procédures encadrant le cycle de vie des identités et des accès des collaborateurs (employés, prestataires, stagiaires et partenaires) chez Neo Financia, depuis leur arrivée (Joiners), leur mobilité interne (Movers) jusqu’à leur départ (Leavers). Elle vise à :

* Garantir l’application du principe du moindre privilège et la séparation des tâches ;
* Réduire les risques liés à l’accès non autorisé aux systèmes, données et actifs bancaires ;
* Assurer la conformité aux exigences réglementaires européennes (PSD2, GDPR, EBA/ACPR) et aux normes ISO 27001 & 27701 ;
* Formaliser des délais clairs et contrôlables pour l’attribution, la modification et la suppression des droits d’accès.

---

## 2. Champ d’application

Cette politique s’applique à :

* Tous les collaborateurs internes de Neo Financia, quelles que soient la nature et la durée de leur contrat ;
* Tous les prestataires externes disposant d’un accès logique ou physique aux actifs informationnels de la banque ;
* L’ensemble des systèmes d’information, applications, services Cloud, infrastructures, équipements et locaux exploités ou propriété de Neo Financia.

---

## 3. Références et définitions

| Terme                 | Définition                                                                                                                                |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Joiner**            | Toute personne pour laquelle un nouveau compte d’accès est requis (nouvelle embauche, consultant, stagiaire).                             |
| **Mover**             | Toute personne dont le rôle, l’affectation ou le périmètre de responsabilités évolue, nécessitant une modification de ses droits d’accès. |
| **Leaver**            | Toute personne quittant définitivement l’organisation ou dont la mission prend fin.                                                       |
| **IAM**               | Identity & Access Management, ensemble des processus et outils permettant de gérer le cycle de vie des identités numériques.              |
| **Moindre privilège** | Principe consistant à n’octroyer que les droits strictement nécessaires à l’exécution des tâches assignées.                               |

---

## 4. Gouvernance et responsabilités

| Rôle                             | Responsabilités clés                                                                                     |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Comité Sécurité & Conformité** | Valide et révise annuellement la présente politique.                                                     |
| **CISO**                         | Détient la responsabilité globale, assure la diffusion et la mise à jour de la politique.                |
| **Équipe IAM**                   | Implémente les processus techniques JML dans l’outil IAM central et exécute les revues d’accès.          |
| **Ressources Humaines (RH)**     | Fournit les données master des collaborateurs, initie les demandes d’intégration et notifie les départs. |
| **Managers hiérarchiques**       | Demandent, approuvent et révisent les accès de leurs équipes ; veillent à la restitution du matériel.    |
| **Service IT**                   | Crée, modifie et supprime les accès techniques ; gère l’inventaire du matériel.                          |
| **Conformité & Audit interne**   | Vérifient l’alignement aux obligations réglementaires et effectuent des contrôles.                       |

---

## 5. Processus JML détaillés

### 5.1 Joiners – Processus d’intégration

| Étape                  | Responsable   | Délai cible  | Description                                                                                                                                                              |
| ---------------------- | ------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Pré‑embarquement       | RH            | ≥ J‑5 ouvrés | Création du profil dans le SIRH ; déclenchement automatique de la « Employee ID » dans l’IAM.                                                                            |
| Provisioning des accès | IAM / IT      | ≤ J‑3 ouvrés | Attribution des rôles par défaut (messagerie, VPN, outils collaboratifs) conformément au poste et à la matrice des rôles. Aucune donnée sensible avant la date de début. |
| Vérification MFA       | Collaborateur | Jour J       | Activation obligatoire de l’authentification multifacteur sur tous les services exposés à Internet.                                                                      |
| Revue post‑intégration | Manager       | J + 30       | Confirmation que les accès octroyés sont adaptés ; suppression des droits non utilisés (> 30 jours).                                                                     |

### 5.2 Movers – Mobilité interne & changements de rôle

| Étape                             | Responsable            | Délai cible | Description                                                                               |
| --------------------------------- | ---------------------- | ----------- | ----------------------------------------------------------------------------------------- |
| Demande de changement             | Manager sortant        | J‑7         | Soumission dans le portail IAM d’un workflow « Transfer » précisant les droits à retirer. |
| Approbation & provisioning        | Manager entrant + CISO | J‑5         | Attribution des nouveaux rôles après validation SoD automatique.                          |
| Déprovisioning des anciens droits | IAM                    | J‑1         | Révocation des droits non requis et mise à jour des groupes AD/SaaS.                      |
| Audit post‑mouvement              | IAM / Audit interne    | J + 15      | Contrôle de conformité et mise à jour de la CMDB des actifs.                              |

### 5.3 Leavers – Processus de départ

| Étape                        | Responsable   | Délai cible      | Description                                                                   |
| ---------------------------- | ------------- | ---------------- | ----------------------------------------------------------------------------- |
| Notification de départ       | RH            | Dès connaissance | RH saisit la date de fin dans le SIRH ; synchronisation immédiate vers l’IAM. |
| Suspendre les accès logiques | IAM           | ≤ 4 heures       | Désactivation des comptes, tokens, certificats, sessions VPN et accès Cloud.  |
| Restitution des actifs       | Manager       | Jour J           | Collecte des ordinateurs, Smartphones, badges, YubiKeys.                      |
| Suppression définitive       | IAM           | J + 30           | Suppression irréversible des comptes (sauf archivage exigé par la loi).       |
| Revues d’accès post‑départ   | Audit interne | Trimestriel      | Vérification échantillonnée des comptes désactivés = 100 % de fiabilité.      |

---

## 6. Principes de gestion des accès

1. **Moindre privilège & SoD** : toute consolidation de droits par rôle, contrôlée par une matrice SoD approuvée par le CISO.
2. **MFA obligatoire** : active sur l’ensemble des systèmes critiques (Core Banking, CRM, Cloud, VPN).
3. **Durée limitée** : accès temporaires (ex. prestataires) expirent automatiquement à T+90 jours, renouvelables sur justification.
4. **Révisions périodiques** : managers procèdent à une revue trimestrielle des accès de leur équipe via l’IAM.
5. **Journalisation** : toute action JML est historisée dans un SIEM central pour audit.

---

## 7. Sensibilisation et formation

* Formation JML incluse dans le parcours d’onboarding numérique (LMS) pour tous les collaborateurs.
* Sessions spécifiques pour les managers et administrateurs système (2 h, e‑learning + quiz).

---

## 8. Documentation & conservation des enregistrements

* Les logs IAM sont conservés **5 ans** conformément aux exigences de l’ACPR.
* Les formulaires d’approbation (Joiner, Mover, Leaver) sont archivés dans DocuSign et indexés par l’ID collaborateur.

---

## 9. Conformité réglementaire

Cette politique soutient la conformité aux textes suivants :

* **PSD2 (Directive EU 2015/2366)** – sécurité des paiements et authentification forte ;
* **Règlement (UE) 2016/679 (GDPR)** – protection des données à caractère personnel ;
* **EBA Guidelines on ICT & Security Risk Management (EBA/GL/2019/04)** ;
* **Arrêté du 3 novembre 2014 (ACPR)** – obligations en matière de contrôle interne des établissements de crédit.

---

## 10. Audit, contrôle & amélioration continue

* Un **audit interne annuel** vérifie l’effectivité des contrôles JML (échantillon ≥ 10 % des mouvements).
* Les résultats sont présentés au Comité Sécurité & Conformité, avec plan d’actions correctives.
* Les indicateurs clés :

  * Taux de désactivation < 4 h ;
  * % de comptes orphelins ;
  * Taux de réussite des revues d’accès trimestrielles.

---

## 11. Exceptions

Toute dérogation à la présente politique doit être demandée par écrit, approuvée par le CISO et consignée dans le registre des exceptions pour une durée maximale de 6 mois renouvelable.

---

## 12. Mise à jour et révision

La politique est revue au minimum **annuellement** ou plus fréquemment si :

* Évolutions réglementaires significatives ;
* Changements majeurs dans l’architecture SI ;
* Incidents de sécurité confirmant une faiblesse du processus JML.

---

## 13. Historique des versions

| Version | Date       | Auteur | Description                    |
| ------- | ---------- | ------ | ------------------------------ |
| 1.0     | 01/06/2025 | CISO   | Création initiale du document. |
