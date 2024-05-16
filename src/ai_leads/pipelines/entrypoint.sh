#!/bin/bash

#!/bin/bash

# Exécution de la pipeline 1
echo "Exécution de la pipeline 1..."
python3 src/ai_leads/pipelines/1_pipeline_job_creation.py

# Vérifier si la pipeline 1 s'est bien exécutée
if [ $? -ne 0 ]; then
  echo "La pipeline 1 a échoué. Arrêt de l'exécution."
  exit 1
fi

# Exécution de la pipeline 2
echo "Exécution de la pipeline 2..."
python3 src/ai_leads/pipelines/2_pipeline_qualify_companies.py

# Vérifier si la pipeline 2 s'est bien exécutée
if [ $? -ne 0 ]; then
  echo "La pipeline 2 a échoué. Arrêt de l'exécution."
  exit 1
fi

# Exécution de la pipeline 3
echo "Exécution de la pipeline 3..."
python3 src/ai_leads/pipelines/3_pipeline_linkedin_contact.py

# Vérifier si la pipeline 3 s'est bien exécutée
if [ $? -ne 0 ]; then
  echo "La pipeline 3 a échoué. Arrêt de l'exécution."
  exit 1
fi

# Exécution de la pipeline 4
echo "Exécution de la pipeline 4..."
python3 src/ai_leads/pipelines/4_pipeline_lead_dataset_creation.py

# Vérifier si la pipeline 4 s'est bien exécutée
if [ $? -ne 0 ]; then
  echo "La pipeline 4 a échoué. Arrêt de l'exécution."
  exit 1
fi

echo "Toutes les pipelines se sont exécutées avec succès."
