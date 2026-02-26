# PROCESSUS – gestion omnicanale des tickets (chat, mail, téléphone)

## 1. Objet et finalité

Assurer une prise en charge efficace, homogène et traçable des demandes clients reçues via les canaux digitaux et traditionnels (chat, mail, téléphone), dans le respect des engagements de qualité de service et de conformité réglementaire.

## 2. Champ d’application / Support Client & Expérience Utilisateur

Ce processus couvre toutes les demandes entrantes et sortantes gérées par les équipes de support client, quel que soit le canal d’origine, du premier contact à la résolution ou escalade.

## 3. Parties prenantes & RACI (rôles)

| Activité                      | Responsable (R) | Approbateur (A) | Consulté (C) | Informé (I) |
|-------------------------------|------------------|------------------|----------------|---------------|
| Traitement des tickets        | Support Client   | Team Leader      | DSI, Juridique | Qualité      |
| Affectation / dispatch        | Superviseur      | -                | -              | -             |
| Escalade                      | Support Client   | Responsable N2   | Juridique      | -             |
| Reporting                     | Qualité Service  | DAF              | COMEX          | -             |

## 4. Entrées, déclencheurs et fournisseurs (SIPOC – S)

- **Fournisseurs** : Clients, APIs canal, outils CRM, RPA
- **Entrées** : Ticket initial (chat, mail, appel), métadonnées (canal, client, horodatage)
- **Déclencheurs** : Réception d’une sollicitation via un des canaux clients

## 5. Macro-workflow BPMN / chaîne de valeur

### 5.1 Vue d’ensemble (diagramme texte)

1. Réception automatisée du ticket (via API/CRM omnicanal)
2. Attribution automatique ou manuelle selon la priorité/canal
3. Traitement initial (réponse, clarification, diagnostic)
4. Résolution directe OU escalade (technique/fonctionnelle)
5. Clôture avec traçabilité et envoi de satisfaction

### 5.2 Sous-processus clés

- Triage automatique des tickets entrants
- Détection de mots-clés sensibles (fraude, blocage)
- Traitement via base de connaissance ou robot de réponse
- Escalade avec transfert de contexte (via outil CRM)

### 5.3 Points de contrôle & jalons

- Ticket affecté < 2 minutes post-réception
- Réponse initiale client < 4h ouvrées
- Ticket ouvert > 24h : inclusion dans backlog prioritaire

## 6. Sorties et clients internes/externes (SIPOC – O/C)

- **Sorties** : Ticket résolu/fermé, fiche satisfaction, log activité
- **Clients** : Utilisateur final, équipes internes, Qualité/Conformité

## 7. Ressources & systèmes support (IT, data, fournisseurs)

- Outils CRM omnicanal (Zendesk, Salesforce, etc.)
- IA conversationnelle / chatbot
- Interfaces API canal / CTI
- Bases de connaissances, scripts, moteurs RPA

## 8. Exigences de conformité (REGS)

- RGPD : gestion des données personnelles client
- ACPR : obligations de réponse client et traçabilité
- ISO 9001 / 27001 : exigence qualité et sécurité de l’information
- PSD2 : vérification des réclamations liées aux paiements

## 9. Indicateurs de performance (KPIs) & seuils SLA

- Taux de résolution au premier contact (> 70%)
- Temps moyen de traitement (TMT) < 6h
- Score de satisfaction client (> 85%)
- Volume de tickets escaladés < 10%

## 10. Risques, gaspillages (Lean) et actions de mitigation

- **Risque** : Ticket non pris en charge > SLA
  - *Mitigation* : alerting temps réel, supervision
- **Gaspillage** : doublon de traitement, ressaisies
  - *Action* : automatisation du tri & intégration CRM
- **Risque** : perte de contexte intercanal
  - *Mitigation* : centralisation via outil unique

## 11. Interfaces & dépendances croisées (processus amont/aval)

- Amont : Portail client, formulaires en ligne, app mobile
- Aval : Traitement réclamation, déclenchement de remboursements, investigations

## 12. Plans d’amélioration continue (PDCA)

- **Plan** : veille satisfaction & analyse cause racine
- **Do** : amélioration des scripts et FAQ
- **Check** : audits mensuels qualitatifs sur 5% des tickets
- **Act** : évolutions logicielles et formation ciblée

## 13. Historique des versions (tableau)

| Version | Date       | Auteur               | Modifications principales               |
|---------|------------|----------------------|------------------------------------------|
| 1.0     | 2025-05-28 | Resp. Support Client | Création initiale du processus          |
