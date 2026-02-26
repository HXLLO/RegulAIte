# Procédures d'Information et de Transparence RGPD

| Champ | Valeur |
|-------|--------|
| **RÉFÉRENCE** | PROC-PRIVACY-001 |
| **CLASSIFICATION** | INTERNE |
| **VERSION** | 1.0 |
| **DATE D'APPROBATION** | 09 juin 2025 |
| **PROPRIÉTAIRE** | Équipe Protection des Données |
| **PÉRIODICITÉ DE RÉVISION** | Semestrielle |

## Approbation

| Rôle | Nom | Date |
|------|-----|------|
| DPO | Sophie Martineau | 09/06/2025 |
| Responsable Conformité | Julien Moreau | 09/06/2025 |

---

**Procédures d'Information et de Transparence RGPD**  
*Mise en œuvre opérationnelle des Articles 12-14*

## 1. Procédure de création d'une notice d'information

### 1.1 Identification du besoin

**Déclencheurs :**

- Nouveau traitement de données personnelles
- Modification substantielle d'un traitement existant
- Nouveau canal de collecte
- Évolution réglementaire
- Audit identifiant une lacune

**Responsable :** Privacy Champion du métier concerné

**Actions :**

- Compléter le formulaire d'identification de besoin (FORM-001)
- Transmettre au DPO dans les 48h
- Programmer un atelier d'analyse si nécessaire

### 1.2 Analyse des exigences

**Responsable :** DPO + Privacy Champion

**Étapes :**

1. **Classification du type de collecte**
   - ☐ Collecte directe → Application Article 13
   - ☐ Collecte indirecte → Application Article 14
   - ☐ Mixte → Application des deux articles

2. **Identification des informations obligatoires**
   - Utiliser la checklist RGPD-ART13 ou RGPD-ART14
   - Documenter les spécificités du traitement
   - Identifier les exceptions éventuelles

3. **Détermination du format et canal**
   - Notice contextuelle courte
   - Politique de confidentialité détaillée
   - Information personnalisée
   - Communication proactive

### 1.3 Rédaction de la notice

**Responsable :** Équipe métier + DPO

**Templates disponibles :**

- **TEMP-001** : Notice formulaire web
- **TEMP-002** : Notice application mobile
- **TEMP-003** : Notice collecte téléphonique
- **TEMP-004** : Notice collecte physique
- **TEMP-005** : Notice API/partenaires

**Règles de rédaction :**

**Structure imposée :**
1. Qui collecte ? (Identité + DPO)
2. Quelles données ? (Catégories)
3. Pourquoi ? (Finalités + base légale)
4. Combien de temps ? (Conservation)
5. Qui y accède ? (Destinataires)
6. Quels droits ? (Droits + exercice)
7. Contact ? (DPO + réclamation)

**Contraintes techniques :**

- Maximum 500 mots pour notice contextuelle
- Score lisibilité Flesch > 60
- Niveau de lecture ≤ Bac+2
- Liens vers informations détaillées

### 1.4 Validation

**Circuit de validation :**
```
Rédaction métier → DPO → Juridique (si complexe) → RSSI (si technique) → Validation finale DPO
```

**Critères de validation :**

- ☐ Exhaustivité des informations obligatoires
- ☐ Exactitude factuelle
- ☐ Clarté et compréhensibilité
- ☐ Conformité template et charte graphique
- ☐ Liens fonctionnels
- ☐ Conformité accessibilité

**Délai de validation :** 5 jours ouvrés

### 1.5 Implémentation

**Responsable :** Équipes techniques + DPO

**Étapes :**

1. **Intégration technique**
   - Développement selon spécifications
   - Tests fonctionnels
   - Tests d'accessibilité

2. **Tests utilisateur**
   - Panel représentatif (5 personnes minimum)
   - Test de compréhension
   - Mesure temps de lecture
   - Feedback sur clarté

3. **Mise en production**
   - Déploiement progressif (A/B testing si possible)
   - Monitoring des métriques d'engagement
   - Documentation de mise en œuvre

### 1.6 Documentation et traçabilité

**Éléments à archiver :**

- Formulaire de demande initial
- Analyses et justifications
- Versions successives de la notice
- Validations obtenues
- Preuve de mise en ligne/diffusion
- Retours utilisateurs

**Durée de conservation :** 5 ans après fin d'utilisation

## 2. Procédure de mise à jour des informations

### 2.1 Détection des besoins de mise à jour

**Sources de déclenchement :**

**Automatiques :**
- Modification du registre des traitements
- Alerte du système de veille réglementaire
- Notification de changement par un métier

**Périodiques :**
- Revue trimestrielle systématique
- Audit de conformité
- Feedback clients/utilisateurs

**Événementielles :**
- Fusion/acquisition
- Nouveau partenaire
- Évolution technologique majeure

### 2.2 Évaluation de l'impact

**Responsable :** DPO + Privacy Champion concerné

**Grille d'évaluation :**

