# Web API For DeGAUSS Containers

[DeGAUSS Introduction](https://degauss.org/)

[DeGAUSS geocoder](https://degauss.org/geocoder/)

[geocoder github](https://github.com/degauss-org/geocoder)

[DeGAUSS geocoder internal API](https://degauss.org/geocoding_api.html)

## If there is not enough disk space to download the image
This only affects the user running the docker/podman command in non-sudo mode, it does not affect the system configuration.

Create a file in your home directory like `touch ~/.config/containers/storage.conf`

Edit the file to something like the following (ensure that you change the username). Note that the there will need to be a path named `/data` on the machine where you are running this:
```toml
[storage]
driver="overlay"
runroot="/data/run/user/$(id -u)"
graphroot="/data/home/<user>/.local/share/containers/storage"
```

Also edit the TMPDIR environment variable

```sh
export TMPDIR=/data/tmp
```

## Steps
1) Login to the github container repository (most recent deguass builds) using a github personal access token.

The requires that the github personal access token be stored in a file named pat.txt

You will also need to change the username from `<user>` to your own username.

```sh
docker login ghcr.io -u <user> --password-stdin < pat.txt
```

2) Navigate to this directory and build from the local Dockerfile
```sh
docker build -t geocoder-api .
```

3) Run the container and name it gs.
```sh
docker run -it -d --replace --name gs \
    -v $(pwd)/logs/gunicorn:/var/log/gunicorn \
    -v $(pwd)/logs/app:/app/log \
    -p 9080:9080 localhost/geocoder-api
```

4) (optional) Test the internal geocoding.
```sh
docker exec gs ruby /app/geocode.rb "3333 Burnet Ave Cincinnati OH 45229"
```

5) Test the url-based geocoding.
```sh
curl --retry 5 "http://localhost:9080/geocode?address=3333+Burnet+Ave+Cincinnati+OH+45229"
```

6) Test the url for the geocoding API.

    [localhost Test Url](http://localhost:9080/geocode?address=3333+Burnet+Ave+Cincinnati+OH+45229)

7) Test the csv-based method (requests library must be installed)
```sh
cd testing
python test_csv_method.py
```

7) Test the csv upload method

[Test Url](http://localhost:9080/geocode_csv)

7) (when desired) Stop and remove the container.
```sh
docker stop gs && docker rm gs
```

## Alternative Method with Docker-compose
**Not currently working**

1) use docker-py version compatible with v1 of docker compose `pip install docker==6.1.3`
1) if not installed, run `pip install docker-compose`
2) run `docker-compose up -d`