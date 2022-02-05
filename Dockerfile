FROM amazonlinux:2
RUN yum install shadow-utils.x86_64 -y
RUN yum install -y python3 python3-pip
RUN yum -y install git
RUN python3 -m pip install -U pip
RUN python3 -m pip install google-api-python-client google-auth boto3 pyjwt
RUN python3 -m pip install git+https://github.com/mailchimp/mailchimp-transactional-python.git
COPY . .
# RUN groupadd -r archiver && useradd -r -g archiver archiver
# RUN chown archiver /home
# USER archiver
CMD ["python3", "-u", "core.py"]
