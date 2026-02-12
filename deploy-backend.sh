#!/bin/bash

# Script de déploiement manuel du backend vers Azure Container Registry et Container App
# Resource Group: DevSecOps-gov-01
# Container Registry: ahacontreg01
# Container App: ahacoapp01

set -e

echo "🚀 Déploiement du backend vers Azure..."

# Variables
RESOURCE_GROUP="DevSecOps-gov-01"
ACR_NAME="ahacontreg01"
ACR_LOGIN_SERVER="ahacontreg01.azurecr.io"
IMAGE_NAME="aia-backend"
CONTAINER_APP="ahacoapp01"
TAG="manual-$(date +%Y%m%d-%H%M%S)"

echo "📦 Tag de l'image: $TAG"

# Étape 1: Login à Azure Container Registry
echo "🔐 Connexion à Azure Container Registry..."
az acr login --name $ACR_NAME

# Étape 2: Construire l'image Docker
echo "🏗️  Construction de l'image Docker..."
cd backend
docker build -t $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG -t $ACR_LOGIN_SERVER/$IMAGE_NAME:latest .
cd ..

# Étape 3: Pousser l'image vers ACR
echo "📤 Push de l'image vers ACR..."
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

# Étape 4: Mettre à jour Container App
echo "🔄 Mise à jour de Container App..."
az containerapp update \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG

# Étape 5: Vérifier le déploiement
echo "✅ Vérification du déploiement..."
az containerapp show \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --query "{name:name,fqdn:properties.configuration.ingress.fqdn,image:properties.template.containers[0].image,replicas:properties.runningStatus}" \
  -o table

echo ""
echo "✅ Déploiement terminé!"
echo "🌐 URL de l'application: https://$(az containerapp show --name $CONTAINER_APP --resource-group $RESOURCE_GROUP --query 'properties.configuration.ingress.fqdn' -o tsv)"
