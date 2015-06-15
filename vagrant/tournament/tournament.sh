#!bin/bash
echo "Creating or recreating tournament database..."
echo " "
psql -X -d vagrant -f tournament.sql
echo " "
echo "Tournament database created or recreated."
echo " "
echo "Running tournament_test.py..."
echo " "
python tournament_test.py
echo "Tournament_test.py completed."
echo " "
echo "Tests complete."
exit
