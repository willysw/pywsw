# Beam Notes

## FEM Process

### Basic Definitions

$$\begin{aligned}
\vec{0} &= 
	\overbrace{
	\mathbf{K}\cdot\mathbf{z} + \mathbf{f_{fe}} 
	} ^ \textrm{internal}
	+
	\overbrace{
	\mathbf{f_{super}} + \mathbf{f_{rxn}}
	} ^ \textrm{external}
\\\\
\mathbf{z} &= \begin{bmatrix}
	z_0 \\ z_1 \\ \vdots \\ z_{2n-1}  \\ z_{2n}
\end{bmatrix} = 
\begin{bmatrix} u_0 \\ \phi_0 \\ \vdots \\ u_1  \\ \phi_1 \end{bmatrix}
,\quad
\mathbf{f} = \begin{bmatrix} V_0 \\ M_0 \\ \vdots \\ V_1 \\ M_1 \\ \end{bmatrix}
\\\\
\mathbf{K} &=
EI \begin{bmatrix}
	k_{0,0} & \cdots & k_{0,2n} \\
	\vdots & \ddots & \vdots \\
	k_{2n,0} & \cdots & k_{2n,2n} \\
	\end{bmatrix}
\end{aligned}$$
For a single element:
$$\begin{aligned}
z &= \begin{bmatrix} u_0 \\ \phi_0 \\ u_1  \\ \phi_1 \end{bmatrix}
\,\quad
f = \begin{bmatrix} V_0 \\ M_0 \\ V_1 \\ M_1 \\ \end{bmatrix}
\\\\
\mathbf{K} &=
EI \begin{bmatrix}
	-\frac{12}{L^3} & -\frac{6}{L^2} & \frac{12}{L^3} & -\frac{6}{L^2} \\
	\frac{6}{L^2} & \frac{4}{L} & -\frac{6}{L^2} & \frac{2}{L} \\
	\frac{12}{L^3} & \frac{6}{L^2} & -\frac{12}{L^3} & \frac{6}{L^2} \\
	\frac{6}{L^2} & \frac{2}{L} & -\frac{6}{L^2} & \frac{4}{L} \\
	\end{bmatrix}
\\\\
\mathbf{f_{fe}} &=
	\begin{bmatrix}
		1 & 0 & -\frac{3}{L^2} & \frac{2}{L^3} \\
		0 & -1 & \frac{2}{L} & -\frac{1}{L^2} \\
		0 & 0 & \frac{3}{L^2} & -\frac{2}{L^3} \\
		0 & 0 & \frac{1}{L} & -\frac{1}{L^2} \\
		\end{bmatrix}
	\begin{bmatrix} 
		\Omega^{(0)} \\ \Omega^{(1)} \\
		\Omega^{(2)} \\ \Omega^{(3)}
		\end{bmatrix}
\end{aligned}$$
## Partitioning
$$\vec{0} =
	\begin{bmatrix}
		\left[\mathbf{K_{r,\,z}}\right] & 
			\left[\mathbf{K_{r,\,z?}}\right] \\
		\left[\mathbf{K_{r?,\,z}}\right] & 
			\left[\mathbf{K_{r?,\,z?}}\right] \\
		\end{bmatrix}
	\cdot \begin{bmatrix}
		\left[\mathbf{z_{z}}\right] \\
		\left[\mathbf{z_{z?}}\right]
		\end{bmatrix}
	+ \begin{bmatrix}
		\left[\mathbf{f_{fe,\,r}}\right] \\
		\left[\mathbf{f_{fe,\,r?}}\right]
		\end{bmatrix}
	+ \begin{bmatrix}
		\left[\mathbf{f_{super,\,r}}\right] \\
		\left[\mathbf{f_{super,\,r?}}\right]
		\end{bmatrix}
	+ \begin{bmatrix}
		\left[\mathbf{f_{rxn,\,r}}\right] \\
		\left[\mathbf{f_{rxn,\,r?}}\right]
		\end{bmatrix}
$$
The top partition can be used to find $\mathbf{z_{z?}}$ by:
$$\begin{align}
\vec{0} &= \mathbf{K_{r, z}}\cdot\mathbf{z_z}
	+ \mathbf{K_{r, z?}}\cdot\mathbf{z_{z?}}
	+ \mathbf{f_{fe,\,r}}
	+ \mathbf{f_{super,\,r}}
	+ \mathbf{f_{rxn,\,r}}
\\\\
- \mathbf{K_{r, z?}}\cdot\mathbf{z_{z?}} &=
	  \mathbf{K_{r, z}}\cdot\mathbf{z_z}
	+ \mathbf{f_{fe,\,r}}
	+ \mathbf{f_{super,\,r}}
	+ \mathbf{f_{rxn,\,r}}
\\\\
\mathbf{z_{z?}} &=
	-\mathbf{K_{r, z?}}\cdot\left(
		  \mathbf{K_{r, z}}\cdot\mathbf{z_z}
		+ \mathbf{f_{fe,\,r}}
		+ \mathbf{f_{super,\,r}}
		+ \mathbf{f_{rxn,\,r}}
		\right) \tag{1} \\
\end{align}$$
Then $\mathbf{z}$ can be used to find $\mathbf{f_{rxn,\,r?}}$ by:
$$\begin{align}
\vec{0} &=
	\mathbf{K_{r?,\,z}} \cdot \mathbf{z_{z}}
	+ \mathbf{K_{r?,\,z?}} \cdot \mathbf{z_{z?}}
	+ \mathbf{f_{fe,\,r?}}
	+ \mathbf{f_{super,\,r?}}
	+ \mathbf{f_{rxn,\,r?}}
\\\\
\mathbf{f_{rxn,\,r?}} &= -\left(
	\mathbf{K_{r?,\,z}} \cdot \mathbf{z_{z}}
	+ \mathbf{K_{r?,\,z?}} \cdot \mathbf{z_{z?}}
	+ \mathbf{f_{fe,\,r?}}
	+ \mathbf{f_{super,\,r?}}
	\right) \tag{2} \\
\end{align}$$