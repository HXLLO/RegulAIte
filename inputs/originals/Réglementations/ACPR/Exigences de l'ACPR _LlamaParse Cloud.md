# ACPR

# SECRÉTARIAT GÉNÉRAL

# Exigences en matière de qualité des données

# pour les organismes et groupes d’assurance

# soumis à la Directive Solvabilité 2

(Version du 08/11/2023)
---
# Table des matières

1. Introduction.................................................................................................................................... 2
2. Gouvernance................................................................................................................................... 3
1. Périmètre des données SII....................................................................................................... 3
2. Document cadre organisant le dispositif de maitrise de la qualité des données ................... 4
3. Rôles et responsabilités........................................................................................................... 4
4. Comitologie ............................................................................................................................. 5
5. Les instruments de suivi .......................................................................................................... 6
6. Les critères de qualité des données ........................................................................................ 7
3. Enjeux en matière de qualité des données externes ..................................................................... 8
1. Identification des prestataires et partenaires en matière de qualité des données................ 8
2. Contractualisation et gestion des risques liés aux données externes..................................... 9
4. Le répertoire ................................................................................................................................... 9
5. Traçabilité ..................................................................................................................................... 11
1. Cartographies ........................................................................................................................ 11
2. Collecte & traitements .......................................................................................................... 11
6. Le contrôle interne ....................................................................................................................... 12
1. Gestion et cartographie des risques...................................................................................... 12
2. Dispositif de contrôle permanent ......................................................................................... 12
3. Fonction actuarielle............................................................................................................... 13
4. Audit interne ......................................................................................................................... 13
7. Précisions dans le cas de groupes prudentiels ............................................................................. 13

# 1. Introduction

Le présent document (la « Notice » dans la suite) est destiné, dans un souci de transparence et de prévisibilité, à indiquer la manière dont l’Autorité de contrôle prudentiel et de résolution (« l’ACPR ») entend contrôler le respect de la réglementation Solvabilité 2. Cette réglementation s’appuie sur la directive 2009/138/CE (« la directive »), le règlement délégué (UE) 2015/35 (« le règlement délégué »), amendés notamment par le règlement délégué (UE) 2019/981 et la directive (UE) et 2014/51/UE.

La Notice vise à clarifier certaines modalités d’application de la règlementation Solvabilité 2, en particulier les articles R351-2, R351-13, R352-5, R352-19, R352-22, R352-24, R354-6, R354-7, R356-50 du code des assurances, les articles 19, 20, 21, 27, 219, 230, 231, 244, 260, 264, 265 et 272 du règlement délégué (UE) n°2015/35 qui regroupent les principales exigences réglementaires relatives à la qualité des données utilisées aux fins des calculs prudentiels Solvabilité II, et, lorsque cela est nécessaire, à apporter des précisions aux orientations publiées par l'Autorité européenne de surveillance des assurances et des pensions professionnelles (« l’AEAPP ») notamment les orientations 48, 52 et 53 relatives au système de gouvernance (EIOPA-BoS-14/253) et les orientations 27, 50, 55, 56 et 57 relatives à l’utilisation de modèles internes (EIOPA-BoS-14/180) auxquelles l’ACPR s’est.
---
déclarée conforme par avis de conformité publiés au registre de l’ACPR l’ACPR le 1ᵉʳ décembre 2023.

Cette Notice ne couvre pas de façon exhaustive les exigences de la réglementation Solvabilité 2 et ne saurait prévaloir sur les dispositions de la réglementation applicable.

La présente Notice est applicable à compter du jour de sa publication au registre officiel de l’ACPR.

Aux fins de la présente Notice, les acronymes « SCR » et « MCR » désigneront respectivement le capital de solvabilité requis et le minimum de capital requis.

Sauf mention contraire, dans cette Notice, « l’entreprise » correspond aux organismes d’assurance ou de réassurance relevant du régime « Solvabilité II » mentionnés aux articles L. 310-3-1 du code des assurances, L. 211-10 du code de la mutualité ou L. 931-6 du code de la sécurité sociale.

Les éléments applicables aux entreprises s’appliquent mutatis mutandis aux groupes mentionnés à l’article L. 356-1 du code des assurances et faisant l’objet du contrôle de groupe mentionné aux deuxième et troisième alinéas de l’article L. 356-2 du code des assurances. Cette Notice introduit également des dispositions spécifiques aux groupes.

