# tạo container để chạy RS
# đẩy code vào folder
# viết API
# docker build + Dockerfile để tạo image
# docker run để tạo container

FROM python:3.9
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./flask_api.py .
EXPOSE 5000
CMD ["python", "flask_api.py"]


# Use a minimal base image
# FROM python:3.9-alpine
# # Install required system packages

# RUN apk add --no-cache \
#     build-base \
#     libressl-dev \
#     libffi-dev \
#     g++ \
#     gcc \
#     musl-dev \
#     gfortran \
#     lapack-dev \
#     libxml2-dev \
#     libxslt-dev \
#     jpeg-dev \
#     zlib-dev \
#     openblas-dev

# # Install pytorch build for cpu only
# # RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# # RUN pip install --no-cache-dir \
# #     scipy['sparse'] \
# #     scikit-learn 
# # copy requirement file
# COPY ./requirements.txt .
# # Install numpy and scipy
# RUN pip install --no-cache-dir -r requirements.txt
# # Remove unnecessary build dependencies
# RUN apk del \
#     build-base \
#     libressl-dev \
#     libffi-dev \
#     g++ \
#     gcc \
#     musl-dev \
#     gfortran \
#     lapack-dev \
#     libxml2-dev \
#     libxslt-dev \
#     jpeg-dev \
#     zlib-dev \
#     openblas-dev
# # Set the working directory
# WORKDIR /app
# # Copy your application code
# COPY ./flask_api.py .
# # Expose app
# EXPOSE 5000
# # Run app
# CMD ["python", "flask_api.py"]
