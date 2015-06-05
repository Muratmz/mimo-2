#!/usr/bin/python
# alamouti_BPSK_2x2.py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
#from matplotlib import rc
 
m_bits = 1e6 # number of bits 
n_rx = 2 # number of receive antenna (Rx)
Eb_N0_dB = np.arange(26, dtype = int) # SNR per bit 
n_errors = np.zeros(26, dtype = int) # initialize error array
hEq = np.array(np.zeros((n_rx * 2, m_bits), dtype = complex)) # initialize equalizer array

for i in Eb_N0_dB:

    # transmitter
    data = np.random.randint(2, size = m_bits) # generate 0, 1 with equal probability
    s = 2 * data - 1 # BPSK modulation

    # alamouti space time block code (STBC)
    # rotate linear bit string in space by chunks of two, kron-ing gives us the desired repetition for two time slots
    # s1 s1 s2 s2 s3 s3 s4 s4 ...
    # s2 s2 s3 s3 s4 s4 s5 s5 ...
    # this works because the receiver is taking care of the conjugation, etc.
    sCode = 1 / np.sqrt(2) * np.kron(np.reshape(s, (2, m_bits / 2), order = 'F'), np.ones(2)) # fortran-like index order

    # channel
    h = 1 / np.sqrt(2) * (np.random.randn(n_rx, m_bits) + 1j * np.random.randn(n_rx, m_bits)) # rayleigh channel
    w = 1 / np.sqrt(2) * (np.random.randn(n_rx, m_bits) + 1j * np.random.randn(n_rx, m_bits)) # white gaussian noise
    y = np.zeros((n_rx, m_bits), complex) # initialize receive array
    yMod = np.zeros((n_rx * 2, m_bits), dtype = complex)
    hMod = np.zeros((n_rx * 2, m_bits), dtype = complex)

    # repeat the same channel for two symbols
    for k in range(n_rx):

        hMod = np.kron(np.reshape(h[k, :], (2, m_bits / 2), order = 'F'), np.ones(2)) 
        hMod[0, 1::2] = np.conj(np.kron(np.reshape(h[k, :], (2, m_bits / 2), order = 'F'), np.ones(2))[1, 1::2])
        hMod[1, 1::2] = -np.conj(np.kron(np.reshape(h[k, :], (2, m_bits / 2), order = 'F'), np.ones(2))[0, 1::2])
    
        # combine channel and add WGN
        y[k, :] = np.sum(np.multiply(hMod, sCode), axis = 0) + np.multiply(np.power(10, -Eb_N0_dB[i] / 20), w[k, :])

        # receiver
        yMod[2 * k:2 * k + 2, :] = np.kron(np.reshape(y[k, :], (2, m_bits / 2), order = 'F'), np.ones(2))

        # create equalization matrix
        hEq[2 * k:2 * k + 2, :] = hMod
        hEq[2 * k, 0::2] = np.conj(hEq[2 * k, 0::2])
        hEq[2 * k + 1, 1::2] = np.conj(hEq[2 * k + 1, 1::2])

    # equalization process
    hEqPower = np.sum(hEq * np.conj(hEq), axis = 0)
    yHat = np.divide(np.sum(hEq * yMod, axis = 0), hEqPower) # [h1*y1 + h2y2*, h2*y1 -h1y2*, ... ]
    yHat[1::2] = np.conj(yHat[1::2])

    # receiver - hard decision decoding
    received_data = np.greater(yHat.real, 0) # can change boolean to binary by dividing by 1, (not neccessary for computation)

    # count errors
    n_errors[i] = np.count_nonzero(data - received_data)

simBer = np.divide(n_errors, m_bits) # Simulated BER

EbN0Lin = np.power(10, Eb_N0_dB / 10) # Eb/N0_dB = 10 * log10(Eb/N0)

pAlamouti = 0.5 - 0.5 * (np.power(1 + np.divide(2, EbN0Lin), -0.5))
theoryBerAlamouti_n_tx2_n_rx1 = np.multiply(np.power(pAlamouti, 2), (1 + 2 * (1 - pAlamouti)))

# plot results
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = [r'\usepackage{units}']
plt.semilogy(Eb_N0_dB, theoryBerAlamouti_n_tx2_n_rx1, marker=",", linewidth=2, label=r"theoretical: $\mathbf{n_t=2}$, $\mathbf{n_r=1}$")
plt.semilogy(Eb_N0_dB, simBer, marker='o', label=r"simulated: $\mathbf{n_t=2}$, $\mathbf{n_r=2}$")
plt.title(r"BER: BPSK, Alamouti, Rayleigh Fading")
plt.xlabel(r"$\nicefrac{\mathbf{E_b}}{\mathbf{N_0}} \mathbf{(dB)}$", fontsize = 16)
plt.ylabel(r"BER", fontsize=16)
plt.legend(loc = 1)
plt.grid()
plt.tight_layout()
#plt.savefig("py_plots/alamouti_BPSK_2x2.pdf")
plt.show()
