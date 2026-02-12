#!/bin/bash

# Script pour diagnostiquer et redéployer le frontend
# Vérifie le build local et force un nouveau déploiement

set -e

echo "🔍 Diagnostic et correction du frontend..."
echo ""

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Erreur: frontend/package.json introuvable"
    exit 1
fi

# Étape 1: Tester le build localement
echo "🏗️  Test du build local..."
cd frontend

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Build local pour vérifier les erreurs
echo "🔨 Build de l'application..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Échec du build local"
    echo "   Corrigez les erreurs de build avant de déployer"
    exit 1
fi

echo "✅ Build local réussi"
echo "📁 Contenu du dossier dist:"
ls -lh dist/ | head -10

# Vérifier que les fichiers essentiels existent
if [ ! -f "dist/index.html" ]; then
    echo "❌ Erreur: dist/index.html manquant"
    exit 1
fi

echo "✅ Fichiers de build présents"
cd ..
echo ""

# Étape 2: Ajouter staticwebapp.config.json et redéployer
echo "📝 Préparation du déploiement..."

# Vérifier si staticwebapp.config.json existe
if [ ! -f "frontend/staticwebapp.config.json" ]; then
    echo "⚠️  staticwebapp.config.json manquant, création..."
    cat > frontend/staticwebapp.config.json << 'EOF'
{
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/images/*.{png,jpg,gif}", "/css/*"]
  },
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["anonymous"]
    }
  ],
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html",
      "statusCode": 200
    }
  },
  "globalHeaders": {
    "content-security-policy": "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:;"
  },
  "mimeTypes": {
    ".json": "application/json",
    ".js": "text/javascript",
    ".css": "text/css"
  }
}
EOF
    echo "✅ staticwebapp.config.json créé"
fi

# Étape 3: Commit et push pour déclencher le déploiement
echo ""
echo "🚀 Déclenchement du déploiement..."
echo ""

# Vérifier s'il y a des changements
if git diff --quiet frontend/; then
    echo "📝 Aucun changement détecté, création d'un commit vide pour forcer le déploiement..."
    git commit --allow-empty -m "Force frontend redeploy - fix blank page"
else
    echo "📝 Ajout des changements..."
    git add frontend/
    git commit -m "Fix frontend deployment - add staticwebapp.config.json"
fi

echo "📤 Push vers GitHub..."
git push origin main

echo ""
echo "✅ Déploiement déclenché!"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Aller sur GitHub Actions: https://github.com/YOUR_USERNAME/aia-assistant/actions"
echo "   2. Vérifier que le workflow 'Azure Static Web Apps CI/CD' démarre"
echo "   3. Attendre 3-5 minutes que le déploiement se termine"
echo "   4. Tester l'URL: https://ambitious-cliff-03a95d40f.1.azurestaticapps.net/"
echo ""
echo "💡 Si la page reste blanche après 5 minutes:"
echo "   - Vérifier les logs du workflow GitHub Actions"
echo "   - Ouvrir la console du navigateur (F12) pour voir les erreurs"
echo "   - Exécuter: ./test-deployments.sh"
