#!/usr/bin/python
# alamouti_BPSK_2x1.py
# Rayleigh fading channel
import numpy as np
import matplotlib.pyplot as plt

N = 1e3 # Number of bits or symbols
Eb_N0_dB = np.array(range(26))
nErr = np.array([]) # Initialize array to hold number of errors per loop

for i in range(len(Eb_N0_dB)):

    # Transmitter
    ip = np.random.randint(2, size = N) # generate 0, 1 with equal probability
    s = 2 * ip - 1 # BPSK modulation 0 -> -1, 1 -> 1

    # Alamouti STBC
    #sCode = np.zeros((2, N))
    #Reshape using Fortran-like index ordering (this is MATLAB's default)
    #sCode[:, 0::2] = (1 / np.sqrt(2)) * np.reshape(s, (2, N / 2), order = 'F') # [x1 x2 ...] 
    #sCode[:, 1::2] = (1 / np.sqrt(2)) * (np.multiply(np.kron(np.ones((1, N / 2)), np.array(
    #    [[-1], [1]])), np.flipud(np.reshape(np.conj(s), (2, N / 2), order = 'F')))) # [-x2* x1* ...]
    #print(sCode)
    sCode = (1 / np.sqrt(2)) * np.kron(np.reshape(s, (2, N / 2), order = 'F'), np.ones(2))

    h = (1 / np.sqrt(2)) * (np.random.randn(1, N) + 1j * np.random.randn(1, N)) # Rayleigh channel
    hMod = np.kron(np.reshape(h, (2, N / 2), order = 'F'), np.ones(2)) # Repeat same channel for two symbols

    n = (1 / np.sqrt(2)) * (np.random.randn(1, N) + 1j * np.random.randn(1, N)) # White Gaussian noise, 0dB variance 
    
    # Channel and noise addition
    y = np.sum(np.multiply(hMod, sCode), 0) + np.power(10, (-Eb_N0_dB[i] / 20)) * n # sum along vertical, axis 0

    # Receiver
    yMod = np.kron(np.reshape(y, (2, N / 2), order = 'F'), np.ones(2)) # [y1 y1 ... ; y2 y2 ...]
    yMod[1, :] = np.conj(yMod[1, :]) # [y1 y1 ... ; y2* y2* ...]

    # Forming the equalization matrix
    hEq = np.zeros((2, N), complex)
    hEq[:, 0::2] = np.reshape(h, (2, N / 2), order = 'F') # [h1 0 ... ; h2 0 ...]
    # [h1 h2 ... ; h2 -h1 ...]
    hEq[:, 1::2] = np.multiply(np.kron(np.ones(N / 2), np.array([[1], [-1]])), np.flipud(np.reshape(h, (2, N / 2), order = 'F'))) 
    hEq[0, :] = np.conj(hEq[0, :]) # [h1* h2* ... ; h2 -h1 ...]
    hEqPower = np.sum(np.multiply(hEq, np.conj(hEq)), 0) # sum along vertical, i.e., axis 0

    yHat = np.divide(np.sum(np.multiply(hEq, yMod), 0), hEqPower) # [h1*y1 + h2y2*, h2*y1 -h1y2*, ...]
    yHat[1::2] = np.conj(yHat[1::2])

    # Receiver - hard decision decoding
    ipHat = np.greater(yHat.real, 0) # can change boolean to binary by dividing by 1, (not neccessary for computation)

    # Counting the errors
    error = np.count_nonzero(ip - ipHat)
    nErr = np.r_[nErr, [error]]

simBer = np.divide(nErr, N) # Simulated BER
#simBer = nErr / N
EbN0Lin = np.power(10, Eb_N0_dB / 10)
theoryBer_nRx1 = np.multiply(0.5, (1 - 1 * np.power((1 + np.divide(1, EbN0Lin)), -0.5)))

p = .5 - .5 * np.power(1 + np.divide(1, EbN0Lin), -0.5) 
theoryBerMRC_nRx2 = np.multiply(np.power(p, 2), (1 + 2 * (1 - p)))

pAlamouti = 0.5 - 0.5 * (np.power(1 + np.divide(2, EbN0Lin), -0.5))
theoryBerAlamouti_nTx2_nRx1 = np.multiply(np.power(pAlamouti, 2), (1 + 2 * (1 - pAlamouti)))

plt.figure()
plt.semilogy(Eb_N0_dB, theoryBer_nRx1, marker="^", label="theory (nTx=1, nRx=1)")
plt.semilogy(Eb_N0_dB, theoryBerMRC_nRx2, marker="d", label="theory (nTx=1, nRx=2, MRC)")
plt.semilogy(Eb_N0_dB, theoryBerAlamouti_nTx2_nRx1, marker=",", linewidth=2, label="theory (nTx=2, nRx=1, Alamouti)")
plt.semilogy(Eb_N0_dB, simBer, marker="o", label="sim (nTx=2, nRx=1, Alamouti)")
plt.title("BER for BPSK and Alamouti in Rayleigh Fading Environment")
plt.xlabel("Eb / N0 (dB)")
plt.ylabel("BER")
plt.legend(loc = 3)
plt.grid()
#plt.savefig("py_plots/alamouti_BPSK_2x1.pdf")
plt.show()
