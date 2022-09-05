docker build -t tool_mongodb -f MongoDockerfile .
if [[ $(docker run -d -p 27888:27017 --name tool-mongodb-docker tool_mongodb 2> /dev/null) ]]; then
  echo "Mongo Docker started"
  echo "Performing one time import of study data into mongo"
  docker exec tool-mongodb-docker bash -c 'mongoimport --db lidar_data --collection mutations --file mongo_db_data/mutations.json --jsonArray'
  docker exec tool-mongodb-docker bash -c 'mongoimport --db lidar_data --collection assets4 --file mongo_db_data/assets4.json --jsonArray'
  docker exec tool-mongodb-docker bash -c 'mongoimport --db lidar_data --collection final_data --file mongo_db_data/final_data.json --jsonArray'
  docker exec tool-mongodb-docker bash -c 'echo "db.createUser({user: \"lidarUser\", pwd:  \"lidarUserPW\",  roles: [ { role: \"readWrite\", db: \"lidar_data\" }] })" > tmp.js && mongo lidar_data tmp.js'
else
  echo "Study data has already been imported, bringing up mongo container if not already started"
  docker start tool-mongodb-docker
fi