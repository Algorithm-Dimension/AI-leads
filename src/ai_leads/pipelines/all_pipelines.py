import subprocess

# Liste des fichiers à exécuter
pipelines = [
    "src/ai_leads/pipelines/1_pipeline_job_creation.py",
    "src/ai_leads/pipelines/2_pipeline_qualify_companies.py",
    "src/ai_leads/pipelines/3_pipeline_linkedin_contact.py",
    "src/ai_leads/pipelines/4_pipeline_lead_dataset_creation.py",
]

# Boucle pour exécuter chaque fichier
for pipeline in pipelines:
    print(f"Execution de {pipeline}...")
    result = subprocess.run(["python", pipeline], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur lors de l'execution de {pipeline} : {result.stderr}")
        break
    else:
        print(f"Execution de {pipeline} terminée avec succès.")
        print(result.stdout)

print("Tous les pipelines ont été exécutés.")
