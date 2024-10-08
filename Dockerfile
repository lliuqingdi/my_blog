FROM python:3.9
MAINTAINER lyy


# Set the working directory
WORKDIR /soft

# Copy the requirements.txt file
COPY ./requirements.txt /soft/requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Install the dependencies from requirements.txt
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/



# Run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
