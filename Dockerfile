FROM ghcr.io/degauss-org/geocoder:v3.4.0

# Install necessary packages
RUN apt-get update && apt-get install -y python3-pip curl

# Install Flask and gunicorn
RUN pip3 install flask gunicorn requests

# Expose port 9080
EXPOSE 9080

# Copy the Flask app into the container
COPY app.py /app/app.py
COPY templates /app/templates
COPY conf /app/conf

# Set the working directory
WORKDIR /app

# create log directory
RUN mkdir -p /var/log/gunicorn

# Override the ENTRYPOINT with gunicorn
ENTRYPOINT ["gunicorn","-c","conf/gunicorn.conf.py", "-w","2","--bind", "0.0.0.0:9080", "--log-level", "debug", "app:app"]