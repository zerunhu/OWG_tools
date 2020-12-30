From alpine:3.8
RUN mkdir -p /go/src
WORKDIR /go/src
COPY prometheus-dingtalk .
COPY conf/conf.ini conf/conf.ini
COPY template/template.tpl template/template.tpl
CMD ./prometheus-dingtalk