| Critère | Impact faible | Impact moyen | Impact fort |
|---------|---------------|--------------|-------------|
| **Nombre de personnes** | <1000 | 1000-10000 | >10000 |
| **Sensibilité données** | Standard | Financières | Sensibles Art.9 |
| **Nature changement** | Technique | Organisationnel | Finalité |
| **Urgence** | >30 jours | 15-30 jours | <15 jours |

**Décisions selon impact :**

- **Faible** : Mise à jour silencieuse
- **Moyen** : Notification passive (site web, app)
- **Fort** : Communication proactive (email, courrier)

### 2.3 Processus de mise à jour

**Préparation**
- **Jour J-30** : Planification
- **Jour J-15** : Rédaction nouvelle version
- **Jour J-7** : Validation
- **Jour J-2** : Préparation communication
- **Jour J** : Mise en œuvre

**Communication aux personnes concernées**

Template email de notification :

```
Objet : Mise à jour - Protection de vos données personnelles

Bonjour [Prénom],

Nous mettons à jour notre politique de confidentialité pour [raison].

📋 Principales modifications :
• [Changement 1]
• [Changement 2]

🔗 Consulter la nouvelle version : [lien]
❓ Questions ? dpo@neofinancia.eu

Cette mise à jour prend effet le [date].

L'équipe Neo Financia
```

**Mise à jour technique**

- Deployment des nouvelles notices
- Archivage des versions précédentes
- Tests de régression
- Mise à jour du registre des traitements

### 2.4 Suivi post-mise à jour

**Métriques à surveiller :**

- Taux d'ouverture des emails de notification
- Consultation de la nouvelle politique
- Questions reçues au DPO
- Demandes d'exercice de droits

**Actions correctives si nécessaire :**

- Communication de clarification
- FAQ complémentaire
- Modification de la notice si ambiguïtés

## 3. Procédure de traitement des demandes d'information

### 3.1 Réception et qualification

**Canaux de réception :**

- Email DPO : dpo@neofinancia.eu
- Formulaire web dédié
- Espace client sécurisé
- Courrier postal
- Signalement via support client

**Première qualification :**

**Type de demande :**
- ☐ Information générale (politique de confidentialité)
- ☐ Information personnalisée (mes données)
- ☐ Clarification sur un traitement
- ☐ Exercice d'un droit (traitement séparé)

**Délai d'accusé de réception :** 48h maximum

### 3.2 Vérification d'identité

**Niveau requis selon le type :**

| Type de demande | Niveau de vérification | Méthode |
|-----------------|------------------------|---------|
| **Information générale** | Aucune | Réponse directe |
| **Information sur traitements non-sensibles** | Simple | Email + question sécurité |
| **Information personnalisée** | Standard | Connexion espace client |
| **Information sensible** | Renforcé | Pièce d'identité + validation téléphonique |

**Procédure de vérification renforcée :**

- Demande de pièce d'identité (scan/photo)
- Vérification par équipe dédiée (48h)
- Validation téléphonique si doute
- Documentation de la vérification

### 3.3 Collecte des informations

**Responsabilités :**

- **DPO** : Coordination et validation
- **Équipes métier** : Fourniture des éléments techniques
- **IT** : Extraction des données si nécessaire
- **Juridique** : Conseil sur aspects complexes

**Informations à collecter selon l'article 15 RGPD :**

- Finalités du traitement
- Catégories de données personnelles
- Destinataires ou catégories de destinataires
- Durée de conservation
- Droits de la personne concernée
- Source des données (si collecte indirecte)
- Existence d'une prise de décision automatisée
- Transferts vers pays tiers et garanties

### 3.4 Préparation et envoi de la réponse

**Format de réponse standardisé :**

```
Madame/Monsieur [Nom],

Suite à votre demande du [date], référence [numéro], nous vous 
communiquons les informations suivantes concernant le traitement 
de vos données personnelles par Neo Financia.

1. TRAITEMENTS VOUS CONCERNANT
[Tableau structuré par traitement]

2. VOS DONNÉES PERSONNELLES
[Liste des catégories détenues]

3. DESTINATAIRES
[Liste des catégories d'accès]

4. CONSERVATION
[Durées par catégorie]

5. VOS DROITS
[Rappel modalités d'exercice]

Pour toute question : dpo@neofinancia.eu

Cordialement,
Sophie Martineau
Délégué à la Protection des Données
```

**Modalités d'envoi :**

- Email sécurisé (si demande par email)
- Espace client (si accès disponible)
- Courrier recommandé (si demande par courrier)
- Remise en main propre (cas exceptionnels)

### 3.5 Suivi et archivage

**Documentation obligatoire :**

- Demande initiale
- Éléments de vérification d'identité
- Correspondances internes
- Réponse fournie
- Accusé de réception si courrier

**Indicateurs de suivi :**

- Délai de traitement
- Taux de satisfaction (enquête post-traitement)
- Demandes de clarification ultérieures
- Réclamations éventuelles

## 4. Procédure spécifique Article 14 (Collecte indirecte)

### 4.1 Identification des cas de collecte indirecte

**Sources typiques chez Neo Financia :**

- Partenaires commerciaux (Mangopay, Lemonway)
- Bases de données publiques (SIRENE, cadastre)
- Bureaux de crédit et fichiers bancaires
- Réseaux sociaux (données publiques uniquement)
- Sources de vérification KYC/LCB-FT