L’application du principe de proportionnalité n’exonère pas l’entreprise de se conformer aux exigences en termes de maitrise de la qualité des données précisées par la réglementation Solvabilité 2, en particulier pour la réalisation des calculs prudentiels. Ainsi, les dispositifs opérationnels ou les bonnes pratiques identifiés dans la Notice, s’ils sont correctement mis en œuvre, constituent un socle général devant, par défaut, permettre à l’entreprise de s’assurer une qualité des données suffisante.

L’entreprise conserve toutefois la responsabilité de définir un dispositif de qualité des données adapté à sa situation en tenant compte de l’ampleur, de la nature ou de la complexité des risques auquel elle est exposée (par exemple du moindre niveau de risque opérationnel ou assurantiel porté par ses opérations d’assurance, ou au regard de la simplicité de cheminement et de transformation des données ou encore du profil des risques assurés). Dès lors, l’entreprise peut utiliser les dispositifs mentionnés dans cette Notice comme socle, tout en les adaptant sur différents registres, comme notamment, et sans viser l’exhaustivité, la granularité ou les fréquences de mise à jour et de contrôle.

Quelle que soit l’organisation retenue en matière de maitrise de la qualité des données, l’entreprise doit être en capacité de démontrer que cette organisation répond aux objectifs précisés par la réglementation et régulièrement rappelés dans cette Notice.

# 2. Gouvernance

# 2.1. Périmètre des données SII

Les données visées par les chapitres suivants doivent s’entendre comme l’ensemble des données concourant aux calculs réalisés dans le cadre de la réglementation Solvabilité II afin d’établir principalement :

- les provisions techniques prudentielles ;
- les paramètres propres à l’entreprise ou au groupe (respectivement « USP » et « GSP ») ;
- l’ensemble des informations calculées à l’aide d’un modèle interne partiel ou total ;
---
Au titre du respect des exigences précisées dans les articles 266 et 258 §1 alinéas h et j du règlement délégué, l’entreprise peut utilement étendre les dispositions aux données suivantes :

- le capital de solvabilité requis (qu’il soit calculé en formule standard ou en utilisant des paramètres spécifiques) et le minimum de capital de solvabilité requis ;
- les éléments composant le bilan prudentiel ;
- plus largement, l’ensemble des éléments des états prudentiels Solvabilité II.

Les conclusions de l'EIRS1 sur la capacité de l'entreprise à faire face à certains évènements adverses doivent être robustes, ce qui induit de les fonder sur des données de qualité qui sont, pour une bonne part, les mêmes que les données critiques utilisées pour établir les informations transmises à l’autorité de contrôle ou à destination du public.

Par ailleurs, le périmètre des données inclut l’ensemble des branches, lignes, segments d’activités d’assurance menées par l’entreprise et ce, quelle que soit l’organisation retenue pour les réaliser (unités opérationnelles, marques commerciales, …).

De plus, le périmètre des données tient compte de leur dimension transversale i.e. depuis les outils de gestion (contrats, sinistres) jusqu’aux états prudentiels en passant par les outils de calcul.

Enfin, les données en provenance de sous-traitants (délégataires de gestion contrats/sinistres, gestionnaires d’actifs…) et de partenaires (courtiers, réassureurs, autres fournisseurs de données…), dès lors qu’elles concourent directement ou indirectement à la production des données visées au paragraphe 11 rentrent également dans le périmètre.

Dans la suite, l’ensemble de ces données sera nommé de façon générique « Données SII ».

# 2.2. Document cadre organisant le dispositif de maitrise de la qualité des données

L’entreprise conçoit et formalise un ou des documents (processus et procédures) organisant le dispositif de maitrise de la qualité des données. Afin d’engager toutes les parties prenantes dans le dispositif de qualité des données, ce corpus documentaire est validé par la direction générale ou le directoire (article 258 § 1 alinéas a, b et f du règlement délégué) qui le promeut au sein de l’entreprise. Ce corpus documentaire est revu au moins annuellement et incorpore à cette occasion les évolutions internes et réglementaires.

Ce document ou corpus documentaire comporte les points suivants :

- le détail du périmètre des données couvertes par le dispositif ;
- les rôles et responsabilités des parties prenantes à la qualité des données ;
- la comitologie mise en place ;
- la définition des critères de qualité des données (dont la notion de criticité) ;
- les instruments de suivi.

