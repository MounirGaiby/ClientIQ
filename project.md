Cahier des Charges 2 : CRM Multi-Entreprise
2.1 Contexte et Objectifs
Contexte Métier Développer un système de gestion de la relation client permettant à
plusieurs entreprises de gérer indépendamment leurs prospects, clients et opportunités
commerciales. Chaque entreprise doit pouvoir personnaliser ses processus de vente et
automatiser ses campagnes marketing.
Objectifs du Projet
• Centraliser la gestion des contacts et opportunités commerciales
• Automatiser les processus marketing et de suivi commercial
• Fournir des outils d'analyse pour optimiser les performances de vente
• Faciliter la collaboration des équipes commerciales
• Offrir une vue d'ensemble du pipeline commercial
2.2 Périmètre Fonctionnel
Fonctionnalités Obligatoires (MVP - 4 semaines)
Module Multi-Tenant
• Configuration d'entreprises avec équipes commerciales
• Personnalisation des pipelines de vente par entreprise
• Gestion des utilisateurs et rôles (Admin, Manager, Commercial, Observateur)
• Isolation complète des données clients entre entreprises
Module Gestion des Contacts
• Création et gestion des contacts (prospects, clients, partenaires)
• Informations complètes : coordonnées, entreprise, poste, notes
• Segmentation manuelle et automatique des contacts
• Import et export de listes de contacts (CSV)
• Historique complet des interactions avec chaque contact
• Système de scoring automatique des prospects
Module Pipeline Commercial
• Création d'opportunités liées aux contacts
• Étapes de vente personnalisables par entreprise
• Valeur estimée et probabilité de conversion
• Date de clôture prévisionnelle
• Assignation des opportunités aux commerciaux
• Suivi de l'avancement dans le pipeline
Module Activités et Suivi
• Planification de tâches et rendez-vous
• Historique chronologique des interactions
• Rappels automatiques pour le suivi des prospects
• Notes et commentaires sur les contacts et opportunités
• Gestion des appels téléphoniques et emails
• To-do list personnalisée par commercial
Module Communication
• Templates d'emails personnalisables
• Envoi d'emails individuels et en masse
• Suivi des ouvertures et clics (basique)
• Journal des communications par contact
• Gestion des campagnes email simples
Module Reporting
• Tableau de bord avec métriques clés
• Rapport des ventes par période et commercial
• Analyse de l'entonnoir de conversion
• Prévisions de vente basées sur le pipeline
• Export des rapports en PDF/Excel
Fonctionnalités Optionnelles (Bonus)
Fonctionnalités Avancées
• Automation marketing avec déclencheurs
• Intégration téléphonie (logs d'appels)
• Synchronisation avec calendriers externes
• Mobile app ou interface mobile avancée
• Intelligence artificielle pour scoring des leads
• Intégration avec réseaux sociaux
2.3 Utilisateurs et Cas d'Usage
Administrateur Entreprise
• Configure les pipelines et processus de vente
• Gère les équipes et assigne les territoires
• Analyse les performances globales de l'entreprise
• Paramètre les campagnes marketing automatisées
Manager Commercial
• Supervise l'activité de son équipe
• Assigne les prospects aux commerciaux
• Analyse les performances individuelles et collectives
• Valide les prévisions de vente
Commercial/Vendeur
• Gère son portefeuille de prospects et clients
• Saisit et suit ses opportunités de vente
• Planifie ses activités et rendez-vous
• Communique avec ses contacts via l'outil
Marketing
• Crée et lance des campagnes email
• Analyse les résultats des campagnes
• Qualifie les leads entrants
• Alimente le CRM avec de nouveaux prospects
2.4 Règles de Gestion
Gestion des Contacts
• Un contact ne peut appartenir qu'à une seule entreprise (tenant)
• Les doublons sont détectés automatiquement à la création
• L'historique des interactions est conservé indéfiniment
• Le scoring évolue selon l'activité et l'engagement du contact
Pipeline Commercial
• Une opportunité passe obligatoirement par toutes les étapes définies
• La probabilité de conversion augmente avec l'avancement dans le pipeline
• Les prévisions se basent sur la valeur × probabilité
• Une opportunité fermée (gagnée/perdue) ne peut plus être modifiée
Activités et Communications
• Toute interaction doit être tracée dans l'historique du contact
• Les rappels sont générés automatiquement selon des règles définies
• Les emails envoyés via le CRM sont automatiquement archivés
• Les tâches en retard apparaissent en priorité dans les tableaux de bord
Sécurité et Permissions
• Les commerciaux ne voient que leurs prospects assignés
• Les managers voient tous les prospects de leur équipe
• L'historique des modifications est conservé pour audit
• Les données sensibles sont chiffrées en base
2.5 Contraintes et Exigences
Contraintes Fonctionnelles
• Support de 10 entreprises avec 500 contacts chacune minimum
• Interface disponible en français
• Conformité RGPD pour la gestion des données personnelles
• Possibilité d'export des données à tout moment
Contraintes de Performance
• Temps de réponse inférieur à 2 secondes pour les recherches
• Interface fluide même avec de gros volumes de données
• Sauvegarde automatique des saisies en cours
• Synchronisation temps réel des mises à jour
Contraintes d'Intégration
• API REST pour intégration avec outils externes
• Import/export standard (CSV, Excel)
• Webhooks pour notifications externes
• Interface mobile responsive
2.6 Livrables Attendus
Application Fonctionnelle
• CRM complet avec toutes les fonctionnalités MVP
• Interface d'administration pour la configuration
• Tableaux de bord et rapports fonctionnels
• Système de notifications opérationnel
Documentation
• Guide utilisateur par rôle (admin, manager, commercial)
• Documentation d'API pour les développeurs
• Procédures d'import/export des données
• Guide de configuration des pipelines de vente
Démonstration
• Jeu de données réaliste avec plusieurs entreprises
• Scénarios de démonstration complets
• Présentation des fonctionnalités clés
• Mesures de performance et statistiques
2.7 Critères d'Acceptance
Fonctionnels
• Gestion complète du cycle prospect → client → opportunité → vente
• Communication email intégrée avec suivi
• Reporting des performances avec graphiques
• Pipeline de vente avec prévisions fiables
Techniques
• Isolation multi-tenant respectée sans faille de données
• Performance acceptable avec volumes de données réalistes
• Interface responsive utilisable sur mobile
• Sécurité des données et conformité RGPD