### 4.2 Processus d'information

**Étape 1 : Identification des personnes concernées**

- Extraction des coordonnées disponibles
- Vérification de l'exactitude des contacts
- Priorisation selon criticité des données

**Étape 2 : Préparation de la communication**

- Adaptation du message selon la source
- Personnalisation si volume le permet
- Choix du canal (email privilégié, courrier si nécessaire)

**Étape 3 : Information dans les délais**
- **Délai standard** : 1 mois maximum après obtention
- **Délai lors communication** : Dès le premier contact
- **Délai divulgation tiers** : Avant la première divulgation

**Template spécifique collecte indirecte :**

```
Objet : Information - Traitement de vos données personnelles

Madame/Monsieur,

Neo Financia a obtenu certaines de vos données personnelles 
auprès de [source] dans le cadre de [finalité].

🔍 Données concernées : [catégories]
📋 Source : [identification précise]
🎯 Finalité : [objectif du traitement]
⚖️ Base légale : [fondement juridique]

Vos droits restent inchangés : accès, rectification, effacement...

Plus d'informations : neofinancia.eu/confidentialite
Contact : dpo@neofinancia.eu

L'équipe Neo Financia
```

### 4.3 Gestion des exceptions

**Exception 1 : Personne déjà informée**

- Vérification documentée de l'information antérieure
- Conservation de la preuve (email, accusé réception)
- Documentation dans le registre des traitements

**Exception 2 : Information impossible**

- Tentatives de contact documentées
- Recherche dans bases publiques
- Justification de l'impossibilité

**Exception 3 : Effort disproportionné**

- Analyse coût/bénéfice documentée
- Évaluation du nombre de personnes concernées
- Mise en place de mesures alternatives (information publique)

**Fiche de justification d'exception :**

```
FICHE EXCEPTION ARTICLE 14.5

Traitement : [nom]
Exception invoquée : ☐ 14.5.a ☐ 14.5.b ☐ 14.5.c ☐ 14.5.d

Justification détaillée :
[Description de la situation]

Éléments de preuve :
☐ Tentatives de contact documentées
☐ Analyse de proportionnalité
☐ Avis juridique joint

Mesures compensatoires :
[Actions pour protéger les droits]

Validé par : Sophie Martineau, DPO
Date : [date]
Révision prévue : [date + 12 mois]
```

## 5. Outils et modèles

### 5.1 Checklist de conformité

**Article 12 - Modalités :**

- ☐ Information concise, transparente, compréhensible
- ☐ Termes clairs et simples
- ☐ Fournie par écrit (électronique de préférence)
- ☐ Information gratuite
- ☐ Délai 1 mois (extensible 3 mois avec justification)
- ☐ Vérification identité proportionnée
- ☐ Refus motivé si demande infondée

**Article 13 - Collecte directe :**

- ☐ Identité responsable traitement
- ☐ Coordonnées DPO
- ☐ Finalités et base juridique
- ☐ Intérêts légitimes (si applicable)
- ☐ Destinataires
- ☐ Transferts pays tiers
- ☐ Durée conservation
- ☐ Droits personne concernée
- ☐ Retrait consentement (si applicable)
- ☐ Réclamation autorité
- ☐ Caractère obligatoire
- ☐ Décision automatisée

**Article 14 - Collecte indirecte :**

- ☐ Toutes informations Article 13
- ☐ Catégories données personnelles
- ☐ Source des données
- ☐ Délais respectés (1 mois max)
- ☐ Exceptions documentées si applicable

### 5.2 Templates techniques

**Intégration formulaire web :**

```html
<div class="gdpr-notice" role="region" aria-labelledby="privacy-title">
  <h3 id="privacy-title">🔒 Protection de vos données</h3>
  <div class="notice-content">
    <p><strong>Finalité :</strong> [Objectif du formulaire]</p>
    <p><strong>Base légale :</strong> [Fondement]</p>
    <p><strong>Conservation :</strong> [Durée]</p>
    <p><strong>Vos droits :</strong> 
       <a href="/droits-donnees" target="_blank" 
          aria-label="En savoir plus sur vos droits">
          Accès, rectification, suppression
       </a>
    </p>
  </div>
  <p class="contact-info">
    Questions ? <a href="mailto:dpo@neofinancia.eu">dpo@neofinancia.eu</a>
  </p>
</div>
```

**API Documentation (partenaires) :**

```json
{
  "privacy_notice": {
    "data_controller": "Neo Financia",
    "dpo_contact": "dpo@neofinancia.eu",
    "purpose": "API transaction processing",
    "legal_basis": "Contract execution",
    "data_categories": ["transaction_data", "authentication"],
    "retention": "5 years after last transaction",
    "rights": "/api/privacy/rights",
    "policy_url": "https://neofinancia.eu/api-privacy"
  }
}
```

---

**Document validé par :**

- Sophie Martineau, DPO - 09/06/2025
- Julien Moreau, Responsable Conformité - 09/06/2025

**Prochaine révision :** 09 décembre 2025