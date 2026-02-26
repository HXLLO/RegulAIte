# PROCESSUS – gestion des vulnérabilités et patch management

## 1. Objet et finalité  

Ce processus a pour finalité de définir l’ensemble des étapes nécessaires à la détection, à l’évaluation, au traitement et au suivi des vulnérabilités informatiques au sein de Neo Financia, ainsi qu’à l’application des correctifs (patchs) en temps utile. Il vise à assurer la protection des systèmes d'information contre les failles de sécurité, tout en garantissant la conformité aux exigences réglementaires et aux normes ISO 27001.

## 2. Champ d’application / Sécurité des Systèmes d’Information & Cyber  

Ce processus s’applique à l’ensemble des environnements informatiques de Neo Financia :

- Postes utilisateurs (bureautique, endpoints)  
- Systèmes serveurs (on-premise et cloud)  
- Applications critiques (banque en ligne, KYC, core banking)  
- Composants réseau, bases de données, middlewares

## 3. Parties prenantes & RACI (rôles)

| Rôle                                | R | A | C | I |
|-------------------------------------|---|---|---|---|
| RSSI (Responsable Sécurité SI)      | X |   | X | X |
| Équipe Cyberdéfense / SOC           |   | X |   | X |
| Administrateurs Systèmes            |   | X |   | X |
| Équipe IT Ops / Infrastructure      |   | X |   |   |
| Équipe Applicative                  |   |   | X | X |
| Direction des Risques               |   |   | X |   |
| Conformité & Audit Interne          |   |   | X |   |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

- Veille cybersécurité (CERT-FR, CISA, CVE, fournisseurs logiciels)
- Scans de vulnérabilités automatisés (hebdomadaires)
- Signalements internes ou audits techniques
- Notes de sécurité éditeurs (patch advisories)
- Incidents ou alertes détectés par le SOC

## 5. Macro-workflow BPMN / chaîne de valeur  

### 5.1 Vue d’ensemble (diagramme texte + numérotation)

1. Détection de la vulnérabilité  
2. Qualification et évaluation du risque  
3. Planification de la correction  
4. Validation des correctifs  
5. Déploiement du patch  
6. Vérification post-déploiement  
7. Archivage, reporting et amélioration continue

### 5.2 Sous-processus clés

- **Détection proactive** : par scans réguliers, bulletins éditeurs, signalements.  
- **Classification** : selon criticité CVSS (score ≥7 : prioritaire sous 72h).  
- **Patch management** : tests sur environnement pilote, validation QA, déploiement progressif.  
- **Revue et validation** : suivi par le RSSI, alertes escaladées si délai dépassé.  
- **Traçabilité** : journalisation systématique des actions menées.

### 5.3 Points de contrôle & jalons

- Point de décision : déploiement immédiat vs report justifié.  
- Contrôle qualité post-patch : tests de non-régression.  
- Suivi de conformité via tableaux de bord hebdomadaires.  
- Jalon mensuel : revue des vulnérabilités critiques non corrigées.

## 6. Sorties et clients internes/externes (SIPOC – O/C)

**Sorties :**

- Rapport de vulnérabilité corrigée (ticket, log, scan)
- Registre des patchs appliqués (CMDB, GRC)
- KPI cybersécurité

**Clients internes :**

- Direction SI
- Direction des Risques
- Audit interne
- Comités de sécurité

**Clients externes :**

- Autorités (ACPR, ANSSI si incident grave)
- Auditeurs externes / PCA

## 7. Ressources & systèmes support (IT, data, fournisseurs)

- Scanner de vulnérabilités (ex : Qualys, Nessus)
- Outil de patch management (WSUS, SCCM, Ansible, scripts personnalisés)
- SIEM / SOC (logs & alertes)
- Outil GRC interne
- Référentiels CVE/NVD (automatisés via API)

## 8. Exigences de conformité (ACPR, EBA, ISO 27001/27701, RGPD)

- **ISO 27001** : A.12.6.1, A.14.2.2 (gestion des vulnérabilités techniques)
- **ISO 27701** : protection des données personnelles en cas de faille
- **ACPR / EBA ICT Guidelines** : exigences de remédiation rapide
- **RGPD art. 32** : obligation de sécurité, notification de faille dans les 72h si données impactées

## 9. Indicateurs de performance (KPIs) & seuils SLA

| KPI                                         | Objectif               | Périodicité     |
|---------------------------------------------|-------------------------|-----------------|
| Délai moyen de traitement vulnérabilité critique | ≤ 72h                 | Hebdomadaire    |
| Taux de conformité patch mensuel             | ≥ 95 %                 | Mensuelle       |
| Nombre de vulnérabilités non traitées >30j   | = 0                    | Mensuelle       |
| Disponibilité post-patch (non-régression)    | ≥ 99,5 %               | Par déploiement |

## 10. Risques, gaspillages (Lean) et actions de mitigation

| Risque / Gaspillage                      | Action de mitigation                          |
|------------------------------------------|-----------------------------------------------|
| Déploiement trop lent                    | Automatisation, priorisation par criticité    |
| Patchs bloquants ou déstabilisants       | Environnement de préproduction obligatoire    |
| Oubli ou doublon dans la gestion         | Suivi centralisé via GRC et CMDB              |
| Manque de ressources qualifiées          | Plan de montée en compétence, backup assigné  |

## 11. Interfaces & dépendances croisées (processus amont/aval)

- **Amont** : gestion des incidents sécurité, veille cyber, audits techniques  
- **Aval** : gestion de configuration (CMDB), suivi conformité, reporting DSI  
- Dépendances avec : gestion des changements, tests QA, communication sécurité

## 12. Plans d’amélioration continue (PDCA)

- **Plan** : Revue semestrielle du périmètre de scan et des politiques patch  
- **Do** : Déploiement pilote de nouveaux outils d'automatisation  
- **Check** : Audit interne ISO 27001 + tests d’intrusion tiers  
- **Act** : Revue des procédures, mise à jour des seuils SLA/KPI

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                        | Modification principale                 |
|---------|------------|-------------------------------|-----------------------------------------|
| 1.0     | 28/05/2025 | Consultant Senior Cybersécurité| Création initiale du processus          |
| 1.1     |            |                               |                                         |
| 1.2     |            |                               |                                         |