# 2.3. Rôles et responsabilités

Pour satisfaire aux exigences de l’article 258 §1 alinéa b du règlement délégué, la gestion de la qualité des données doit être organisée afin que les fonctions et responsabilités des différentes parties prenantes soient clairement assignées. À ce titre, l’entreprise désigne un responsable (« responsable QDD » dans la suite), le cas échéant assisté d’une équipe dédiée, qui dispose d’une vision transversale sur les données SII. En fonction de la nature, de

1 Évaluation Interne des Risques et de la Solvabilité (ORSA en anglais)
---
l’ampleur et de la complexité des risques, ce responsable peut exercer d’autres fonctions au sein de l’entreprise, à condition de se prémunir de tout conflit d’intérêt potentiel². Le responsable QDD exerce ses missions afin :

- d’être le garant du corpus documentaire encadrant la qualité des données y compris le répertoire (cf. infra),
- de piloter le dispositif de maitrise de la qualité des données, animer les comités, organiser le contrôle continu des données, consolider les résultats des contrôles et impulser le processus d’amélioration continue des données,
- d’évaluer le risque porté par les projets internes (dont les projets informatiques) en matière de qualité de données,
- de participer à la contractualisation des accords d’externalisation quand ceux-ci sont susceptibles d’avoir des impacts sur la qualité des données : par exemple, la prise en compte des exigences en matière de qualité des données dans les accords d’externalisation en fournissant des clauses standards et l'annexe type évoquée en section 3.2.

En fonction de la taille des entreprises et de la complexité des calculs règlementaires selon le type d’activité, il est par ailleurs conseillé de :

- nommer des personnes « relais » au sein des fonctions opérationnelles impliquées dans les calculs prudentiels (par exemple : gestion des contrats, gestion des sinistres, gestion des actifs, comptabilité, actuariat, informatique…). Ces relais peuvent ainsi contribuer à la mise à jour du répertoire des données, à la formalisation du cheminement et des transformations des données, coordonner la réalisation des contrôles opérationnels en respectant les objectifs de qualité définis (cf. infra) et animer le processus d’amélioration continue de la qualité des données dans leur fonction ;
- de désigner des propriétaires des données au sein des fonctions opérationnelles impliquées dans les calculs prudentiels, responsables de la qualité desdites données et de leur amélioration continue.
- En outre, la qualité des données doit être intégrée au contrôle interne de l’organisme : la fonction de gestion des risques incorpore les risques inhérents à la non qualité des données dans la cartographie des risques de l’entreprise ;
- le système de contrôle interne garantit la conception, le recensement et la réalisation :
- - des contrôles opérationnels (dits de 1ᵉʳ niveau) concourant à la maitrise des risques identifiés dans la cartographies des risques,
- des contrôles de 2ⁿᵈ niveau relatifs au risque de non qualité des données ;

la fonction d’audit interne intègre le risque de non qualité des données dans son univers d’audit et évalue le dispositif de contrôle de la qualité des données ;
- la fonction actuarielle apprécie la suffisance et la qualité des données utilisées dans le calcul des provisions techniques prudentielles. Le cas échéant, elle émet des recommandations visant à améliorer la qualité des données.

# 2.4. Comitologie

L’article 258 §1 alinéa k dispose que « l’entreprise instaure des lignes de reporting claires, garantissant la transmission rapide des informations à toutes les personnes qui en ont besoin, d'une manière leur permettant de reconnaître l'importance de ces informations au

² A titre d’exemple, pour des petites entreprises ayant une activité unique, ce responsable peut être un dirigeant effectif ou un des responsables de fonction clé.
---
regard de leurs responsabilités respectives ». L’entreprise met ainsi en place un système adapté à la nature, l’ampleur et la complexité des risques - de transmission d’information permettant :

- aux instances de gouvernance, notamment la direction effective, de disposer des éléments essentiels relatifs à la qualité des données pour faciliter leur prise de décision ;
- aux autres personnes impliquées dans le dispositif de qualité des données d’être en mesure de remonter ou recevoir les informations pertinentes pour la réalisation de leur mission.

# Dispositions spécifiques aux entreprises de taille significative ou portant des risques complexes

i.e. celles pour lesquelles l’ampleur, la nature ou la complexité des risques limite l’application du principe de proportionnalité - ou aux entreprises recourant à des modèles internes ou des paramètres propres.

