# Common
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import time
import gc
import requests

# Qiskit
from qiskit import __qiskit_version__ as qiskit_version
from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit, execute, Aer
from quantastica.qiskit_toaster import ToasterBackend

# pyQuil
from pyquil import Program, get_qc
from pyquil.gates import H, CPHASE, SWAP, MEASURE

# Cirq
import cirq

# qsim
from qsimcirq import qsim


def qft_qiskit(n):
    qc = QuantumCircuit()

    q = QuantumRegister(n, 'q')
    c = ClassicalRegister(n, 'c')

    qc.add_register(q)
    qc.add_register(c)

    for j in range(n):
        for k in range(j):
            qc.cu1(math.pi/float(2**(j-k)), q[j], q[k])
        qc.h(q[j])

    for i in range(n):
        qc.measure(q[i], c[i])
        
    return qc


def qft_pyquil(n):
    p = Program()

    ro = p.declare('ro', memory_type='BIT', memory_size=n)

    for j in range(n):
        for k in range(j):
             p.inst(CPHASE(math.pi/float(2**(j-k)), j, k))
        p.inst(H(j))

    for i in range(n):
        p.inst(MEASURE(i, ro[i]))
        
    return p


def qft_cirq(n):
    q = cirq.GridQubit.rect(1, n)

    gates = []
    for j in range(n):
        for k in range(j):
             gates.append(cirq.ZPowGate(exponent=math.pi/float(2**(j-k))).controlled()(q[j], q[k]))
        gates.append(cirq.H(q[j]))

    for i in range(n):
        gates.append(cirq.measure(q[i], key='c' + str(i)))
    
    circ = cirq.Circuit(gates)

    return circ


def qft_qsim(n):
    qsim_c = str(n) + "\n"

    t = 0
    for j in range(n):
        for k in range(j):
            qsim_c += str(t) + " cp " + str(j) + " " + str(k) + " " + str(math.pi/float(2**(j-k))) + "\n"
            t += 1
        qsim_c += str(t) + " h " + str(j) + "\n"
        t += 1

    # No measurement gate...
    # for i in range(n):
    #     qsim_c += str(t) + " m " + str(i) + "\n"
        
    qsim_c += "\n"

    return qsim_c


def benchmark_qft_qiskit(from_qubits, to_qubits, results):
    gc.disable()

    # Toaster results column name
    r = requests.get(url="http://127.0.0.1:8001/info")
    toaster_version = r.json()["version"]
    col_qiskit_toaster = "Qiskit+Toaster " + toaster_version
    results[col_qiskit_toaster] = np.nan

    # Aer results column name
    col_qiskit_aer = "Qiskit+Aer " + qiskit_version["qiskit-aer"]
    results[col_qiskit_aer] = np.nan

    # Get backends
    aer_backend = Aer.get_backend("qasm_simulator")
    toaster_backend = ToasterBackend.get_backend("qasm_simulator")

    for i in range(from_qubits, to_qubits + 1):
        circ = qft_qiskit(i)

        # Repeat multiple times for small number of qubits and get best time
        repeat = 4 if i <= 20 else 1

        # Qiskit with Toaster backend
        toaster_time = np.nan
        for r in range(repeat):
            gc.collect()
            start_time = time.time()
            job = execute(circ, backend=toaster_backend, shots=1)
            result = job.result()
            elapsed_time = (time.time() - start_time) * 1000
            toaster_time = elapsed_time if np.isnan(toaster_time) else min(toaster_time, elapsed_time)
        results[col_qiskit_toaster][i] = toaster_time

        # Qiskit with Aer backend
        aer_time = np.nan
        for r in range(repeat):
            gc.collect()
            start_time = time.time()
            job = execute(circ, backend=aer_backend, shots=1)
            result = job.result()
            elapsed_time = (time.time() - start_time) * 1000
            aer_time = elapsed_time if np.isnan(aer_time) else min(aer_time, elapsed_time)
        results[col_qiskit_aer][i] = aer_time


    gc.enable()


