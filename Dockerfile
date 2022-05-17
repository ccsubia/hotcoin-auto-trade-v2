FROM ubuntu:20.04 
RUN apt update && apt install git python3 pip -y 
COPY ./ /hotcoin-auto-trade-v2/
WORKDIR /hotcoin-auto-trade-v2
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package && pip install -r requirements.txt
CMD [ "sh", "/init.sh" ]