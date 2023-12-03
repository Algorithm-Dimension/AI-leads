# AI-leads

* Poetry
- git pull
- cd to the location containing poetry.lock and pyproject.toml
- poetry install --no-dev : install only dependancies needed to run the project
- poetry run python src/ai_leads/ui/dash_app/index.py 

* Deployment
- Lien du serveur: http://13.38.119.82:8050 (http et non https)
- EC2 AWS Ubuntu: ssh -i remy_key.pem ubuntu@ec2-13-38-119-82.eu-west-3.compute.amazonaws.com
- Deploy via nohup
- nohup poetry run python src/ai_leads/ui/dash_app/index.py > dash_app.log 2>&1 &
- ps aux | grep "python src/ai_leads/ui/dash_app/index.py" : check the process status
- kill PID : stop the app