Pour les entreprises de taille significative ou portant des risques complexes ou pour les entreprises recourant à des modèles internes ou des paramètres propres, il est recommandé de créer un comité de gouvernance et de pilotage des données SII dont les principales missions sont de :

- surveiller, via des tableaux de bord, les indicateurs de qualité déduits des résultats agrégés des contrôles participant à l’évaluation de la qualité des données ;
- arbitrer les projets, définir les priorités et allouer les budgets nécessaires à la maitrise de la qualité des données ;
- décider du traitement des incidents majeurs et de leur plan de remédiation à plus long terme ;
- veiller à ce que les décisions soient déclinées en feuilles de route à destination des équipes opérationnelles participant au dispositif de maitrise de la qualité des données.

La direction générale ou son représentant mandaté à cet effet préside cette instance qui rassemble les principales personnes concernées par le suivi de la qualité des données. Par défaut, cette instance regroupe a minima le responsable QDD et les représentants des fonctions opérationnelles (lignes métier impliquées dans les processus prudentiels dans lesquelles sont nommés les « relais »), de la fonction informatique, de la fonction actuarielle et de la fonction gestion des risques. Un compte-rendu incluant un relevé de décisions est systématiquement formalisé.

La fréquence de réunion de ce comité est cohérente avec la fréquence de validation des calculs prudentiels (provisions techniques, capital de solvabilité) afin de tenir compte dans cette validation de l’évaluation de la qualité et des potentielles limites des données utilisées aux fins des calculs.

Les conclusions adoptées et décisions prises au sein de ce comité sont portées à la connaissance des dirigeants effectifs.

L’entreprise peut également mettre en place un comité plus opérationnel afin de mettre en œuvre le dispositif de maitrise de qualité des données et préparer les séances du comité de gouvernance et de pilotage.

# Les instruments de suivi

Sur la base de l’article 258 §1 alinéas a, h, j et k et de l’article 266 du règlement délégué, l’entreprise met en place des outils permettant d’apprécier à fréquence régulière la qualité.
---
des données. À cette fin, elle conçoit des tableaux de bord synthétisant l’ensemble des résultats des contrôles de qualité des données jalonnant le processus de cheminement et de transformation de la donnée du niveau le plus fin au niveau le plus agrégé.

# 27

La conception de ces contrôles (cf. infra) requiert de réaliser les étapes préalables suivantes :

- définir la tolérance globale au risque de non qualité des données : ce niveau de tolérance correspond, en cas de moindre qualité des données, au niveau maximum d’incertitude accepté par l’entreprise sur les résultats prudentiels (provisions techniques prudentielles, capital de solvabilité requis, …) ;
- décliner cette tolérance globale, a minima pour les données critiques, en seuil d’acceptation par contrôle correspondant à l’atteinte des objectifs de qualité des utilisateurs. En lien avec le seuil d’acceptation d’un contrôle, l’entreprise peut définir une grille de seuils en fonction desquels des actions (investigations, corrections) sont enclenchées.

# 28

Afin d’exploiter et de synthétiser les résultats des contrôles dans un tableau de bord, l’entreprise définit et formalise une méthodologie d’agrégation qui doit être validée et partagée.

# 29

Le tableau de bord est présenté et commenté en comité de gouvernance et de pilotage de la qualité des données quand celui-ci est mis en place.

# 30

Les dirigeants effectifs de l’entreprise sont destinataires du tableau de bord dans le cadre du système de transmission d’information. Le tableau de bord peut également faire l’objet d’une transmission aux organes de contrôle de l’entreprise (conseil d’administration ou de surveillance, comité d’audit et des risques,…). De ce fait, la granularité des éléments présents dans le tableau de bord doit être adaptée à la prise de décision par les différentes instances de gouvernance de l’entreprise.

# 31

Par ailleurs, en cas d’utilisation d’un modèle interne, les tableaux de bord évaluant la qualité des données sont pris en compte dans la validation des résultats issus de celui-ci (cf. notice MI §16.6).

# 32

La périodicité des tableaux de bord est adaptée à la périodicité des calculs réglementaires ou, le cas échéant, des comités de gouvernance et de pilotage.

# 2.6. Les critères de qualité des données

# 33

Les critères d’exactitude, d’exhaustivité et de pertinence permettent d’apprécier la qualité des données SII.

# 34

