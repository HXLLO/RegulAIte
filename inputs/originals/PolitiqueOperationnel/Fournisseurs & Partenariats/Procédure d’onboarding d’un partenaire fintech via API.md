# PROCÉDURE – onboarding d’un partenaire fintech via API

## 1. Objet et finalité  

Cette procédure décrit les étapes opérationnelles à suivre pour l’onboarding technique et contractuel d’un partenaire fintech via une intégration API, dans le cadre des partenariats de Neo Financia. Elle garantit un cadre sécurisé, conforme et efficient pour le démarrage des services interconnectés.

## 2. Champ d’application / Fournisseurs & Partenariats  

Cette procédure s’applique à tout nouveau partenariat impliquant une communication technique via API, notamment dans les domaines du paiement, de la gestion de données, ou des services bancaires as-a-service.

## 3. Références réglementaires et normatives (REGS)  

- Règlement général sur la protection des données (RGPD)  
- Directive européenne sur les services de paiement (DSP2)  
- Normes ISO/IEC 27001 et 27017  
- Lignes directrices EBA sur l’externalisation  
- Recommandations de l’ACPR sur les prestataires critiques  

## 4. Définitions & acronymes  

- **API** : Application Programming Interface  
- **KYS** : Know Your Supplier  
- **DPIA** : Data Protection Impact Assessment  
- **SRM** : Supplier Relationship Management  
- **PKI** : Public Key Infrastructure  
- **TTP** : Third-Party Provider  

## 5. Rôles et responsabilités (RACI)  

| Activité / Rôle                    | Partenariats | IT/API | RSSI | Juridique | DPO | Conformité | Métier demandeur |
|----------------------------------|--------------|--------|------|-----------|-----|------------|------------------|
| Sélection du partenaire          | R            | C      | C    | I         | I   | A          | A                |
| Signature contractuelle          | A            | I      | I    | R          | C   | C          | C                |
| Évaluation sécurité/API          | C            | R      | A    | I         | I   | C          | C                |
| DPIA et documentation RGPD       | I            | I      | C    | I         | R   | A          | C                |
| Déploiement technique & tests    | I            | A      | C    | I         | I   | I          | C                |

## 6. Prérequis / Entrées nécessaires  

- Demande métier formalisée  
- Validation du modèle économique  
- Informations techniques sur l’API du partenaire  
- Attestations conformité RGPD / Sécurité / DSP2  
- Analyse de risque fournisseur  
- Accord de confidentialité signé  

## 7. Étapes détaillées du workflow  

### 7.1 Étape 1 : Sélection et validation du partenaire  

- Analyse de la fiche KYS  
- Due diligence conformité et sécurité  
- Présentation en comité fournisseurs

### 7.2 Étape 2 : Évaluation technique & contractualisation  

- Revue des spécifications API  
- Évaluation sécurité (audit code/API, PKI, authentification)  
- Rédaction et signature du contrat & SLA

### 7.3 Étape 3 : Intégration, tests et go-live  

- Ouverture des environnements sandbox  
- Tests techniques (authentification, volumétrie, charge)  
- Mise en production et déclenchement du monitoring  
- Revue post-déploiement (30 jours)

### 7.4 Points de décision & contrôles qualité  

- Go/No-Go Comité Fournisseurs  
- Validation DPIA par le DPO  
- Revue sécurité obligatoire avant déploiement  
- Mise à jour du référentiel SRM

## 8. Enregistrements produits / Evidences  

- Fiche d’évaluation fournisseur (KYS)  
- DPIA et documentation RGPD  
- Log de tests API  
- PV de Comité Go/No-Go  
- Relevé de SLA signé  

## 9. Indicateurs de performance & SLA (KPIs)  

- Taux d’onboarding dans les délais contractuels (< 30 jours)  
- % de tests d’API réussis (≥ 95%)  
- Taux d’incidents critiques 1er mois (objectif : 0)  
- Niveau de complétude des DPIA (100 %)

## 10. Risques, points de vigilance & mesures de mitigation  

- **Risque technique** : intégration API incomplète → validation par checklist de tests  
- **Risque RGPD** : données sensibles mal gérées → DPIA obligatoire  
- **Risque sécurité** : API non conforme → audit sécurité + tests pentest  
- **Risque contractuel** : flou sur les responsabilités → clause SLA et auditabilité

## 11. Systèmes / outils support & interfaces  

- SRM Neo Financia  
- Portail API Gateway  
- Jira (suivi de tickets d’intégration)  
- SharePoint (archivage des documents)  
- Outil DPIA (OneTrust ou équivalent)  

## 12. Gestion des exceptions et escalade  

- Escalade au Responsable Sécurité ou au DPO en cas de faille détectée  
- Arbitrage Comité Fournisseurs en cas de blocage contractuel ou juridique  
- Documentation obligatoire de toute dérogation dans le SRM

## 13. Historique des versions (tableau)

| Version | Date       | Auteur             | Modifications principales               |
|---------|------------|--------------------|------------------------------------------|
| 1.0     | 2024-05-28 | Direction Partenariats | Création initiale                       |
| 1.1     | À venir    | À compléter        | —                                        |
