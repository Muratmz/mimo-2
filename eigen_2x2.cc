// eigen_2x2.cc
// differential alamouti, 2 x 2 MIMO
// Eigen library must be installed and linked to when compiling
// <random> is part of C++11, must inform compiler
// to compile: (on my system)
// g++ -I /usr/include/eigen3 -std=gnu++11 -o eigen_2x2 eigen_2x2.cc

#include <iostream>
#include <Eigen/Dense>
#include <complex>
#include <random>

const int LENGTH = 8;
const int N_RX = 2;
const int N_TX = 2;

int main()
{
	// message vector, M
	std::complex<double> z1(1, 2), z2(2, 3), z3(3, 4), z4(4, 5), \
			     z5(5, 6), z6(6, 7), z7(7, 8), z8(8, 9);
	Eigen::RowVectorXcd M(LENGTH);
	M << z1, z2, z3, z4, z5, z6, z7, z8;

	// generate random values from gaussian distribution
        std::random_device rd;
        std::mt19937 gen(rd());
        std::normal_distribution<> N(0, 1);

	/*
	// message vector, M
	Eigen::RowVectorXcd M(LENGTH);
	for (int i = 0; i < LENGTH; i++)
	{	
		M(i) = {N(rd), N(rd)};
	}
	*/

	std::cout << "message" << std::endl;
	std::cout << M << std::endl;
	std::cout << "decoded message" << std::endl;

	// 2x2 identity matrix, I_2
	std::complex<double> i1(1, 0), i2(0, 0), i3(0, 0), i4(1, 0);
	Eigen::Matrix2cd I_2;
	I_2 << i1, i2,
	       i3, i4;

	// radon matrix, R
	std::complex<double> r1(0, 0), r2(1, 0), r3(-1, 0), r4(0, 0);
	Eigen::Matrix2cd R;
	R << r1, r2,
	     r3, r4;

	// seed recursion, x(n - 1)'s
	std::complex<double> x1(1, 0), x2(-1, 0), x3(1, 0), x4(1, 0);
	Eigen::Matrix2cd X_st;
	X_st << x1, x2, 
	        x3, x4;

	// rayleigh channel, H
	Eigen::Matrix2cd H;
        for (int i = 0; i < N_RX; i++)
	{
		for (int j = 0; j < N_TX; j++)
			H(i, j) = {N(rd), N(rd)};
	}
	
	Eigen::Matrix2cd S;
	Eigen::Matrix2cd S_st;
	Eigen::MatrixXcd Y;
	Eigen::MatrixXcd Y_tilde(4, 1);
	Eigen::MatrixXcd Y_st_1(4, 2);
	Eigen::MatrixXcd Y_st_2(4, 1);
	Eigen::MatrixXcd Y_st(4, 2);
	Eigen::MatrixXcd A(4, 2);
	Eigen::MatrixXcd A_T(2, 4);
	Eigen::MatrixXcd A_H(2, 4);
	Eigen::Matrix2cd A_I;
	Eigen::MatrixXcd S_decode;

	for (int i = 0; i < LENGTH; i+=2)
	{
		// symbols in space-time format
		S = M(i) * I_2 + M(i + 1) * R;
		S.transposeInPlace();
		S_st << S.col(0), S.col(1).conjugate();

		// recursion produces transmitted space-time codeword
		X_st = (1 / std::sqrt(2)) * X_st * S_st;
		//std::cout << "X_st" << std::endl;
		//std::cout << X_st << std::endl;

		// received symbols
		Y = H * X_st; // 2x2
		Y_tilde << Y(0, 0), std::conj(Y(0, 1)), \
		           Y(1, 0), std::conj(Y(1, 1)); // 4x1
		
		if (i == 0)
		{
			Y_st_1 = Y_tilde.replicate(1, 2);
			// block(i, j, rows, cols)
			Y_st_1.block(0, 1, 2, 1).reverseInPlace();
			Y_st_1.block(2, 1, 2, 1).reverseInPlace();
			Y_st_2 << std::conj(Y_st_1(0, 1)), \
				-std::conj(Y_st_1(1, 1)), \
			  	std::conj(Y_st_1(2, 1)), \
				-std::conj(Y_st_1(3, 1));
			Y_st << Y_st_1.block(0, 0, 4, 1), Y_st_2;

			A = (1 / std::sqrt(2)) * Y_st;
			A_T = A.transpose();
			A_H = A_T.conjugate(); // A Hermitian
			A_I = A_H * A; // scaled identity matrix
		}
		else
		{
			// S_decode = previous A * current Y
			S_decode = (A_H / A_I(0, 0)) * Y_tilde;
			std::cout << S_decode << std::endl;

			Y_st_1 = Y_tilde.replicate(1, 2);
			// block(i, j, rows, cols)
			Y_st_1.block(0, 1, 2, 1).reverseInPlace();
			Y_st_1.block(2, 1, 2, 1).reverseInPlace();
			Y_st_2 << std::conj(Y_st_1(0, 1)), \
				-std::conj(Y_st_1(1, 1)), \
				std::conj(Y_st_1(2, 1)), \
				-std::conj(Y_st_1(3, 1));
			Y_st << Y_st_1.block(0, 0, 4, 1), Y_st_2;

			A = (1 / std::sqrt(2)) * Y_st;
			A_T = A.transpose();
			A_H = A_T.conjugate(); // A Hermitian
			A_I = A_H * A; // scaled identity matrix
		}
	}
	return 0;
}
