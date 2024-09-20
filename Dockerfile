FROM python:3.11

WORKDIR /usr/src/app

# Copy the requirements first to cache them.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything to the container. Note that in the development environment 
# the code mounted through volumes takes precedence over the copied code. 
COPY . .

# Ensure entrypoint.sh is executable.
RUN chmod +x entrypoint.sh
