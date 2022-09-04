docker pull mongo:5.0.10
docker run -d -p 27018:27018 --name mongodb-docker mongo:5.0.10
docker exec mongodb-docker bash -c 'echo "db.createUser({user: \"lidarUser\", pwd:  \"lidarUserPW\",  roles: [ { role: \"readWrite\", db: \"lidar_data\" }] })" > tmp.js && mongo lidar_data tmp.js'