# lsi-vector-model

Semestral project for the BI-VWM (Searching the web and multimedial databases) subject, summer semester 2020/2021 by
Daniel Bukač ([bukacdan@fit.cvut.cz](mailto:bukacdan@fit.cvut.cz)) and Matěj Latka ([latkamat@fit.cvut.cz](mailto:latkamat@fit.cvut.cz)).

# Hosting
The project is hosted at [https://lsi-vector.krupizde.eu](https://lsi-vector.krupizde.eu).

# Documentation
Documentation and results are provided in [docs.md](https://gitlab.fit.cvut.cz/latkamat/lsi-vector-model/blob/master/docs/docs.md) or at [https://lsi-vector.krupizde.eu/about](https://lsi-vector.krupizde.eu)

# Installation
If you want to install the project locally, please follow these steps:
1. [Install Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
2. Clone the repository with SSH
```shell
git clone git@gitlab.fit.cvut.cz:latkamat/lsi-vector-model.git  
```
or with HTTPS
```shell
git clone https://gitlab.fit.cvut.cz/latkamat/lsi-vector-model.git
```
# Running the project
1. Go to the project directory
```shell
cd lsi-vector-model
```
2. Run container(s) normally
```shell
docker-compose up
```
or in the background 
```shell
docker-compose up -d
```
3. Open [http://localhost:5000](http://localhost:5000) in browser and enjoy :slight_smile:

# Stopping the project
In the `lsi-vector-model` directory, run
```shell
docker-compose down
```

