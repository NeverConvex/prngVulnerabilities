# openssl is the package that provides purportedly secure PRNG used below
# any available CRAN mirror is fine; this is just an example:
install.packages('openssl', repos='https://cran.us.r-project.org')
library(openssl)    # needed for secure PRNG

# distr is a standard R library including a laplace implementation (*not* secure)
install.packages('distr', repos='https://cran.us.r-project.org')
library(distr)      # does not use secure PRNG. Just included for comparison

openSslLaplace <- function(scale, length) # use to generate centered laplace RVs with secure openSSL PRNG
{
    uniformRNs = rand_num(n=length) # rand_num is the at least purportedly secure OpenSSL uniform RV generator on (0,1)
    laplaceRNs = sign(uniformRNs - 0.5) * scale * log(1. - 2. * abs(uniformRNs - 0.5)) # inverse CDF transform (with a small trick): uniform -> laplace
                                                                                       # (see p. 652 of https://crysp.uwaterloo.ca/courses/pet/F18/cache/Mironov.pdf)
    return(laplaceRNs)
}

# Example invocation
privacyLossBudget = 0.1  #
querySensitivity = 1    # Calculated from structure of tabulations/counts/queries desired to publish, & whether bounded/unbounded DP
openSslLaplaceRVs = openSslLaplace(scale=querySensitivity/privacyLossBudget, length=10000)
insecureLaplaceRVs = r(DExp(rate=privacyLossBudget/querySensitivity))(10000) # distr uses rate parameter (reciprocal of scale parameter)

# Side-by-side plots to check that centered (mean=0) laplace distribution looks right
X11()
old.par <- par(mfrow=c(1, 2))
h1 <- hist(openSslLaplaceRVs, breaks=100, plot=FALSE) # openSSL laplace RVs, using secure PRNG
h1$counts = h1$counts/sum(h1$counts)
plot(h1)

h2 <- hist(insecureLaplaceRVs, breaks=100, plot=FALSE) # distr laplace RVs, using insecure PRNG
h2$counts = h2$counts/sum(h2$counts)
plot(h2)

par(old.par)
message("Press Return To Continue")
invisible(readLines("stdin", n=1))
