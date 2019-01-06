import numpy

def toInt(bitArray):
    bitArray = numpy.array([numpy.uint32(b) for b in bitArray]) # Re-cast in case we received an array of str 0/1's
    return numpy.uint32(bitArray.dot(2**numpy.arange(bitArray.size)[::-1]))

def xor(b1, b2):
    if b1 + b2 == 1:
        return numpy.uint32(1)
    return numpy.uint32(0)

def goFish(i, binaryVector, magicNumber, leftShift):
        if magicNumber[i] == 1:
            return xor(goFish(i + leftShift, binaryVector, magicNumber, leftShift), binaryVector[i])
        return binaryVector[i]

def invertLeftShiftThenMagicMaskThenXOR(value, leftShift, magicNumber):
    """
        Given value as numpy.uint32 and assuming

            value = intit32 XOR ( (init32 << leftShift) & magicNumber )

        this fxn solves for init32. MersenneTwister uses:

            - leftShift of 7 and 15 in its 2nd and 3rd tempering ops
            - magicNumber of 0x9d2c5680 = 1001 1101 0010 1100 0101 0110 1000 0000 in its 2nd tempering op
            - magicNumber of 0xefc60000 = 1110 1111 1100 0110 0000 0000 0000 0000 in its 3rd tempering op

            Works because:

            [A] right-most leftShift bits are 0, so & magicNumber leaves these as 0, & XOR means right-most leftShift bits are correct
            
            [B] left-most (32 - leftShift) bits are determined by:

                    if 1, this means (init32[i + leftShift] & mN[i]) XOR init32[i] -> final[i]

                        => (1) where mN[i] = 0, final[i] = init32[i]                           (are correct, 'invert' by doing nothing)

                        => (2) where mN[i] = 1, final[i] = init32[i + leftShift] XOR init32[i] (invert by XOR with init32[i + leftShift])

                        This requires init32[i + leftShift] for i=0,..,32-leftShift. We have these when mN[i + leftShift] = 0; o.w.,
                        we compute them recursively using (2) (until we end up in case (1) ).

         1001 1100 0010 << 5 
                =
         1000 0100 0000

    """
    initBinary = [numpy.uint32(b) for b in numpy.binary_repr(value)]
    initBinary = [numpy.uint32(0)] * (32 - len(initBinary)) + initBinary
    invertedValue = [numpy.uint32(b) for b in initBinary]
    magicNumber = [numpy.uint32(b) for b in numpy.binary_repr(magicNumber)]

    print("--->")
    print(initBinary, len(initBinary))
    print(invertedValue, len(invertedValue))
    print(magicNumber, len(magicNumber))

    for i in range(32 - leftShift):
        if magicNumber[i] == 1:
            #invertedValue[i] = numpy.bitwise_xor(initBinary[i + leftShift], initBinary[i])
            invertedValue[i] = goFish(i, initBinary, magicNumber, leftShift)

    print("invertedValue being returned as: ")
    print(invertedValue)

    return toInt(invertedValue)

def invertRightShiftThenXOR(value, rightShift):
    """
        Given value as numpy.uint32 and assuming

            value = init32 XOR (init32 >>> rightShift)

        this fxn solves for init32. MersenneTwister uses:
        
            - rightShift of 11 and 18 in its 1st and 4th tempering ops
    """
    initLeftBinary = numpy.binary_repr(toInt(numpy.array([numpy.uint32(b) for b in numpy.binary_repr(value)[:rightShift]])))
    initRightBits = toInt(numpy.array([numpy.uint32(b) for b in numpy.binary_repr(value)[rightShift:]]))
    initLeftBits = toInt(initLeftBinary[:32-rightShift])
    trueEndBits = numpy.bitwise_xor(initLeftBits, initRightBits)
    return trueEndBits

def attackGeometricMechanism_Example():
    """
        This fxn extends the ideas in invertTwisterExample to attack the most obvious real-world implementation of the Geometric Mechanism
        in numpy.
    """

def attackPostProcessedLaplaceMechanism_Example():
    """
        This fxn extends the ideas in attackLaplaceMechanism to attack a raesonable real-world implementation of the Laplace Mechanism
        output of which has been postprocessed by an optimizer to maintain known invariants.
    """

def attackLaplaceMechanism_Example():
    """
        This fxn extends the ideas in invertTwisterExample to attack the most obvious real-world implementation of the Laplace Mechanism
        in numpy.
    """

