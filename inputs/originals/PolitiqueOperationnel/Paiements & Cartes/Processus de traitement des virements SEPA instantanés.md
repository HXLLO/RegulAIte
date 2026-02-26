# PROCESSUS – traitement des virements SEPA instantanés

## 1. Objet et finalité

Ce processus décrit, de manière opérationnelle détaillée, l’ensemble des étapes permettant à Neo Financia de traiter les virements SEPA instantanés, 24h/24 et 7j/7, conformément aux exigences de sécurité, de performance et de conformité réglementaire. Il vise à garantir une exécution en temps réel (≤ 10 secondes), tout en assurant la traçabilité, la détection des fraudes et la satisfaction client.

## 2. Champ d’application / Paiements & Cartes

Le processus s’applique à :

* Tous les virements SEPA instantanés initiés ou reçus par les clients de Neo Financia (particuliers et professionnels).
* L’ensemble des équipes impliquées dans la chaîne de traitement (paiements, sécurité, conformité).
* Les systèmes d’échange interbancaire connectés au réseau SEPA Instant Credit Transfer (SCT Inst).

## 3. Parties prenantes & RACI (rôles)

| Rôle                           | Responsable (R) | Acteur (A) | Consulté (C) | Informé (I) |
| ------------------------------ | --------------- | ---------- | ------------ | ----------- |
| Responsable Paiements          | R               |            |              |             |
| Analyste Paiements             |                 | A          |              |             |
| Responsable Sécurité IT (CISO) |                 | A          | C            | I           |
| Responsable Conformité         |                 | C          |              | I           |
| Équipe Support Client          |                 | A          |              | I           |
| Directeur des Opérations       |                 |            | C            | I           |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

| Entrées                               | Déclencheurs                      | Fournisseurs                  |
| ------------------------------------- | --------------------------------- | ----------------------------- |
| Ordre de virement (client, API, app)  | Saisie ou instruction automatique | Client, API partenaire        |
| Données bénéficiaire (IBAN, nom, BIC) | Saisie en ligne                   | Client                        |
| Référentiel interbancaire SCT Inst    | Tentative de virement instantané  | EBA CLEARING / TARGET Instant |
| Authentification client (SCA)         | Validation de l’opération         | Neo Financia / TPP (si PSD2)  |

## 5. Macro-workflow BPMN / chaîne de valeur

### 5.1 Vue d’ensemble (diagramme texte + numérotation)

``
[1] Initiation du virement → [2] Authentification forte (SCA) → [3] Vérification des plafonds/solde → [4] Vérification format & compatibilité SCT Inst → [5] Contrôle antifraude temps réel → [6] Transmission au système de compensation (TARGET/EBA) → [7] Réception de confirmation → [8] Notification au client → [9] Journalisation & archivage
``

### 5.2 Sous-processus clés

* **2.1 Authentification** : forte (SCA) selon canal (app, API, carte).
* \*\*3.1 Vérification du solde disponible et des plafonds instantanés.
* \*\*5.1 Contrôle en temps réel via moteur antifraude (pattern, bénéficiaire, localisation).
* \*\*6.1 Envoi structuré via API au système de règlement (EBA CLEARING ou TARGET Instant).

### 5.3 Points de contrôle & jalons

* SCA validée (étape 2) → clé de conformité PSD2.
* Vérification de conformité IBAN & BIC + banque bénéficiaire membre SCT Inst (étape 4).
* Confirmation de règlement (étape 7) < 10 secondes.

## 6. Sorties et clients internes/externes (SIPOC – O/C)

| Sorties                            | Clients internes/externes   |
| ---------------------------------- | --------------------------- |
| Confirmation de virement           | Client (externe)            |
| Journal d’opération (log sécurisé) | Audit, conformité (interne) |
| Notification push/email/SMS        | Client (externe)            |

## 7. Ressources & systèmes support (IT, data, fournisseurs)

* Plateforme Core Banking & moteur temps réel de paiements
* Connectivité EBA CLEARING / TARGET Instant
* Moteur SCA & moteur antifraude
* Module API (REST) ouvert pour TPP (Third Party Provider)
* Infrastructure de supervision des flux 24/7
* Système de journalisation sécurisé et piste d’audit (ISO 27001)

## 8. Exigences de conformité (ACPR/EBA, RGPD, PSD2, ISO 9001/27001)

* **ACPR/EBA** : conformité à la Directive 2015/2366 (PSD2) et à RTS SCA/CSC.
* **RGPD** : protection des données de paiement et traçabilité.
* **ISO 9001** : performance, continuité et qualité de service.
* **ISO 27001** : sécurité des échanges, chiffrement des données sensibles.

## 9. Indicateurs de performance (KPIs) & seuils SLA

| Indicateur                                         | Fréquence     | SLA           |
| -------------------------------------------------- | ------------- | ------------- |
| Délai moyen d’exécution d’un virement instantané   | Quotidienne   | ≤ 10 secondes |
| Taux de succès des virements instantanés           | Hebdomadaire  | ≥ 99 %        |
| Disponibilité du service SEPA Inst                 | Mensuelle     | ≥ 99,9 %      |
| Taux d’opérations bloquées par antifraude légitime | Trimestrielle | ≤ 2 %         |

## 10. Risques, gaspillages (Lean) et actions de mitigation

| Risque ou gaspillage                          | Action de mitigation                         |
| --------------------------------------------- | -------------------------------------------- |
| Non-routage vers SCT Inst (banque non membre) | Vérification automatique via référentiel SCT |
| Erreurs d’authentification client             | Optimisation UX et double canal SCA          |
| Temps de traitement > 10s                     | Monitoring 24/7 + équilibrage charge système |
| Faux positifs antifraude                      | Affinage des règles & IA comportementale     |

## 11. Interfaces & dépendances croisées (processus amont/aval)

| Processus amont                        | Processus aval                         |
| -------------------------------------- | -------------------------------------- |
| Authentification et sécurisation (SCA) | Suivi transactionnel et support client |
| Gestion des comptes & soldes           | Réconciliation comptable et reporting  |
| Intégration API pour TPP               | Reporting PSD2 & supervision ACPR      |

## 12. Plans d’amélioration continue (PDCA)

* **Plan** : Revue mensuelle des incidents, alertes antifraude, performances système.
* **Do** : Mise en place des améliorations (optimisation, UX, filtrage).
* **Check** : Suivi des indicateurs et audits de conformité.
* **Act** : Ajustement des règles antifraude, API, délais de traitement.

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                      | Modification principale                        |
| ------- | ---------- | --------------------------- | ---------------------------------------------- |
| 1.0     | 28/05/2025 | Consultant Senior Paiements | Création initiale du processus SEPA instantané |
| 1.1     |            |                             |                                                |
| 1.2     |            |                             |                                                |
