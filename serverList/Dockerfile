From python:3.6.12
COPY ./updateServerList.py /usr/
COPY .aws /root/.aws
ENV HTTPSECRETKEY vxdfgrsjAsdferukhdf487jw9er1g5dsr896dfg4
ENV SECRET SEC561ad04e665fdf4f889c77572f50066965df1ef364311c094e3f8bb07df4f0dd
ENV ACCESS_TOKEN c59842fdd612c145b61782779cbe99615399a4190f1a488d0fe14d0bbbf042ce
RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple/ flask requests boto3 
CMD python3 /usr/updateServerList.py
