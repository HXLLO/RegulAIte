# PROCÉDURE – réponse aux incidents de sécurité (CSIRT)

## 1. Objet et finalité  

Cette procédure définit les étapes détaillées de gestion des incidents de sécurité au sein de Neo Financia, via le dispositif CSIRT (Computer Security Incident Response Team). Elle vise à identifier, qualifier, contenir, éradiquer, analyser et capitaliser tout incident cyber, en garantissant une réponse rapide, coordonnée et conforme.

## 2. Champ d’application / Sécurité des Systèmes d’Information & Cyber  

Cette procédure s’applique à tous les systèmes, infrastructures, applications et données critiques de Neo Financia, y compris les environnements cloud, les endpoints utilisateurs, les réseaux internes et les interfaces tierces. Elle couvre les incidents de type :

- Intrusion ou tentative d’intrusion  
- Malware / ransomware  
- Exfiltration ou perte de données  
- Déni de service  
- Compromission de comptes / accès non autorisé  
- Faille de sécurité logicielle exploitée

## 3. Références réglementaires et normatives (ACPR, EBA, RGPD, ISO 27001)

- **RGPD – Art. 33 & 34** : Notification à l’autorité de contrôle et aux personnes concernées  
- **ISO/IEC 27001** : A.16 – Gestion des incidents liés à la sécurité  
- **ISO/IEC 27035** : Gestion des incidents de sécurité de l'information  
- **EBA ICT Guidelines** : Réactivité et communication en cas d’incident majeur  
- **ACPR** : Instruction N°2019-I-05 sur les signalements de cybersécurité

## 4. Définitions & acronymes  

- **CSIRT** : Équipe de réponse aux incidents de sécurité informatique  
- **IOC** : Indicateur de compromission  
- **SIEM** : Security Information and Event Management  
- **SOC** : Security Operations Center  
- **NOC** : Network Operations Center  
- **IRP** : Incident Response Plan

## 5. Rôles et responsabilités (RACI)

| Fonction                        | R | A | C | I |
|---------------------------------|---|---|---|---|
| Responsable CSIRT               |   | X | X |   |
| Analyste SOC / Cyberdéfense     | X |   |   | X |
| RSSI                            |   |   | X | X |
| DSI / IT Infrastructure         |   |   | X | X |
| Juridique / DPO                 |   |   | X | X |
| Communication institutionnelle  |   |   |   | X |
| Management de crise             |   |   |   | X |

## 6. Prérequis / Entrées nécessaires  

- Alertes SIEM / détection SOC  
- Signalement utilisateur ou métier  
- Logs système / réseau / applicatifs  
- Indicateurs de compromission (IOC)  
- Liste des actifs critiques et classification  
- Plans d’action et procédures d’escalade

## 7. Étapes détaillées du workflow  

### 7.1 Étape 1 : Détection & alerte  

- Détection automatisée (SIEM, EDR) ou manuelle (utilisateur, audit)  
- Ouverture de ticket incident cyber  
- Notation de la gravité selon grille CSIRT

### 7.2 Étape 2 : Qualification & priorisation  

- Analyse initiale par le SOC  
- Vérification de la compromission, périmètre impacté  
- Classification : faible / modéré / critique / majeur  
- Activation du CSIRT selon seuils de criticité

### 7.3 Étape 3 : Contention & éradication  

- Isolation des systèmes compromis  
- Interruption de connexions externes malveillantes  
- Suppression des fichiers malicieux, correctifs appliqués  
- Mise à jour des signatures / règles SIEM

### 7.4 Étape 4 : Reprise & communication  

- Vérification de l’intégrité et redémarrage des services  
- Communication interne et externe selon protocole  
- Notification CNIL si données personnelles affectées  
- Rédaction d’un rapport d’incident complet

### 7.5 Points de décision & contrôles qualité  

- Point de décision : incident grave ou critique → gestion de crise activée  
- Contrôle qualité : relecture rapport incident, validation RSSI, archivage centralisé  
- Revue post-mortem systématique pour tout incident classé critique

## 8. Enregistrements produits / Evidences

- Journal d’alerte initiale (horodatage, source)  
- Fichiers logs (système, réseau, applicatif)  
- Rapport d’analyse CSIRT  
- Chronologie de l’intervention  
- Plan d’action correctif et post-incident  
- Registre des notifications (ACPR, CNIL, clients le cas échéant)

## 9. Indicateurs de performance & SLA (KPIs)

| KPI                                         | Objectif               | Fréquence     |
|---------------------------------------------|-------------------------|---------------|
| Délai moyen de qualification d’un incident  | ≤ 1 heure              | Hebdomadaire  |
| Délai de résolution des incidents critiques | ≤ 24 heures            | Mensuel       |
| Taux d'incidents requalifiés en post-mortem | ≤ 5 %                  | Trimestriel   |
| % d’incidents notifiés dans les délais CNIL | 100 %                  | Trimestriel   |

## 10. Risques, points de vigilance & mesures de mitigation  

| Risque / Point sensible              | Action de mitigation                     |
|--------------------------------------|------------------------------------------|
| Retard de détection                  | Surveillance 24/7 via SOC + SIEM         |
| Mauvaise qualification               | Formation continue SOC + double validation |
| Communication inadaptée              | Communication pré-rédigée / validée DPO  |
| Redondance d’incidents similaires    | Capitalisation post-mortem systématique |

## 11. Systèmes / outils support & interfaces  

- SIEM (Splunk, QRadar, etc.)  
- EDR / XDR (CrowdStrike, SentinelOne)  
- Gestionnaire de tickets (Jira, ServiceNow)  
- Playbooks de réponse automatisée (SOAR)  
- Référentiels IOC / vulnérabilités (CERT, CVE)  
- Réseau VPN sécurisé d’intervention

## 12. Gestion des exceptions et escalade  

- Tout écart aux SLA ou contournement du processus standard doit faire l’objet :  
  - D’une documentation circonstanciée  
  - D’une validation par le RSSI ou le Comité Sécurité  
  - D’un retour d’expérience formalisé en post-incident  
- L’escalade vers la direction générale s’applique pour tout incident classé critique/majeur

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                        | Modification principale                    |
|---------|------------|-------------------------------|--------------------------------------------|
| 1.0     | 28/05/2025 | Consultant Senior Sécurité SI | Création initiale de la procédure CSIRT    |
| 1.1     |            |                               |                                            |
| 1.2     |            |                               |                                            |
