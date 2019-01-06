mersenneTwisterStateAttack.py illustrates the following kinds of attacks on the MersenneTwister algorithm:

        invertTwister_Example:

        invertTwister_Example adapts James Roper's example from his Sept 22, 2010 blog post on attacking the MersenneTwister PRNG:

            https://jazzy.id.au/2010/09/22/cracking_random_number_generators_part_3.html

        (such attacks have long been known, but James' explanation is particularly accessible)

        The ``big idea'' can be explained very quickly: consider lines 223 - 252 in
        
            https://github.com/numpy/numpy/blob/master/numpy/random/mtrand/randomkit.c

            (an implementation of MersenneTwister in numpy's source)

        Lines 227 - 242 look complex, but their details can be ignored: they reset the STATE.KEY vector of currently available random numbers
        every time a ``fresh'' sequence of 624 random iterate draws has completed. For our purposes, the only importance of these lines is
        that they can be thought of as a deterministic fxn, f(STATE.KEY) -> STATE.KEY, and that they are dormant until every 624th consecutive
        random number is drawn.

        Most of the time, f is not invoked, and MT simply returns g(STATE.KEY[STATE.POS+1]), incrementing STATE.POS in the process, where g
        is a fxn g(STATE.KEY[i]) -> uint32. g is implemented entirely by lines 246 - 249, and so if we can invert these operations, we ``win,''
        i.e., we can take an output uint32 RV from the MT PRNG and convert it back into the state value STATE.KEY[i] that generated it. Once
        we've done this 2*624 times, then we necessarily have captured the PRNG's complete state, and we can re-implement lines 227 - 242
        to perfectly predict the future behavior of the PRNG.

        Each of lines 246 - 249 represents an invertible operation, so this is achievable, as this fxn illustrates.

            (See other fxns for practical extensions of this idea, focused on attacking noise infusion systems, and specifically
             on attacking naively implemented differentially private mechanisms.)