S’agissant spécifiquement du critère d’exhaustivité, l’entreprise prend en compte tous les groupes de risques homogènes dans les calculs. Elle apprécie et justifie au cas par cas la profondeur d’historique des données selon, notamment, les activités d’assurance concernées. À cette fin, elle réalise une étude de sensibilité en fonction de la profondeur de l’historique.

# 35

L’entreprise veille à ce que les informations utilisées dans les calculs de provisions techniques prudentielles et dans les calculs réalisés par un modèle interne soient crédibles. L’entreprise est en mesure d’en apporter la preuve, notamment par les éléments suivants :

- leur cohérence ;
---
- leur objectivité (capacité à refléter fidèlement et sans parti pris la réalité) ;

- la fiabilité de la source ;

- la transparence (en lien avec la piste d’audit) avec laquelle elles ont été générées et éventuellement (re)traitées.

36 Par ailleurs, en matière de provisions techniques, l’article 20 du règlement délégué précise les mesures à mettre en œuvre lorsque les données utilisées ne satisfont pas l’une des dispositions de l’article 19 du règlement délégué. L’entreprise documente et explicite dans ce cas :

- les raisons pour lesquelles les données ne satisfont pas aux critères de qualité (limites) ;
- la méthode de remédiation ou de contournement (ajustements par exemple) mise en œuvre ;
- les fonctions responsables de ce processus.

Le responsable QDD est impliqué dans ce processus.

37 Afin de garantir la piste d’audit, les données en défaut sont enregistrées et stockées avant de faire l’objet d’ajustements. Lorsque des ajustements sont pratiqués (notamment en exploitant d’autres données dont la qualité est éprouvée - par exemple : recours au numéro de sécurité sociale pour identifier le genre), ils sont explicités dans une documentation ad hoc.

38 Aux termes de l’article 21 du règlement délégué, l’entreprise n’utilise pas d’approximations pour calculer les provisions techniques prudentielles lorsque l’une des assertions suivantes est réalisée :

- il est possible d’ajuster les données (cf. supra),
- les insuffisances constatées sur les données sont dues à l’inadéquation des processus et procédures internes de collecte, de stockage ou de validation de ces données,
- il est possible d’utiliser des données externes pour remédier à ces insuffisances. Dans ce cas, l’entreprise d’assurance ou de réassurance doit veiller à respecter les principes énoncés à l’article 27 du règlement délégué.

39 Lorsque les données utilisées ne sont pas exactes, exhaustives ou appropriées, l’entreprise d’assurance ou de réassurance démontre que ces insuffisances ou ajustements ne conduisent pas à une sous-estimation de ses engagements ou de sa solvabilité.

# 3. Enjeux en matière de qualité des données externes

40 L’entreprise peut utiliser des données provenant d'une source externe (délégataires de gestion de contrats et de sinistre, gestionnaires d’actifs, réassureurs, prestataires informatiques, fournisseurs de données …) à condition de satisfaire aux exigences de qualité énoncées précédemment. L’entreprise reste responsable de la qualité des données utilisées et s’assure que les données provenant de sources externes répondent aux mêmes critères de qualité que les données internes. Les dispositifs s’appliquant à ces dernières s’appliquent mutatis mutandis aux données externes.

# 3.1. Identification des prestataires et partenaires en matière de qualité des données

41 L’entreprise identifie les données provenant d’une source externe et évalue leur importance relative dans son activité (proportion de contrats et/ou de sinistres gérés par rapport à son portefeuille total, quote-part de réassurance, modélisation de garanties…). Cette analyse
---
# 3.2. Contractualisation et gestion des risques liés aux données externes

42 Certaines informations telles que les données de marchés financiers, les données relatives aux catastrophes naturelles, aux générateurs de scenarios économiques ou encore les tables de mortalité … proviennent de fournisseurs spécialisés dont c’est l’activité principale. Il appartient à l’entreprise qui y a recours d’étudier, lors de la sélection de ces fournisseurs, les garanties de qualité dont ceux-ci se prévalent. Pour autant, l’entreprise reste responsable de l’importation des données en question dans ses systèmes d’information et doit être en capacité de justifier que cette opération n’a pas altéré leur intégrité. Elle est également responsable de leur contrôle avant usage et garante de la traçabilité des traitements qui leur sont appliqués ainsi que de l’utilisation adéquate qui en est faite dans les chaines de calculs prudentiels.

