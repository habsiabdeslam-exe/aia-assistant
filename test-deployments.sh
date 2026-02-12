#!/bin/bash

# Script de test des déploiements
# Teste les URLs et affiche les résultats

echo "🧪 Test des déploiements Azure..."
echo ""

# Obtenir les URLs
echo "📡 Récupération des URLs..."
STATIC_URL=$(az staticwebapp show --name ahaweb01 --query 'defaultHostname' -o tsv 2>/dev/null)
CONTAINER_URL=$(az containerapp show --name ahacoapp01 --resource-group DevSecOps-gov-01 --query 'properties.configuration.ingress.fqdn' -o tsv 2>/dev/null)

if [ -z "$STATIC_URL" ]; then
    echo "❌ Impossible de récupérer l'URL du Static Web App"
    echo "   Vérifiez que vous êtes connecté à Azure: az login"
    exit 1
fi

if [ -z "$CONTAINER_URL" ]; then
    echo "❌ Impossible de récupérer l'URL du Container App"
    echo "   Vérifiez que vous êtes connecté à Azure: az login"
    exit 1
fi

echo "✅ URLs récupérées:"
echo "   Frontend: https://$STATIC_URL"
echo "   Backend:  https://$CONTAINER_URL"
echo ""

# Tester le backend
echo "🔍 Test du backend (Container App)..."
echo "   URL: https://$CONTAINER_URL/health"
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$CONTAINER_URL/health" 2>/dev/null)

if [ "$BACKEND_STATUS" = "200" ]; then
    echo "   ✅ Backend répond correctement (HTTP $BACKEND_STATUS)"
    curl -s "https://$CONTAINER_URL/health" | jq '.' 2>/dev/null || echo "   Response: OK"
else
    echo "   ❌ Backend ne répond pas correctement (HTTP $BACKEND_STATUS)"
    echo "   Vérifiez que l'image backend est déployée (pas nginx)"
fi
echo ""

# Tester le frontend
echo "🔍 Test du frontend (Static Web App)..."
echo "   URL: https://$STATIC_URL"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$STATIC_URL" 2>/dev/null)

if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "   ✅ Frontend répond (HTTP $FRONTEND_STATUS)"
    
    # Vérifier si le contenu est vide
    CONTENT_LENGTH=$(curl -s "https://$STATIC_URL" | wc -c)
    if [ "$CONTENT_LENGTH" -lt 100 ]; then
        echo "   ⚠️  ATTENTION: Le contenu semble vide ou très petit ($CONTENT_LENGTH bytes)"
        echo "   Cela peut indiquer un problème de build ou de déploiement"
    else
        echo "   ✅ Contenu présent ($CONTENT_LENGTH bytes)"
    fi
else
    echo "   ❌ Frontend ne répond pas correctement (HTTP $FRONTEND_STATUS)"
fi
echo ""

# Recommandations
echo "📋 Recommandations:"
if [ "$BACKEND_STATUS" != "200" ]; then
    echo "   1. Déployer le backend: ./deploy-backend.sh"
fi

if [ "$FRONTEND_STATUS" != "200" ] || [ "$CONTENT_LENGTH" -lt 100 ]; then
    echo "   2. Redéployer le frontend:"
    echo "      - Faire un commit dans frontend/"
    echo "      - Pousser vers GitHub"
    echo "      - Vérifier le workflow GitHub Actions"
fi

echo ""
echo "🌐 Pour tester manuellement:"
echo "   Frontend: https://$STATIC_URL"
echo "   Backend Health: https://$CONTAINER_URL/health"
echo "   Backend Docs: https://$CONTAINER_URL/docs"
