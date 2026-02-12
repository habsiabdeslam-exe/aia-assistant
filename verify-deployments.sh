#!/bin/bash

# Script de vérification des déploiements Azure
# Vérifie le statut de Static Web App et Container App

echo "🔍 Vérification des déploiements Azure..."
echo ""

# Vérifier Static Web App
echo "📱 Static Web App (ahaweb01):"
az staticwebapp show --name ahaweb01 \
  --query "{Name:name,Status:status,URL:defaultHostname,LastModified:lastModifiedTime}" \
  -o table
echo ""

# Vérifier Container App
echo "🐳 Container App (ahacoapp01):"
az containerapp show \
  --name ahacoapp01 \
  --resource-group DevSecOps-gov-01 \
  --query "{Name:name,FQDN:properties.configuration.ingress.fqdn,Image:properties.template.containers[0].image,Status:properties.runningStatus,Replicas:properties.template.scale.minReplicas}" \
  -o table
echo ""

# Obtenir les URLs
echo "🌐 URLs des applications:"
STATIC_URL=$(az staticwebapp show --name ahaweb01 --query 'defaultHostname' -o tsv)
CONTAINER_URL=$(az containerapp show --name ahacoapp01 --resource-group DevSecOps-gov-01 --query 'properties.configuration.ingress.fqdn' -o tsv)

echo "Frontend: https://$STATIC_URL"
echo "Backend:  https://$CONTAINER_URL"
echo ""

# Vérifier les logs récents du Container App
echo "📋 Logs récents du Container App (dernières 20 lignes):"
az containerapp logs show \
  --name ahacoapp01 \
  --resource-group DevSecOps-gov-01 \
  --tail 20 \
  --follow false
