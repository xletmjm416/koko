# Welcome to Koko Model Toolkit & extensions version 0 (draft)

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
- [x] pickles model output and saves it together with parameters
- [ ] supports cloud computing
- [x] is thoroughly unit tested and documented

Note that throughout documentation:

- empty tickbox [ ] means "feature planned",
- checked box [x] means "feature implemented",
- striketrough or striked box [-] means "feature formerly planned, but now abandoned."

Koko was built as a personal project by Mikolaj Metelski under MIT License.
Feel free to build your extensions on top of Koko. This is what it's for - on its own, it does nothing.

## Theoretical foundation

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
There is a function that does exactly this, but a bit more elegantly on the inside: (and [ ] in parallel on multiple grid points)

```
koko.analytics.run_model_on_param_grid(Model, data, param1=[0.1, 0.2, 0.3], param2=[True, False])
```

Results of the analysis will be [ ] saved in an HDF store.

## Terminology

- model class = a class inheriting from AbstractModel
- model object = instance of model class
- model input =  an object passed to model object's `__call__`
- model input arguments = labels of model objects's `__call__` arguments
- model output = an object returned from model object's `__call__`
- parameter = attribute of model object
- parameter input = collectively: objects passed to model object's `__init__`
- parameter output = undefined (makes no sense, really) # a model object created by instatiating model class with a given parameter input
- input arguments = labels of model object's `__call__` arguments
- parameter arguments = labels of model objects's `__init__` arguments
- parameter label = label (variable name) of model object's parameter
- (supermodel's) submodel = a model object (A) that is another model object's (B's) parameter. B is referred to as supermodel of A.
- (submodel's) supermodel = a model object (A) whose one of parameters is a model object (B). B is referred to as submodel of A.
- model tree = a tree diagram of model substructure whose leaves are parameters that are not model objects.
- run calibrator = a model object (A) whose model inputs are a model object (B) and fixed B's model input and whose (A's) model output is a dictionary whose keys are B's parameter arguments.
- init calibrator = a model object (A) whose parameter input is something that would ordinarily be considered another model object (B's) model input
init calibrator's parameter input is what would ordinarily be another model object (B's) model input.
- assumption = a model object (A) whose model input is another model object (B) together with its (B's) model input, and its (A's) model output is a boolean (True/False).
- model instantiation / creation = a shorthand name for instantiating a model class
- model run = a shorthand name for calling model object's `__call__`
- calibration = a general term encompassing init calibration and run calibration
- reparametrisation = a general term meaning replacement of the parameters inside model object and propagating those changes to submodels. it also encompasses replacement of submodels

## Model objects

Model object is an instance of any model class. You can make any Python callable a model class by wrapping it with `"kokomodel` for easy onboarding. This will convert positional arguments of the callable into model input arguments and keyword arguments into parameter arguments. Model objects are instantiated by passing parameter input to model class's `__call__` (meaning as arguments to the model object's `__init__`).
Once you have a model model class or a model object, you can run all sorts of analysis with them, using the methods inherited from `AbstractModel` or provided by `koko.analytics`. You can set other model objects as parameters or replace submodels wherever you want to create complex model dependency trees. `koko` will take care of parallelizing the computation, assessing your models' performance, profiling, saving model outputs for reuse, calibration and assumption verification.

## Calibrators

Both init calibrators and run calibrators are model objects of the Calibrator class, but they are a bit different conceptually so it is worth distinguishing between the two. Their behaviour differs depending on whether calibrator is a static attribute of a model class (init calibrator) or a parameter of a model object (run calibrator).

### Run calibrator

Run calibrator is a model object (A) whose model inputs are a model object (B) and B's model input and whose (A's) model output is a dictionary whose keys are B's parameter labels. When a model object (A) has some run calibrators as its parameters (i.e. A's submodel that is a calibrator), they will be discovered and all called (ordered alphabetically) in A's `__call__`. After that, A's wil call `reparam` with the calibrator's output. The run calibrators will be passed the model object (self) as first argument and model input as the other argument. It is bad pracice to rely on run calibrators' order; run calibrators should be independent of each other by design. (TODO: decide? You may or may not want to adjust model object's parameters with calibrator's output; if you do, just pass it to model object's reparam with `init_calibration=False`)
Use case:
You want some parameters to be adjusted (or added to the model) just prior to the run of model object's `__call__`, but they cannot be determined solely from parameter input are require model input to be known.

### Init calibrator

Init calibrator is a model object (A) whose parameter input is something that would ordinarily be considered another model object (B's) model input. A's model output is a dictionary whose keys are B's parameter labels. When a model class (presumably the class of B) has an init calibrator A as one of its attributes, it (A) will be discovered and called in model class's `__init__` during model object instantiation. A will be passed parameter input of B as model input. If there are more than one init calibrators, they will be called alphabetically. It is bad practice to rely on init calibrators' order; init calibrators should be independent of each other by design. You may or may not want to adjust model object's parameters with calibrator's output; if you do, just pass it to model's reparam with `init_calibration=False`.
Use case:
You want some parameters to be calculated given a fixed model input. Instead of writing this in `__init__` manually by passing the "expected" model input as parameter input, create an init calibrator and register it by making it a class attribute.
WARNING: Watch out for the memory size of init calibrators. Since their parameter input is another model object's model input, they can get very large, if you save their parameter input as parameter. The parameter will be stored in runtime memory and impact performance. Consider keeping a path to a file or some other pointer to the fixed model input data as a parameter if your dataset is large.

## Assumptions

Assumption is a model object that is similar to a run calibrator in that it accepts a model object and its model input. Assumptions have a different return, though: they can only return True or False.
Assumptions that are parameters of a model object are called before AND after run calibrators in model object's `__call__`. It is bad pracice to rely on run assumptions' verification order; assumptions should be independent of each other by design.
Assumptions' role is first to verify that the input to the model is okay and to confirm that run calibrators have not broken any assumptions of the model. Whenever an Assumption model object returns False inside a model object's (A's) `__call__`, the supermodel (A) will raise `AssertionError`.

## Conceptual exercises

- What is an assumption on a run calibrator? What is a run calibrator on an assumption?
- Can one make an init calibrator of a run calibrator or vice versa?
- Should there be run assumptions and init assumptions, like there are two types of calibrators? Why? Why not? What would that mean?
- Should assumptions be called before or after an init calibrator?
- Can there be a non-assumption submodel of an assumption? What could that be used for?
- Init calibrator on an assumption can generate assumption models that depend on some fixed observations. How could one use that?
- Will assumptions and calibrators show up in their supermodel's model tree?
- Why aren't assumptions and calibrators kept in a list to keep their execution order?
- Would that make a difference if the calibrators knew each other's exectution order? (Consider two calibrators. If one depends on the other's output, perhaps one should be another's submodel?)

## Notes

### Passing model object vs model class as parameter input

In typical use cases, if you want to make a supermodel of a model object you own, you should the existing model object as parameter input/parameter, not its model class.
If you pass a model class as parameter input, strongly consider to create an instance of this class
and store it as parameter. Only then it will appear in model tree and will take part in reparam, calibration, parallelisation, submodel storage etc. On the other hand,
using a model class as parameter input may be used to instantiate a custom version of a model object that depends on the data, the rest of parameters or init calibrators' outcomes inside model object's `__call__`. Typically such a task can be accomplished by writing an appropriate run calibrator instead.

### Propagate reparametrisation to all leaves of the model tree

Example:  `modelobject.reparam(a=5, b=8, ...)`

The expected behaviour of `model.param = 5` is to set the parameter only for `model`. The parameter may or may not already exist before assignment.
`reparam` instead replaces the parameter for all submodels recursively inside the parameter tree. If the leaf is an object (but not a model object), `neither` its `__set__` nor `__setattr__` will be called but the object replaced altogether.
Notice that reparam can replace more than one occurence of a parameter, is the submodel's parameters have the same labels. This is especially important if model objects of the same model class occur in the model tree. If you want to reparam only for a submodel, traverse the model tree and call reparam on the submodel instead.

## Toy model for examples explanation

Newtonian gravity is a simple model.
$$F = G \frac{m_1 m_2}{r^2}$$
Newtonian gravity is a one parameter model: G is the ony free parameter. It takes as input two charges and output the magnitude of force between them.

## Koko design guidelines

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
