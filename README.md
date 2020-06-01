## scrobble

### Workflow

create session
create rounds
create user
for users: join session as user

for rounds:
send string to users
while timer:
log user responses
calculate scores
update leaderboard
send leaderboard to users


### Quick Start Server

```
cd server
conda create -n scrobble python=3.7
source activate scrobble
pip install -r webapp/requirements.txt
./start.sh
```

### Local Dev
```
cd server
./start.sh
```


### Deploy
```
cd server
./deploy.sh
```

