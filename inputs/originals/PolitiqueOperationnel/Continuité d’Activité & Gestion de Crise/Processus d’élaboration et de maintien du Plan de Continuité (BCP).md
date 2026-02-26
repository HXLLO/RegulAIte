# PROCESSUS – élaboration et de maintien du Plan de Continuité (BCP)

## 1. Objet et finalité  

Ce processus a pour objet de définir les modalités d’élaboration, de mise à jour, de validation et de maintien opérationnel du Plan de Continuité d’Activité (BCP) de Neo Financia. Il vise à garantir la résilience de l’organisation en cas de perturbation majeure (incident SI, crise sanitaire, cyberattaque, sinistre physique, etc.), en assurant la poursuite ou la reprise rapide des activités critiques.

## 2. Champ d’application / Continuité d’Activité & Gestion de Crise  

Ce processus couvre l’ensemble des entités, fonctions critiques, systèmes et prestataires stratégiques de Neo Financia en France et au Royaume-Uni. Il s’applique aux activités bancaires digitales (crédit, paiement, épargne, KYC, etc.), ainsi qu’aux fonctions support (IT, RH, finance, conformité, etc.).

## 3. Parties prenantes & RACI (rôles)

| Rôle                            | Responsable | Acteurs | Consultés | Informés |
|---------------------------------|-------------|---------|-----------|----------|
| Responsable Continuité d’Activité (RCA) |     X       |         |     X     |    X     |
| Direction Métier (par domaine) |             |    X    |           |    X     |
| Direction Informatique         |             |    X    |     X     |    X     |
| Direction Sécurité SI (RSSI)   |             |         |     X     |    X     |
| DPO / Conformité                |             |         |     X     |    X     |
| Top Management / COMEX         |             |         |     X     |    X     |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

- Sources / Fournisseurs :
  - Analyse d’impact métier (BIA)
  - Cartographie des risques opérationnels
  - Retour d’expérience (REX) post-crise
  - Lignes directrices EBA/ACPR
- Déclencheurs :
  - Création ou évolution de processus critique
  - Audit, test BCP, incident significatif
  - Échéance annuelle de revue

## 5. Macro-workflow BPMN / chaîne de valeur  

### 5.1 Vue d’ensemble (diagramme texte + numérotation)

1. Identifier les processus critiques via la BIA  
2. Évaluer les impacts métiers et définir les objectifs de continuité (RTO/RPO)  
3. Élaborer les scénarios de crise et plans de réponse associés  
4. Documenter le BCP consolidé  
5. Valider le BCP avec les métiers et la direction  
6. Tester les plans (tests papier, techniques, de crise)  
7. Mettre à jour suite aux tests, incidents ou changements d’organisation  
8. Diffuser, former et sensibiliser les parties prenantes  
9. Archiver et tracer les évolutions du BCP

### 5.2 Sous-processus clés

- Réalisation de l’analyse d’impact métier (BIA)
- Définition des solutions de continuité (IT, humaine, site de repli)
- Rédaction des fiches de continuité par unité métier
- Coordination avec les plans ITDR (Disaster Recovery)
- Organisation des tests annuels et revues de conformité

### 5.3 Points de contrôle & jalons

- Validation formelle des RTO/RPO par les directions métiers
- Réalisation annuelle des tests BCP
- Enregistrement des résultats de test et plans d’action correctifs
- Revue semestrielle du BCP en comité de continuité

## 6. Sorties et clients internes/externes (SIPOC – O/C)

- Sorties :
  - Plan de continuité d’activité complet (BCP)
  - Registre des RTO/RPO
  - Rapports de tests et de mise à jour
- Clients :
  - Directions métiers
  - COMEX
  - ACPR/EBA (en cas de contrôle)
  - Auditeurs internes/externes

## 7. Ressources & systèmes support (IT, data, fournisseurs)

- Outil GRC (Governance, Risk & Compliance) pour la cartographie des processus
- Outil de gestion documentaire (BCMS)
- Plateforme de test (scénarios, communication de crise)
- Base des incidents et retours d’expérience
- Fournisseurs d’infogérance / cloud pour ITDR
- Sites de secours physique

## 8. Exigences de conformité (ACPR, EBA, ISO 22301, ISO 27001)

- Lignes directrices EBA sur la résilience opérationnelle (EBA/GL/2021/07)
- Instruction ACPR sur la continuité d’activité
- ISO 22301:2019 – Système de management de la continuité d’activité
- ISO 27001 – Intégration avec le SMSI

## 9. Indicateurs de performance (KPIs) & seuils SLA

| Indicateur                             | Seuil cible         | Fréquence |
|----------------------------------------|----------------------|-----------|
| % de couverture BCP des processus critiques | ≥ 100 %           | Annuel    |
| Taux de conformité des tests BCP       | ≥ 95 %               | Annuel    |
| Délais de mise à jour post-incident    | ≤ 15 jours ouvrés    | À l’occurrence |
| Nombre de plans BCP non testés         | 0                    | Trimestriel |

## 10. Risques, gaspillages (Lean) et actions de mitigation

- **Risques** : BCP obsolète, solutions non testées, dépendance fournisseur non maîtrisée
- **Gaspillages** : Documentation redondante, absence de centralisation, reporting manuel
- **Actions de mitigation** :
  - Automatisation des alertes de révision
  - Intégration ITDR/BCP dans une même gouvernance
  - Cartographie des interdépendances systèmes-métiers

## 11. Interfaces & dépendances croisées (processus amont/aval)

- **Amont** : Gestion des risques opérationnels, analyse BIA, gouvernance IT
- **Aval** : Gestion de crise, reprise IT (ITDR), réponse aux incidents (CSIRT)

## 12. Plans d’amélioration continue (PDCA)

- **Plan** : Réaliser une cartographie exhaustive des processus critiques
- **Do** : Tester les BCP et valider avec les métiers
- **Check** : Exploiter les retours de tests, audits et incidents
- **Act** : Adapter les plans et renforcer la culture de continuité

## 13. Historique des versions (tableau)

| Version | Date       | Auteur                         | Modification principale                      |
|---------|------------|--------------------------------|----------------------------------------------|
| 1.0     | 28/05/2025 | Responsable Continuité d’Activité | Création initiale du processus BCP         |
|         |            |                                |                                              |
