
simple_matrix_ifelse:                   
	MUL	R0, %blockIdx, %blockDim
	ADD	R0, R0, %threadIdx
	CONST	 R1, #8
	ADD	R1, R0, R1
	LDR	R1, R1	
	LDR	R2, R0 	
	CMP	R2, R1
	BRnz .LBB0_2
	CMP R0 R0
 	BRz	.LBB0_1
.LBB0_1:                                
	CONST	 R1, #16 
	ADD	R0, R0, R1
	STR	R0, R2 
	CMP R0 R0
 	BRz	.LBB0_3
.LBB0_2:                                
	CONST	 R2, #16
	ADD	R0, R0, R2
	STR	R0, R1 
.LBB0_3:                                
	RET