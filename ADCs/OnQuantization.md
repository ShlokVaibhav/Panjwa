# On Quantization Noise

I’ve been reading Marcel Pelgrom’s insightful monograph “Analog to Digital Conversion” and loved his treatment of quantization error and various mental tricks to simplify it. I have not produced any of his tables or figures but given page details for reader to locate them exactly.

I will comment on

1. Commutation of quantization and sampling (Novel idea)
2. Autocorrelation of Quantization error (Pelgrom's First assumption)
3. PSD of quantization error (Pelgrom's Second assumption)
4. Robustness (Future work)

## 1. Commutation of Quantization and Sampling operators 

(I'm using the term operator and not the term operation)


On page 428, he remarks while the mainstream ADCs are sample-and-hold first and then quantize, the opposite architecture, ie, level-crossing converters that quantize continuously in time are also in existence.

This seems trivially true the way sample-and-hold operation is described in textbooks - literally freeze the signal till comparison, the freezeing itself is quantization to some analog level. However, it will be interesting to see the limitations of this equivalence in cutting-edge GSps ADCs, a topic for a later article!

For now, we just keep this property in mind.

## 2. Quantization error as Noise

I think this is the single most interesting and unique aspect of ADCs, there's a new creature discovered - the quantization error - but it is not the signal, even though it decends from it, it is not quite noise either though it looks like it at times. So now the engineer must also wield taxonomy! 

Let us look at some characteristics of quantization error first

### 2a. Autocorrelation 

On page 431, Pelgrom is clearly in a mood of following pedagogy of thermodynamics (which he cites later) and stats mech (Which is not doing exactly great these days!)

The first assumption is to assume the autocorrelation of quantization creature is a dirac-delta in time. However, he misses to remark that while the thermal noise is also ergodic which allows a single realization of it to have the desired autocorrelation, quantization error is clearly not:

I can always create a particular input signal to realize any correlation function for one particular quantization trajectory. And i think this is why standards like IEEE 1241-2023 stick to few classes of signals for characterizing commercial ADCs, which often requires the end-user to do his own characterization based on his class of input signals (No one created a standard to measure thermal noise simply because you cannot shape its autocorrelation)

I would request Pelgrom to add another row on ergodicity to table 9.1


### A small question
I also have a question for the reader - usually we put anti-aliasing filters before ADCs or even the circuitry-limited inherent low-pass filtering ($kT/C$), does a thermal noise realization that is effectively being integrated by an RC filter, still memoryless and dirac-delta correlated??

### 2b. PSD

The quantization error can be written in closed form as [The intermodulation and distortion due to quantization of sinusoids
](https://ieeexplore.ieee.org/document/1164729):

$$Q(t) = \frac{1}{2}-\sum_{n=1}^{\infty} \frac{1}{n\pi} \sin(2n\pi x(t))$$

(This is simply the fourier expansion of sawtooth as noted on the wiki page for ceiling and floor function)

Note that while $x(t)$ may be band-limited to nyquist frequency, as the above equation shows, quantization error is clearly not because of non-linear sinusoidals being added (Infact, for the 1-bit case discussed in exact in Pelgrom's book shows the higher harmonics appearing clearly)

So how do we then comment on PSD? 

After sampling, clearly the higher nyquist zones of $Q(t)$ will fold into the first and we know that the autocorrelation was assumed to be a dirac-delta so in frequency domain, so $Q(f)= c$,  some constant even after folding.

Now how do we estimate this constant $c$?  Note that **quantization error cannot have more energy than the signal**, so $c$ is a finite constant and since quantization error can be conceived as a sum of pulses of width $T_s$ multiplied a level-modulated signal (analogous to how the effect of sample-and-hold is analyzed):

$$Q(t) = \sum_{n=-\infty}^{n=\infty} (x(t)-x(nT_s))[u(t-nT_s)-u(t-(n-1)T_s)]$$

(Here $u(t)$ is the step function)
 In frequency domain, that's sum of a series of convolutions of sinc  with a band-limited signals, at any rate, since sinc pulse bandwidth is first few nyquist zones, each quantization noise realization is going to be actually band-limited, despite the zero-correlation assumption made. 

### Thermal noise relegated down to quantization error
 What was the point of this detour in last 2 paragraphs?

 It was to show the equivalence of quantization noise with the thermal noise that passes through an external or even the circuitry-limited internal low-pass filtering ($kT/C$), both have effectively a PSD that dies off in few nyquist zones and neither has a correlation that is dirac-delta anymore. (Though thermal noise is still ergodic)


 ### Quantization PSD from time domain

 Since frequency-domain didn't answer our query of determining $c$, let us try to work in time-domain, and look at the bold-highlight above, we know that quantization noise lies in $[-A_{LSB}/2, A_{LSB}/2]$ always and takes some distribution.

 We invoke the poor-man's hypothesis, or what Pelgorm calls his second assumption - 

 **Equal a priori probability**

 In absence of any reason to assume otherwise, $Q(t)$ takes a uniform distribution over $[-A_{LSB}/2, A_{LSB}/2]$
This duly gives :

$$c = \frac{A_{LSB}^2}{12f_s}$$

 (Note that as in statistical mechanics, this assumption is totally natural when averaged over all possible realizations but for a single realization which mixed-signals must deal with, often without the macroscopic helping hand, it's unsatisfying)


 ## 3. Robustness

This is the most beautiful move by Pelgrom, which separates the master from the reader: 
> This assumption does not take any specific
signal properties into account, neither will the result be sensitive to small changes
in the properties of the signal.


This is the landmark field of "Robust Statistics" (Refer to the book by Huber and Ronchetti), yes i assumed a uniform distribution but experience shows this is a very robust estimator and even if you were to work out an exact theory, answers won't change much. 
As empiricist this statement is, he demonstrates it in table 9.2 by producing the simualated vs estimated SQNR for a corner case.


There is also another guardrail put by Pelgromm, he shows us how to analyze things when signal really becomes too rebellious - a pure sine wave touching the rails as well as when number of bits are too low - 1. 

This exact analysis coupled with the generic basket that catches everything else, I felt very well-equipped to deal with any signal that shows up at my ADC!