43 En dehors du cas particulier traité au paragraphe précédent, lors de la contractualisation de la relation avec le prestataire au titre des activités sous-traitées qui positionnent ce dernier par effet secondaire en fournisseur de données à l’entreprise, l’accord écrit explicite les exigences relatives à la qualité des données transmises, notamment :

- la méthode, les métriques et la fréquence d’évaluation de la prestation sur la base du niveau de service négocié entre les parties (performances et résultats) tenant compte des critères de qualité des données y compris leur disponibilité (article 274 §4 (a) du règlement délégué);
- la sûreté et la confidentialité des données (articles 274 §3 (f) et 274 §4 (g) du règlement délégué).

44 L’accord est complété d’une annexe encadrant les modalités de transmission des données précisant :

- les données attendues (granularité, définition des données, format…),
- les modalités d’envoi dont les aspects de sécurité,
- les contrôles opérés par le fournisseur pour attester du niveau de qualité,
- la disponibilité.

# 4. Répertoire des données

45 Le répertoire des données indique leur source, leurs caractéristiques et l'usage qui en est fait. Le responsable QDD est garant de son élaboration et de sa conformité. Son alimentation découle d’un travail transversal animé par le responsable QDD (impliquant notamment les directions de l’actuariat, de la gestion des contrats et des sinistres, des risques et informatique).

46 Le processus d’alimentation du répertoire est formalisé. L’entreprise définit notamment les modalités de mise à jour afin de prendre en compte les évolutions des systèmes d’information et/ou des processus de réalisation des calculs prudentiels (notamment modification du modèle interne partiel ou total). Le responsable QDD est garant du processus de maintenance du répertoire.

47 Le répertoire de données permet de centraliser les données intervenant directement ou indirectement dans les calculs de provisions techniques, de paramètres propres et
---
également aux fins de l'ensemble des calculs réalisés en modèle interne sans en limiter le périmètre aux données qui seraient référencées comme critiques :

- il couvre notamment les données des systèmes sources internes (depuis la comptabilité ou l’environnement de gestion (contrats, sinistres, actifs) par exemple), ainsi qu’en provenance des fournisseurs externes (délégataires de gestion, réassureurs, partenaires commerciaux, courtiers, fournisseurs de données spécifiques³…),
- il couvre également les données intermédiaires produites dans la chaine de calcul et les données inscrites dans les états prudentiels.

Par ailleurs, couvrir les autres éléments demandés dans les états prudentiels attendus de la réglementation Solvabilité 2 relève d’une bonne pratique.

48 Le répertoire comprend au moins les attributs suivants caractérisant les données :

- leur description,
- leur localisation,
- leur source,
- l’usage qui en est fait (processus métier dans lesquels les données sont impliquées : provisionnement, capital de solvabilité et autre élément du bilan prudentiel),
- leur « criticité » (cf. infra),
- leur propriétaire (rôles et responsabilités à définir vis-à-vis de la donnée),
- leurs modalités (par exemple : numérique, alphanumérique, plage de valeur),
- la fréquence de mise à jour.

49 Aux termes de l’article 19 §3 alinéa e point iii), l’information sur la fréquence de mise à jour de la donnée est une caractéristique à incorporer dans le répertoire.

50 La notion de criticité permet à l’entreprise de porter une attention renforcée sur les données ayant le plus d’impact sur les calculs prudentiels et, si nécessaire, de mettre en place des contrôles supplémentaires pour s’assurer de la qualité de ces données jugées critiques. Elle traduit le niveau de sensibilité des résultats des calculs prudentiels à une variation de la donnée. Une donnée est définie comme critique lorsque l’impact sur les résultats est jugé significatif par l’entreprise (niveau de significativité qui doit être cohérent avec la tolérance globale au risque de non qualité des données – cf. supra).

51 Lorsque la criticité est déterminée par des tests de sensibilité, l’entreprise est en capacité de fournir la méthodologie appliquée et validée (notamment l’explicitation du seuil au-delà duquel l’évolution du résultat final est jugée significative) et les résultats des calculs. Si la criticité est déterminée « à dires d’expert », l’organisme formalise cet avis. La criticité est réévaluée au gré des changements liés à l’activité d’assurance, aux méthodologies de calculs prudentiels…

52 Le répertoire permet de faire le lien avec la cartographie des flux de données et les contrôles de qualité des données.

