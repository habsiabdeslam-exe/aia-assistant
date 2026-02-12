#!/bin/bash

# Script pour déployer l'image backend depuis ACR vers Container App
# Ce script construit l'image, la pousse vers ACR, et met à jour le Container App

set -e

echo "🚀 Déploiement du backend FastAPI..."
echo ""

# Variables
RESOURCE_GROUP="DevSecOps-gov-01"
ACR_NAME="ahacontreg01"
ACR_LOGIN_SERVER="ahacontreg01.azurecr.io"
IMAGE_NAME="aia-backend"
CONTAINER_APP="ahacoapp01"
TAG="v$(date +%Y%m%d-%H%M%S)"

echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   ACR: $ACR_LOGIN_SERVER"
echo "   Container App: $CONTAINER_APP"
echo "   Image Tag: $TAG"
echo ""

# Étape 1: Vérifier qu'on est dans le bon répertoire
if [ ! -f "backend/Dockerfile" ]; then
    echo "❌ Erreur: backend/Dockerfile introuvable"
    echo "   Assurez-vous d'exécuter ce script depuis la racine du projet"
    exit 1
fi

# Étape 2: Login à Azure Container Registry
echo "🔐 Connexion à Azure Container Registry..."
az acr login --name $ACR_NAME
if [ $? -ne 0 ]; then
    echo "❌ Échec de connexion à ACR"
    echo "   Vérifiez que vous êtes connecté à Azure: az login"
    exit 1
fi
echo "✅ Connecté à ACR"
echo ""

# Étape 3: Construire l'image Docker
echo "🏗️  Construction de l'image Docker..."
echo "   Dockerfile: backend/Dockerfile"
echo "   Context: backend/"
docker build \
    -f backend/Dockerfile \
    -t $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG \
    -t $ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
    backend/

if [ $? -ne 0 ]; then
    echo "❌ Échec de construction de l'image"
    exit 1
fi
echo "✅ Image construite avec succès"
echo ""

# Étape 4: Pousser l'image vers ACR
echo "📤 Push de l'image vers ACR..."
echo "   Image: $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG"
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest

if [ $? -ne 0 ]; then
    echo "❌ Échec du push vers ACR"
    exit 1
fi
echo "✅ Image poussée vers ACR"
echo ""

# Étape 5: Mettre à jour Container App avec la nouvelle image
echo "🔄 Mise à jour de Container App..."
echo "   Container App: $CONTAINER_APP"
echo "   Nouvelle image: $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG"

az containerapp update \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG

if [ $? -ne 0 ]; then
    echo "❌ Échec de mise à jour du Container App"
    exit 1
fi
echo "✅ Container App mis à jour"
echo ""

# Étape 6: Vérifier le déploiement
echo "🔍 Vérification du déploiement..."
CONTAINER_INFO=$(az containerapp show \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --query "{FQDN:properties.configuration.ingress.fqdn,Image:properties.template.containers[0].image,Replicas:properties.runningStatus}" \
    -o json)

echo "$CONTAINER_INFO" | jq '.'

FQDN=$(echo "$CONTAINER_INFO" | jq -r '.FQDN')
echo ""
echo "✅ Déploiement terminé!"
echo ""
echo "🌐 URLs de test:"
echo "   Backend URL: https://$FQDN"
echo "   Health Check: https://$FQDN/health"
echo "   API Docs: https://$FQDN/docs"
echo ""
echo "🧪 Test du health endpoint..."
sleep 5
curl -s "https://$FQDN/health" | jq '.' || echo "En attente que le container démarre..."
echo ""
echo "💡 Si vous voyez encore nginx, attendez 30 secondes et réessayez:"
echo "   curl https://$FQDN/health"