def invertTwister_Example():
    """
        This fxn is an adaptation of James Roper's example from his Sept 22, 2010 blog post:

            https://jazzy.id.au/2010/09/22/cracking_random_number_generators_part_3.html

        (such attacks have long been known, but James' explanation is particularly accessible)
    """
    initBinary = numpy.array([numpy.uint32(b) for b in '10110111010111100111111001110010'])
    print(f"Initial binary value, as an array of 0/1 int's: {initBinary}")

    init32 = numpy.uint32(toInt(initBinary))
    print(f"Initial binary value, converted to uint32: {init32}")

    print(f"Note that numpy.binary_repr({init32}): {numpy.binary_repr(init32)}")

    print("Attacking MersenneTwister requires inverting combined bitwise XORs, shifts, & masks.")
    print("(Though it is tempting to try to separately invert these, each operation considered alone is not invertible.")

    print("\n\nConsider an example XOR(rightShift):")
    rightShifted18 = numpy.right_shift(init32, 18)
    print(f"In binary, {init32} >>> 18: {numpy.binary_repr(rightShifted18)}")
    rightShiftedThenXORd = numpy.bitwise_xor(init32, rightShifted18)
    print(f"And {init32} XOR {rightShifted18}: {numpy.binary_repr(rightShiftedThenXORd)}")
    trueEnd14 = invertRightShiftThenXOR(rightShiftedThenXORd, rightShift=18)
    print(f"Inversion attack believes original final 14 bits were: {numpy.binary_repr(trueEnd14)}")

    print("\n\nNow consider an example XOR(mask(leftShift)):")
    print(f"Let the initial value, as before, be: {numpy.binary_repr(init32)}")
    leftShifted7 = numpy.left_shift(init32, 7)
    print(f"We have numpy.binary_repr(init32) << 7: {numpy.binary_repr(leftShifted7)}")
    leftShiftedThenMagicMasked = numpy.bitwise_and(leftShifted7, 2636928640)
    print(f"We now apply mask 0x9d2c5680, or, in binary: 1001 1101 0010 1100 0101 0110 1000 0000")
    print(f"({numpy.binary_repr(init32)} << 7) & 0x9d2c5680: {numpy.binary_repr(leftShiftedThenMagicMasked)}")
    leftShiftedThenMagicMaskedThenXORd = numpy.bitwise_xor(init32, leftShiftedThenMagicMasked)
    print(f"Next, {numpy.binary_repr(init32)} XOR (({numpy.binary_repr(init32)} << 7) & 0x9d2c5680): {numpy.binary_repr(leftShiftedThenMagicMaskedThenXORd)}")
    invertedValue = invertLeftShiftThenMagicMaskThenXOR(leftShiftedThenMagicMaskedThenXORd, leftShift=7, magicNumber=numpy.uint32(2636928640))
    print(f"Inversion attack believes original binary value was: {numpy.binary_repr(invertedValue)}")

    #invertedAsBinary = ['0']*(32-len(numpy.binary_repr(invertedValue))) + [b for b in numpy.binary_repr(invertedValue)]
    #final = ['0']*(32-len(numpy.binary_repr(invertedValue))) + [b for b in numpy.binary_repr(leftShiftedThenMagicMaskedThenXORd)]
    #print("True Guess Magic Shift7 Final Final[i+7]:")
    #print([b for b in numpy.binary_repr(init32)])
    #print(invertedAsBinary)
    #print([b for b in numpy.binary_repr(numpy.uint32(2636928640))])
    #print([b for b in numpy.binary_repr(leftShifted7)[7:]])
    #print(final)
    #print([final[i+7] for i in range(32-7)])

def main():
    invertTwister_Example()                         # Illustrates attack on numpy MersenneTwister w/ direct access to PRNG output
    attackLaplaceMechanism_Example()                # Illustrates attack on numpy MersenneTwister w/ access to Laplace Mechanism outputs
    attackPostProcessedLaplaceMechanism_Example()   # Illustrates attack on numpy MersenneTwister w/ access to invariant-postprocessed Laplace Mechanism outputs
    attackGeometricMechanism_Example()              # Illustrates attack on numpy MersenneTwister w/ access to Geometric Mechanism outputs

if __name__ == "__main__":
    main()