53 L’outil choisi pour héberger le répertoire des données en garantit la maintenance et l’accessibilité.

3 Modélisation du risque catastrophe, taux de change, données des scenarios économiques…
---
# 5. Traçabilité

L’entreprise constitue une documentation comprenant notamment les spécifications relatives à la collecte, au traitement et à l'application des données.

# 5.1. Cartographies

Afin de visualiser l’environnement informatique, de maîtriser la chaîne de transformation des données et d’identifier les zones de risques de leur cheminement, l’entreprise établit une documentation. Celle-ci peut prendre la forme de deux cartographies qui se complètent :

- la cartographie des systèmes d’information, documentée et à jour. Elle fournit une vision globale des éléments, applications et outils, qui constituent son système d’information ;
- la cartographie des flux de données qui représente les cheminements des données ou agrégats de données qui parcourent son système d’information.

La cartographie des flux permet de visualiser le cheminement des données au sein de l’entreprise, depuis les systèmes sources jusqu’aux états prudentiels. Cette cartographie précise les applicatifs impliqués en positionnant les principales étapes de transformation et les références des contrôles manuels et automatiques réalisés (cf. infra). Selon l’étendue des activités et la complexité des systèmes d’information, plusieurs cartographies peuvent être formalisées.

La cartographie des flux couvre tout autant les données internes que les données externes et quelles que soient les modalités d’intégration (manuelles ou automatiques) dans le système d’information de l’entreprise qui leur sont appliquées.

La cartographie des flux de données permet de faire le lien avec le répertoire des données et les contrôles de qualité des données.

L’outil choisi pour héberger la cartographie des flux de données en garantit la maintenance et l’accessibilité. L’entreprise veille à la mise à jour régulière de la cartographie des flux de données selon les évolutions de ses activités et de son système d’information.

En complément, la mise en place du lignage par donnée (cartographie « micro ») est notamment une bonne pratique qui répond aux exigences de traçabilité des données critiques. Le lignage d’une donnée schématise les différentes étapes et transformations effectuées entre les systèmes sources à l’origine de la donnée et son utilisation finale. Le lignage peut être documenté dans le répertoire ou dans un outil ad hoc. Il répond aux mêmes critères que la cartographie des flux (exhaustivité, lien avec les autres documents, sûreté informatique, mise à jour).

# 5.2. Collecte & traitements

Les processus de collecte, de transport et de traitement des données sont documentés. Ces documents et procédures recensent, pour un périmètre donné, tous les fichiers et entrepôts successifs impliqués dans le transport et/ou les traitements manuels et automatiques des données y compris les corrections. Cette documentation permet de comprendre la nature des transformations et d’en appréhender la fréquence. Les transformations des données permettent par exemple de corriger, d’homogénéiser, de regrouper les données utilisées à la même fin, y compris celles provenant de différentes sources.
---
# 6. Contrôle interne

L’entreprise :

- référence l’ensemble des bases de données, entrepôts et fichiers utilisés (par exemple bordereaux de primes, bordereaux trimestriels de réassurance,…) et leurs propriétaires ;
- explicite l’ensemble des transformations opérées sur les données de ces fichiers (usage de taux de change, programmes, tables de correspondance (entre branche, catégorie ministérielle, segmentation propre à l’organisme et ligne d’activité Solvabilité 2…)), indique l’objectif de ces transformations et précise les responsables de ces transformations.

L’entreprise veille à la mise à jour régulière de ces documents et procédures selon les évolutions de ses activités et de son système d’information.

# 6.1. Gestion et cartographie des risques

Le système de contrôle interne de l’entreprise vise à garantir la disponibilité et la fiabilité de l’information financière et non financière (article 266 du règlement délégué). Le risque de non qualité des données est un risque transverse, à la croisée des processus de souscription, de provisionnement, de production des comptes sociaux et prudentiels alimentés par des systèmes internes et externes, comportant des risques opérationnels.

Plus spécifiquement, l’article 260 du règlement délégué dispose que les politiques de souscription et de provisionnement incluent le sujet de la suffisance et de la qualité des données à prendre en considération dans ces deux domaines. Ainsi, le risque de non qualité des données est associé aux processus de souscription et de provisionnement et la cartographie des risques établie par l’entreprise le reflète. Lorsque le processus d’établissement du capital de solvabilité requis (resp. des paramètres propres) est référencé comme un processus à part entière, le risque de non qualité des données inhérent à ce processus est également inclus dans la cartographie des risques.