def benchmark_qft_pyquil(from_qubits, to_qubits, results):
    gc.disable()

    # QVM results column name
    r = requests.post(url="http://127.0.0.1:5000", json={ "type": "version" })
    qvm_version = r.text
    col_pyquil_qvm = "pyQuil+QVM " + qvm_version
    results[col_pyquil_qvm] = np.nan

    for i in range(from_qubits, to_qubits + 1):

        circ = qft_pyquil(i)
        circ.wrap_in_numshots_loop(1)

        # Repeat multiple times for small number of qubits and get best time
        repeat = 4 if i <= 20 else 1

        # pyQuil with QVM backend
        qc = get_qc(str(i) + 'q-qvm')
        
        qvm_time = np.nan
        for r in range(repeat):
            gc.collect()
            start_time = time.time()
            result = qc.run(circ)        
            elapsed_time = (time.time() - start_time) * 1000
            qvm_time = elapsed_time if np.isnan(qvm_time) else min(qvm_time, elapsed_time)
        results[col_pyquil_qvm][i] = qvm_time

    gc.enable()

        
def benchmark_qft_cirq(from_qubits, to_qubits, results):
    gc.disable()

    col_cirq = "Cirq " + cirq.__version__
    results[col_cirq] = np.nan

    for i in range(from_qubits, to_qubits + 1):
        simulator = cirq.Simulator()

        circ = qft_cirq(i)

        # Repeat multiple times for small number of qubits and get best time
        repeat = 4 if i <= 20 else 1

        # Cirq simulator
        cirq_time = np.nan
        for r in range(repeat):
            gc.collect()
            start_time = time.time()
            result = simulator.run(circ, repetitions=1)
            elapsed_time = (time.time() - start_time) * 1000
            cirq_time = elapsed_time if np.isnan(cirq_time) else min(cirq_time, elapsed_time)
        results[col_cirq][i] = cirq_time

    gc.enable()


def benchmark_qft_qsim(from_qubits, to_qubits, results):
    gc.disable()

    col_qsim = "qsim"
    results[col_qsim] = np.nan

    for i in range(from_qubits, to_qubits + 1):

        circ = qft_qsim(i)

        qsim_options = {
            "c": circ,
            "i": "",
            "t": 1,
            "v": 0
        }

        # Repeat multiple times for small number of qubits and get best time
        repeat = 4 if i <= 20 else 1

        qsim_time = np.nan
        for r in range(repeat):
            gc.collect()
            start_time = time.time()
            result = qsim.qsim_simulate(qsim_options)
            elapsed_time = (time.time() - start_time) * 1000
            qsim_time = elapsed_time if np.isnan(qsim_time) else min(qsim_time, elapsed_time)
        results[col_qsim][i] = qsim_time

    gc.enable()


def benchmark_qft(from_qubits, to_qubits):
    results = pd.DataFrame(index=range(from_qubits, to_qubits + 1), columns=[])
    
    # Qiskit
    benchmark_qft_qiskit(from_qubits, to_qubits, results)
    
    # pyQuil
    benchmark_qft_pyquil(from_qubits, to_qubits, results)

    # Cirq
    benchmark_qft_cirq(from_qubits, to_qubits, results)

    # qsim
#    benchmark_qft_qsim(from_qubits, to_qubits, results)

    print(results)

    plt.figure(dpi=300)
    plt.title("QFT")
    plt.xlabel("Qubits")
    plt.ylabel("Time (ms)")
    plt.xticks(range(from_qubits, to_qubits + 1, 2))
    plt.yscale("log")
    plt.plot(results)
    plt.grid(which='both')
    plt.legend(loc="upper left", labels=results.columns)
    plt.savefig("output/benchmark_qft.png")


benchmark_qft(1, 27)
