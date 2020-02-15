Welcome to Koko Model Toolkit & extensions version 0 (draft)
=====================

Koko Model Toolkit is a minimal, powerful and abstract object-oriented toolkit for implementation and analysis of mathematical models.

Koko is not bound to a specific model implementation, and as such, Koko is useless on its own. It would be best described as a meta-model: a model of how models are handled. The idea is to give Koko the mathematical specification of a model, calibration and analysis to be done, and it will handle the rest. A model can be put into Koko's framework by creating a class and making it implement a relevant interface. One of the biggest advantages of Koko is the fact that Koko models can use other Koko models as parameters and those dependencies can be replaced for analytics.

Koko:
- [x] runs arbitrary models on arbitrary data
- [x] calibrates arbitrary model params (minimisation with arbitrary targets)
- [ ] calibrates arbitrary model params (with root solving)
- [x] propagates reparametrisation of the model to the dependent models
- [ ] resolves ambiguity in reparametrisation when multiple dependent models have the same parameter name
- [x] handles passing the dependent's parameter to the independent's call
- [ ] validates model assumptions that depend on:
	- [ ] model parameters
	- [ ] data
	- [ ] calibration output
- [ ] provides extremely easy analytics and automatic model parameter change impact reports, in particular:
	- [x] runs models on parameter grids using same data
	- [ ] evaluates model performance in terms of time taken for computation
	- [ ] calculates pairwise parameters' change impacts (e.g. impact of changing from one set of parameters to the next)
	- [ ] calculates pairwise parameters' change impacts on a parameter grid (all combinations of given parameter sets)
- [ ] eases out the onboarding of your current model implementations into Koko by providing:
	- [ ] function decorators that create a relevant model class
- [ ] handles analysis of models on large datasets through an HDF5 store
- [ ] supports cloud computing
- [x] is thoroughly unit tested and documented

Note that throughout documentation:
- empty tickbox [ ] means "feature planned",
- checked box [x] means "feature implemented",
- striketrough or striked box [-] means "feature formerly planned, but now abandoned."

Koko was built as a personal project by Mikolaj Metelski under MIT License.
Feel free to build your extensions on top of Koko. This is what it's for - on its own, it does nothing.

Theoretical foundation
======================

Typically one mathematically treats a model as a function of input data $x$, given parameters $p$:
$$y = f(x; p)$$
and it outputs $y$. Note there is a clear distiction between model *input*, 
which is usually a result of an experiment, market data, output from a random number generator or 
some other type of independent observation, whereas model *parameters*, once calibrated, are the fixed for any data inputted.
Calibration is, in general, a procedure that finds parameters that best match the observed data.
We can therefore consider models of fixed parameters to be functions of data only. 
The models themselves are outputs of model factories, which must be passed given parameters:
$$model = factory(p)$$
$$y = model(x)$$
We can write $f(x; p) = factory(p)(x)$.
This conceptual framework is very powerful, when we, for example, allow model parameters to be other models:
$$M = some_model_factory(real parameter)$$
$$M' = some_other_model_factory(M)$$
$$y = M'(data)$$
This is exactly how this toolkit works.

Koko treats models as objects of classes inheriting from base AbstractModel class:
```
class Model(AbstractModel):
    def __init__(**parameters):
        ... # your model factory implementation here
    def __call__(*data):
        ... # your model running
```
Every object of class inheriting from AbstractModel it must implement `__call__`.
Parameters are arguments of the Model object, whereas data are arguments with which model object can be called:
```
model = AbstractModel(parameters)
output = model(data) # will raise NotImplementedError as Model is an abstract class (in OOP sense)
```

In such a manner, running the model under different parameters is very simple:
```
params1 = [0.1, 0.2, 0.3]
params2 = [-1, 0, 1]
params3 = [False, True]
params4 = [another_model1, another_model2]
for params in itertools.product(params1, params2, params3, params4):
	model = Model(parameters)
	output = model(data)
```
will run the model on each point of the parameters grid.
There is a function that does exactly this, but a bit more elegantly on the inside: (and [ ] asynchronously on mutiple grid points)
```
koko.analytics.run_model_on_param_grid(Model, data, param1=[0.1, 0.2, 0.3], param2=[True, False])
```
Results of the analysis will be [ ] saved in an HDF store.

Toy model for examples explanation
==================================
Newtonian gravity is a simple model.
$$F = G \frac{m_1 m_2}{r^2}$$
Newtonian gravity is a one parameter model: G is the ony free parameter. It takes as input two charges and output the magnitude of force between them.

Koko design guidelines
======================

Koko's modules are as follows:
- [x] `core` handles the abstract notions of the models, but it is not related to any model in and of itself.
Once a model is implemented using Koko's base AbstractModel class, a wide array of analytics can be done with very few function calls.
- [x] `analytics` proves functions to provide common analysis tasks, such as calibration and model running.
- [ ] `assumption` provides decorators and base models for assumption verification.
- [ ] `calibrate` helps in constructing you calibration workflows.

Koko naming conventions:
- Name classes inheriting from Model *Model, e.g. RadioactiveDecayModel, LeastSquaresModel, MyMachineLearningModel, CoulombModel

The general conding guidelines are as follows:
- favour OOP over procedural programming
- favour pure functions over impure (in functional sense)
- favour iterators
- favour generic variables over constants
- never repeat same code twice
- prove algorithm termination where possible (avoid missing elses/elifs)
- raise meaningful exceptions when necessary. never catch-to-print
- always use Google documentation standards (Sphinx-Napoleon generates the docs)
- favour small datasets stored on disk than large datasets stored in memory
- use a logger
- favour threading where possible
- favour Python builtins over libraries
- use simple versioning: 0, 1, 2, 3...
- enforce PEP style guidelines (use linter)
- always use type hints
- use generic typing in type hints when appropriate