# 6.2. Dispositif de contrôle permanent

Le référentiel de contrôles (contrôles opérationnels dits contrôles de 1ᵉʳ niveau) recense à la fois :

- les contrôles effectués dans le cadre des processus établissant les provisions techniques prudentielles, paramètres spécifiques et capital de solvabilité qui participent directement ou indirectement à mesurer le risque de non qualité des données utilisées ;
- les contrôles spécifiquement conçus pour réduire les risques identifiés en matière de qualité des données tout au long du cheminement des données.

Ces contrôles sont documentés et décrits (risque sous-jacent, périodicité, critères de qualité vérifiés, donnée(s) vérifiée(s), seuil(s) retenu(s), réalisation manuelle/automatique, mode opératoire, responsable). Leur résultat est formalisé et enregistré d’une campagne de contrôles à l’autre, s’inscrivant ainsi dans une démarche d’amélioration continue.
---
L’entreprise garantit la cohérence entre le référentiel des contrôles, la cartographie des flux et le répertoire des données. L’entreprise veille à la mise à jour régulière du référentiel des contrôles.

L’entreprise met en place un processus de revue régulière (dite de 2ème niveau) afin de vérifier que les contrôles opérationnels sont adéquats et efficaces.

# 6.3. Fonction actuarielle

La fonction actuarielle apprécie la suffisance et la qualité des données utilisées dans le calcul des provisions techniques prudentielles. Pour ce faire, elle utilise notamment les tableaux de bord évaluant la qualité des données. Elle veille à ce que les limites identifiées dans certaines données soient prises en compte dans l’estimation des provisions techniques prudentielles. Le cas échéant, le niveau des provisions techniques est ajusté pour en tenir compte. Cet ajustement est justifié et documenté.

# 6.4. Audit interne

La fonction d’audit interne visée à l’article L354-1 du code des assurances inclut le risque de non qualité des données dans son univers d’audit et conçoit en conséquence son plan d’audit pluriannuel afin d’évaluer l’adéquation et l’efficacité du dispositif mis en place au sein de l’entreprise en matière de maitrise de la qualité des données entrant dans les calculs prudentiels.

# 7. Précisions dans le cas de groupes prudentiels

Les entités têtes de groupe visées aux L.356-2 al. 2 à 5 du code des assurances, L.212-1 al. 2 du code de la mutualité et L.913-9 al.2 du code de la sécurité sociale respectent les exigences quantitatives, les exigences relatives au système de gouvernance, au système de gestion des risques et au système de contrôle interne des groupes dont la maitrise de la qualité des données SII. À ce titre, les éléments de gouvernance (respectivement de gestion des risques et de contrôle interne) relatifs à la qualité des données SII de la tête de groupe et des entités « solos » du groupe sont cohérents entre eux, notamment :

- le document cadre organisant le dispositif de maitrise de la qualité des données SII adopté par la tête de groupe est adopté, et le cas échéant adapté, par chaque entreprise soumise à la réglementation Solvabilité 2 composant le groupe,
- les rôles et responsabilités des parties prenantes à la gestion de la qualité des données (dont les fonctions clefs) sont endossés au niveau de chaque entreprise soumise à la réglementation Solvabilité 2 composant le groupe,
- la cartographie des risques du groupe comporte tous les risques émanant des entreprises du groupe dont celui de non qualité des données SII. La tolérance au risque de non qualité des données de la tête de groupe est cohérente avec celles des entreprises soumises à la réglementation Solvabilité 2,
- les définitions des critères, les indicateurs et standards relatifs à la qualité des données sont partagés et adoptés par les entreprises du groupe soumises à la réglementation Solvabilité 2,
- en conséquence, les contrôles mis en place pour mesurer la qualité des données sont cohérents d’une entreprise du groupe à l’autre. Les instruments de suivi sont communs de façon à garantir la compatibilité et en permettre la synthèse au niveau de la tête de groupe, aidant notamment la fonction clé actuariat du groupe à se prononcer sur la suffisance et la qualité des données utilisées dans le calcul des provisions techniques prudentielles agrégées au niveau du groupe.
---
Plus largement, le système de contrôle interne du groupe garantit la bonne information relative à la gestion de la qualité des données SII à tous les niveaux du groupe.

14