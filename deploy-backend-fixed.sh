#!/bin/bash

# Script de déploiement backend avec la bonne plateforme (linux/amd64)
# Corrige l'erreur "no child with platform linux/amd64"

set -e

echo "🚀 Déploiement du backend (linux/amd64)..."
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
echo "   Platform: linux/amd64"
echo ""

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "backend/Dockerfile" ]; then
    echo "❌ Erreur: backend/Dockerfile introuvable"
    exit 1
fi

# Login à ACR
echo "🔐 Connexion à Azure Container Registry..."
az acr login --name $ACR_NAME
if [ $? -ne 0 ]; then
    echo "❌ Échec de connexion à ACR"
    exit 1
fi
echo "✅ Connecté à ACR"
echo ""

# Construire l'image avec la bonne plateforme
echo "🏗️  Construction de l'image Docker pour linux/amd64..."
echo "   ⚠️  IMPORTANT: Spécification de --platform linux/amd64"
echo "   (Cela peut prendre 3-5 minutes sur Mac ARM)"
echo ""

docker buildx build \
    --platform linux/amd64 \
    -f backend/Dockerfile \
    -t $ACR_LOGIN_SERVER/$IMAGE_NAME:$TAG \
    -t $ACR_LOGIN_SERVER/$IMAGE_NAME:latest \
    --push \
    backend/

if [ $? -ne 0 ]; then
    echo "❌ Échec de construction de l'image"
    echo ""
    echo "💡 Si buildx n'est pas disponible, essayez:"
    echo "   docker buildx create --use"
    echo "   Puis réexécutez ce script"
    exit 1
fi

echo "✅ Image construite et poussée vers ACR"
echo ""

# Mettre à jour Container App
echo "🔄 Mise à jour de Container App..."
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

# Vérifier le déploiement
echo "🔍 Vérification du déploiement..."
FQDN=$(az containerapp show \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo "✅ Déploiement terminé!"
echo ""
echo "🌐 URLs de test:"
echo "   Backend URL: https://$FQDN"
echo "   Health Check: https://$FQDN/health"
echo "   API Docs: https://$FQDN/docs"
echo ""
echo "🧪 Test du health endpoint dans 30 secondes..."
sleep 30
echo ""
curl -s "https://$FQDN/health" | jq '.' || curl -s "https://$FQDN/health"
echo ""
echo "💡 Si vous voyez {\"status\":\"healthy\"}, le backend fonctionne!"
echo "💡 Si vous voyez encore nginx, attendez 1 minute et testez:"
echo "   curl https://$FQDN/health"
