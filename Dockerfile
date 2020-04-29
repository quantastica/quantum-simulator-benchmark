FROM ubuntu:18.04

RUN apt-get update

RUN apt-get install -y \
	software-properties-common \
	build-essential \
	python3 \
	python3-pip \
	libzmq3-dev \
	wget \
	curl


###
# python and pip
###

RUN pip3 install -U pip
RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
RUN rm -f /usr/bin/pip && ln -s /usr/bin/pip3 /usr/bin/pip
RUN python --version
RUN pip --version
RUN pip install numpy pandas matplotlib


###
# Install Qiskit
###

RUN pip install qiskit


###
# Install pyQuil and Forest SDK
###

RUN pip install pyquil
RUN wget http://downloads.rigetti.com/qcs-sdk/forest-sdk-2.19.0-linux-deb.tar.bz2 -O ~/forest-sdk-2.19.0-linux-deb.tar.bz2
RUN tar -xjvf ~/forest-sdk-2.19.0-linux-deb.tar.bz2 -C ~/
RUN yes | ~/forest-sdk-2.19.0-linux-deb/forest-sdk-2.19.0-linux-deb.run

RUN quilc -v
RUN qvm -v


###
# Install Qubit Toaster
###

RUN curl https://quantastica.com/toaster/install | /bin/sh

RUN pip install quantastica-qiskit-toaster

RUN qubit-toaster -v


###
# Install Cirq and qsim
###

RUN pip install cirq
RUN pip install qsimcirq


###
# Make output dir
###

RUN mkdir /root/output/


###
# Copy benchmark scripts
###

COPY ./benchmark_qft.py /root/benchmark_qft.py
COPY ./run_benchmarks.sh /root/run_benchmarks.sh


###
# Run benchmarks
###

WORKDIR "/root/"
ENTRYPOINT ["/bin/bash", "/root/run_benchmarks.sh"]
