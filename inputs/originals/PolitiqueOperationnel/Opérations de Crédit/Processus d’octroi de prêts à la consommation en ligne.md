# PROCESSUS – octroi de prêts à la consommation en ligne

## 1. Objet et finalité

Ce processus détaille les étapes opérationnelles pour l’octroi rapide, sécurisé et conforme de prêts à la consommation via une plateforme entièrement digitale. Il assure l’efficacité du traitement, la satisfaction client, la maîtrise des risques crédit, et garantit le respect des exigences réglementaires ACPR/EBA, RGPD, PSD2 et ISO 9001/27001.

## 2. Champ d’application / Opérations de Crédit

Ce processus concerne exclusivement :

* Les prêts à la consommation (prêts personnels, crédits renouvelables, etc.).
* L’ensemble des demandes initiées via les canaux digitaux (web et mobile).
* Toutes les opérations de crédit pour les particuliers dans les pays couverts (France et Royaume-Uni).

## 3. Parties prenantes & RACI (rôles)

| Rôle                     | Responsable (R) | Acteur (A) | Consulté (C) | Informé (I) |
| ------------------------ | --------------- | ---------- | ------------ | ----------- |
| Responsable Crédit Conso | R               |            |              |             |
| Analyste Crédit          |                 | A          |              |             |
| Responsable Conformité   |                 | C          |              | I           |
| Équipe IT/Digital        |                 | A          | C            | I           |
| Service Client           |                 | A          |              | I           |
| Directeur Risques        |                 |            | C            | I           |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

| Entrées                             | Déclencheurs                       | Fournisseurs       |
| ----------------------------------- | ---------------------------------- | ------------------ |
| Demande en ligne complétée          | Soumission via plateforme digitale | Client             |
| Pièces justificatives électroniques | Téléchargement documents           | Client             |
| Score de risque automatisé          | Validation automatique dossier     | Système de scoring |
| Données client/KYC                  | Vérification initiale              | Bases externes/KYC |

## 5. Macro-workflow BPMN / chaîne de valeur

### 5.1 Vue d’ensemble (diagramme texte + numérotation)

``
[1] Réception demande → [2] Vérification initiale automatisée (KYC/Risque crédit) → [3] Analyse approfondie crédit (si nécessaire) → [4] Décision d’octroi/refus automatisée → [5] Validation manuelle exceptionnelle (si requis) → [6] Signature digitale contrat → [7] Mise à disposition fonds → [8] Archivage & suivi conformité
``

### 5.2 Sous-processus clés

* **2.1 Vérification automatisée des données KYC et scoring crédit initial**
* **3.1 Analyse manuelle crédit (exception dossiers complexes ou à risque élevé)**
* **4.1 Processus de décision automatique avec seuils préétablis**
* **6.1 Signature électronique et archivage contrat**

### 5.3 Points de contrôle & jalons

* Validation automatique des informations et scoring initial (étape 2)
* Décision manuelle si scoring insuffisant ou anomalies détectées (étape 5)
* Vérification conformité RGPD/KYC avant mise à disposition fonds (étape 6)

## 6. Sorties et clients internes/externes (SIPOC – O/C)

| Sorties                          | Clients internes/externes    |
| -------------------------------- | ---------------------------- |
| Contrat signé électroniquement   | Client (externe)             |
| Rapport de décision crédit       | Audit interne (interne)      |
| Archivage dossier crédit complet | Compliance/Risques (interne) |

## 7. Ressources & systèmes support (IT, data, fournisseurs)

* Plateforme digitale intégrée de demande et gestion de prêts
* Outil de scoring automatique (modèle de risque crédit interne)
* Systèmes KYC automatisés
* Solution de signature électronique certifiée
* Archivage sécurisé (système SharePoint sécurisé)
* Fournisseurs externes de données (Bureaux de crédit, bases KYC)

## 8. Exigences de conformité (ACPR/EBA, RGPD, PSD2, ISO 9001/27001)

* **ACPR/EBA** : conformité des processus crédit (EBA/GL/2017/06)
* **RGPD** : traitement sécurisé et confidentiel des données personnelles
* **PSD2** : sécurité renforcée authentification, transparence tarifaire
* **ISO 9001/27001** : qualité opérationnelle, intégrité et sécurité des données

## 9. Indicateurs de performance (KPIs) & seuils SLA

| Indicateur                                   | Fréquence   | SLA                             |
| -------------------------------------------- | ----------- | ------------------------------- |
| Temps de traitement global d’une demande     | Mensuel     | ≤ 15 min (auto), ≤ 48h (manuel) |
| Taux d’acceptation automatique               | Mensuel     | ≥ 80 %                          |
| Taux de dossiers non conformes ou incomplets | Mensuel     | ≤ 5 %                           |
| Taux de satisfaction client sur le processus | Trimestriel | ≥ 90 %                          |

## 10. Risques, gaspillages (Lean) et actions de mitigation

| Risque/Gaspillage                  | Actions de mitigation                         |
| ---------------------------------- | --------------------------------------------- |
| Traitements manuels excessifs      | Optimisation constante du scoring automatique |
| Données incorrectes ou incomplètes | Contrôles automatisés renforcés (IA)          |
| Non-conformité réglementaire       | Audits internes périodiques ciblés            |

## 11. Interfaces & dépendances croisées (processus amont/aval)

| Processus amont              | Processus aval                       |
| ---------------------------- | ------------------------------------ |
| Acquisition digitale clients | Gestion et recouvrement crédit       |
| Vérification KYC initiale    | Monitoring crédit & reporting        |
| Modèles de scoring crédit    | Amélioration continue scoring risque |

## 12. Plans d’amélioration continue (PDCA)

* **Plan** : Analyse mensuelle des anomalies et incidents récurrents.
* **Do** : Mise en œuvre rapide d’améliorations techniques/process.
* **Check** : Validation trimestrielle par audit interne et revue KPI.
* **Act** : Ajustement et implémentation continue des meilleures pratiques observées.

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                   | Modification principale        |
| ------- | ---------- | ------------------------ | ------------------------------ |
| 1.0     | 28/05/2025 | Consultant Senior Crédit | Création initiale du processus |
| 1.1     |            |                          |                                |
| 1.2     |            |                          |                                |
