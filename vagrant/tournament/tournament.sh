#!bin/bash
echo "Creating or recreating tournament database..."
psql -X -d vagrant -f tournament.sql
echo "Tournament database created or recreated."
echo "Running tournament_test.py..."
python tournament_test.py
echo "Tournament_test.py completed."
echo "Tests complete."
exit
