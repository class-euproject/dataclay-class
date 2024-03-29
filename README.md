# dataclay-class

This repository contains the file containing the data model and the docker files
to deploy dataClay with the model.

# Python dependencies

The Python used is `3.6.9`. The following python packages must be installed as well:

```
python3 -m pip install geolib dataclay requests pygeohash
```

# Install docker-compose
```
sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

# Build

To build the dockers containing the data model defined below, use the script located in `./build/build_dockers.sh`, which generates the dataclay dockers.

## Model 

<p align="center"><img src="./imgs/class-dataclay-model.png" alt="DataClay Model" title="DataClay Model"/></p>

`detected_object` attribute in `Event` class is needed for dataClay federation purposes. `objects_refs` attribute in `EventSnapshot` class is provided for PyWren to retrieve objects remotely. `objects` attribute in `EventSnapshot` is used to store all objects in one single make\_persistent call to avoid extra visits to dataClay.


# Deployment

First the exposed dataclay IP should be changed to the IP of your cloud resource, that is, updating the `./deploy/dataclay/docker-compose.yml` file replacing the content of **EXPOSED_IP_FOR_CLIENT=${IP}** by the actual IP.

Then, go to the `./deploy/` folder and execute the script that deploys the dockers:
```
./launch_dockers.sh
```

In order to populate the dataClay database with information, a simulator code is provided in the `app/` folder to fill it with actual data. The following dependencies are required:
```bash
pip3 install pandas
```

And to run it, execute the following command:
```python
cd app/
python3 run_demo.py
```
