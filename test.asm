CONST R8, #0
CONST R9, #8
CONST R10, #16


if_else:                                ; @if_else
	MUL	R0, %blockIdx, %blockDim
	ADD	R0, R0, %threadIdx
	CONST	 R1, #1
	MUL	R1, R0, R1
	ADD	R1, R8, R1
	LDR	R1, R1
	CONST	 R2, #11
	CMP	R1, R2
	BRn	.LBB0_2
	CMP R0 R0
 	BRz	.LBB0_1
.LBB0_1:                                ; %if.then
	CONST	 R1, #1
	MUL	R0, R0, R1
	ADD	R0, R10, R0
	CONST	 R1, #1
	STR	R0, R1
	CMP R0 R0
 	BRz	.LBB0_3
.LBB0_2:                                ; %if.else
	CONST	 R1, #1
	MUL	R0, R0, R1
	ADD	R0, R10, R0
	CONST	 R1, #2
	STR	R0, R1
.LBB0_3:                                ; %if.end
	RET