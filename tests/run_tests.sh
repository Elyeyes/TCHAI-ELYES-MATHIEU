#!/bin/bash

# Script pour exécuter tous les tests de sécurité
# Usage: ./tests/run_tests.sh

echo "================================================"
echo "   TESTS DE SÉCURITÉ - Système Tchaî"
echo "================================================"
echo ""

# Vérifier que le serveur principal est lancé
echo "Assurez-vous que l'API principale tourne sur le port 5000"
read -p "Appuyez sur Entrée pour continuer..."


echo ""
echo "================================================"
echo "TEST 1: Modification du fichier de données"
echo "================================================"
echo "Voulez-vous éxecuter le test? (o/n)"
read -p "> " response

if [ "$response" = "o" ] || [ "$response" = "O" ]; then
    python tests/modif_fichier.py
    
fi


echo ""
echo "================================================"
echo "TEST 2: Suppresion d'une transaction"
echo "================================================"
echo "Voulez-vous éxecuter le test? (o/n)"
read -p "> " response

if [ "$response" = "o" ] || [ "$response" = "O" ]; then
    python tests/supr_transac.py
    
fi

echo ""
echo "================================================"
echo "   TESTS TERMINÉS"
echo "================================================"
echo ""
echo "Consultez le README.md pour plus d'informations"