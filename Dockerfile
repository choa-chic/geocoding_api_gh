FROM ghcr.io/degauss-org/geocoder:v3.4.0

# Install necessary packages
RUN apt-get update && apt-get install -y python3-pip curl

# Set the working directory
COPY requirements.txt .

# Install Flask and gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app into the container
WORKDIR /app
COPY app/*.py .
COPY templates ../templates
COPY conf ../conf

# Expose port 9080, 8502
EXPOSE 9080 8502

# create log directory
RUN mkdir -p /var/log/gunicorn

# Override the ENTRYPOINT with gunicorn
ENTRYPOINT ["sh","-c","gunicorn -c conf/gunicorn.conf.py -w 4 --bind 0.0.0.0:9080 --log-level debug app:app \
    & streamlit run --server.port 8502 streamlit_app.py"]