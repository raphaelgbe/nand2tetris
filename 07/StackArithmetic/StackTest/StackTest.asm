//push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
//eq
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE0
D;JEQ
D=0
@AFTERTRUEFALSE1
0;JMP
(REGTRUE0)
D=-1
(AFTERTRUEFALSE1)
@SP
A=M
M=D
@SP
M=M+1
//push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
//eq
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE2
D;JEQ
D=0
@AFTERTRUEFALSE3
0;JMP
(REGTRUE2)
D=-1
(AFTERTRUEFALSE3)
@SP
A=M
M=D
@SP
M=M+1
//push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
//eq
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE4
D;JEQ
D=0
@AFTERTRUEFALSE5
0;JMP
(REGTRUE4)
D=-1
(AFTERTRUEFALSE5)
@SP
A=M
M=D
@SP
M=M+1
//push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
//lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE6
D;JLT
D=0
@AFTERTRUEFALSE7
0;JMP
(REGTRUE6)
D=-1
(AFTERTRUEFALSE7)
@SP
A=M
M=D
@SP
M=M+1
//push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
//lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE8
D;JLT
D=0
@AFTERTRUEFALSE9
0;JMP
(REGTRUE8)
D=-1
(AFTERTRUEFALSE9)
@SP
A=M
M=D
@SP
M=M+1
//push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
//lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE10
D;JLT
D=0
@AFTERTRUEFALSE11
0;JMP
(REGTRUE10)
D=-1
(AFTERTRUEFALSE11)
@SP
A=M
M=D
@SP
M=M+1
//push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
//gt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE12
D;JGT
D=0
@AFTERTRUEFALSE13
0;JMP
(REGTRUE12)
D=-1
(AFTERTRUEFALSE13)
@SP
A=M
M=D
@SP
M=M+1
//push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
//gt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE14
D;JGT
D=0
@AFTERTRUEFALSE15
0;JMP
(REGTRUE14)
D=-1
(AFTERTRUEFALSE15)
@SP
A=M
M=D
@SP
M=M+1
//push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
//gt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@REGTRUE16
D;JGT
D=0
@AFTERTRUEFALSE17
0;JMP
(REGTRUE16)
D=-1
(AFTERTRUEFALSE17)
@SP
A=M
M=D
@SP
M=M+1
//push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
//push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
//add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=D+M
@SP
A=M
M=D
@SP
M=M+1
//push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
//sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@SP
A=M
M=D
@SP
M=M+1
//neg
@SP
M=M-1
A=M
D=-M
@SP
A=M
M=D
@SP
M=M+1
//and
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=D&M
@SP
A=M
M=D
@SP
M=M+1
//push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
//or
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=D|M
@SP
A=M
M=D
@SP
M=M+1
//not
@SP
M=M-1
A=M
D=!M
@SP
A=M
M=D
@SP
M=M+1
