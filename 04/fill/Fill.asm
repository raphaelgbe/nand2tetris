// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.


// SOME CONSIDERATIONS ON HOW TO MAINTAIN STATE ABOUT SCREEN STATUS
//NOTE: screenIsBlack ? its more time-efficient to use a register to keep this info (and only one register less memory efficient than checking beginning and end of screen memory map) ; however sudden interruption of program could mess with its value
//NOTE: however, no-toggle-variable solution(checking start & end) doesn't explicitly encode this logic (and relies on a side-effect: that all registers in between start and end are same colour if they are ; though if they aren't, what do we do?)
//NOTE: However it seems reasonable that if first register is -1, then the INTENDED status of screen is black, so it should be considered as such. But updating the toggle var in the end allows to update about completion ; though once again, blocked if process started but didn't complete
//@screenIsBlack // when M=0, screen is white, when M=1, it is black
//M=0


// initialization
@SCREEN
D=A
@iter // iterator variable which addresses screen location, used to go through the whole screen
M=D
// following lines: determine address corresponding to the end of the screen in the memory map
@8192 // the end is 256 (lines) * 32 (16bits registers making up each row, ie 512=32*16 columns) = 8192
D=A
@iter
D=D+M
@iterend
M=D

(LOOP)
	//reinit iter variable
	@SCREEN
	D=A
	@iter
	M=D

	//Start listening to the keyboard and go to whiten / blacken if it's resp. inactive / active
	@KBD
	D=M
	@KEYISPRESSED
	D;JNE
	@KEYISNOTPRESSED
	D;JEQ
	@LOOP
	0;JMP

(KEYISPRESSED)
	//@iterend // check if screen is black
	//D=M
	//@LOOP
	//D;JNE // screen is indeed already black => go back to loop

	// check if screen is black by checking first register in screen memory map:
	@SCREEN
	D=M
	@LOOP
	D+1;JEQ // if M=-1 at SCREEN, the screen is already black => go back to listen the keyboard

	// We know screen is white : we will fill it with black lines
	(BLACKENLOOP)
		// check if end of loop
		@iter
		D=M
		@iterend
		D=D-M
		@LOOP
		D;JGE

		// blacken the current line
		@iter
		A=M
		M=-1

		// increment register to blacken address
		@iter
		M=M+1

		// close the loop : go back to its beginning
		@BLACKENLOOP
		0;JMP

(KEYISNOTPRESSED)
	//@screenIsBlack
	//D=M
	//@LOOP
	//D;JEQ // screenIsBlack == 0 so screen is in fact already white => go back to loop

	// check if screen is white by checking first register in screen memory map:
	@SCREEN
	D=M
	@LOOP
	D;JEQ // if M=0 at SCREEN, the screen is already white => go back to listen the keyboard

	// We know screen is black : we will fill it with white lines
	(WHITENLOOP)
		// check if end of loop
		@iter
		D=M
		@iterend
		D=D-M
		@LOOP
		D;JGE

		// whiten the current line
		@iter
		A=M
		M=0

		// increment register to blacken address
		@iter
		M=M+1

		// close the loop : go back to its beginning
		@WHITENLOOP
		0;JMP